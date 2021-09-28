#!/bin/python
"""
registers local dynamic IP in route53 zone
"""
import logging
import boto3
import botocore
from botocore.config import Config
from botocore.exceptions import BotoCoreError
import netifaces
import argparse


class Route53ChangeBatch:
    def __init__(self):
        Name = ''
        Type = ''
        TTL = ''
        ResourceRecordSet = dict()
        ResourceRecords = []
        # {
        #     "Comment":"Updated From DDNS Shell Script",
        #     "Changes":[
        #             {
        #               "Action":"UPSERT",
        #               "ResourceRecordSet":{
        #                 "ResourceRecords":[
        #                   {
        #                     "Value":"$IP"
        #                   }
        #                 ],
        #                 "Name":"$NAME",
        #                 "Type":"$TYPE",
        #                 "TTL":"$TTL"
        #               }
        #             }
        #           ]
        #         }


def list_local_interfaces():
    """
    lists local interfaces with their addresses
    :return: dict; {interface, addresses}
    """
    result = dict()

    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        result.update({interface: addresses})

    return result


def get_local_ip(interface_name):
    """
    This function accepts the name of a local interface and returns the last IP address associated with it.
    :interface: str;
    :return: str; the IP address of the local interface
    """
    result = None

    try:
        addresses = netifaces.ifaddresses(interface_name)
        ipv4 = addresses[netifaces.AF_INET]
        for link in ipv4:
            result = link['addr']
    except Exception as e:
        print('interface not found.  Try one of these: \r\n' + str(list_local_interfaces()))

    return result


def get_aws_session(aws_access_key_id=None, aws_secret_access_key=None):
    """
    Creates AWS session; uses passed-in credentials first; then uses environment variables
    :param aws_access_key_id: if None, boto3 credential look-up mechanisms are used
    :param aws_secret_access_key: if None, boto3 credential look-up mechanisms are used
    :return: Session() object
    """
    result = None
    try:
        if aws_access_key_id is None and aws_secret_access_key is None:
            result = boto3.Session()
        else:
            result = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    except BotoCoreError as b:
        raise b

    return result


def get_route53_client(key=None, secret=None):
    result = None
    try:
        result = get_aws_session(aws_access_key_id=key, aws_secret_access_key=secret).client('route53')
    except BotoCoreError as b:
        raise b

    return result


def get_route53_record(zone_id, host, record_type, key=None, secret=None):
    result = None

    route53 = get_route53_client(key=key, secret=secret)
    record_sets = route53.list_resource_record_sets(HostedZoneId=zone_id)
    for record_set in record_sets['ResourceRecordSets']:
        if host in record_set['Name'] and record_set['Type'] == record_type:
            result = record_set

    return result


def update_route53_record(zone_id, host, record_type, new_ip, key=None, secret=None):
    result = None
    change_batch = {
        "Comment": "Updated from boto3",
        "Changes": [
                {
                  "Action": "UPSERT",
                  "ResourceRecordSet": {
                    "ResourceRecords": [
                      {
                        "Value": "{0}".format(new_ip)
                      }
                    ],
                    "Name": "{0}".format(host),
                    "Type": "{0}".format(record_type),
                    "TTL": 300
                  }
                }
              ]
            }
    try:
        route53 = get_route53_client(key=key, secret=secret)
        result = route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=change_batch)
    except BotoCoreError as b:
        # TODO: log something?
        raise b

    return result


def get_route53_ip(zone_id, host, record_type, key=None, secret=None):
    result = None
    try:
        record = get_route53_record(zone_id=zone_id, host=host.lower(), record_type=record_type, key=key, secret=secret)
        result = record['ResourceRecords'][0]['Value']
    except IndexError as i:
        print(i)

    return result


if __name__ == '__main__':
    # parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', type=str, help="enter the name of the local interface who's IP you wish to update")
    parser.add_argument('--list-interfaces', help='list the interface names that this program can use')
    parser.add_argument('--zone_id', type=str, help='the name of the route53-hosted zone to query/update')
    parser.add_argument('--host', type=str, help='the FQDN of the host record to query/update')
    parser.add_argument('--type', type=str, help='the type of record to update', default='A')
    parser.add_argument('--key', type=str, help='aws_access_key_id', default=None)
    parser.add_argument('--secret', type=str, help='aws_secret_access_key', default=None)
    args = parser.parse_args()

    # go
    local_ip = get_local_ip(args.interface)
    route53_ip = get_route53_ip(zone_id=args.zone_id, host=args.host, record_type=args.type, key=args.key, secret=args.secret)
    if local_ip != route53_ip:
        update_route53_record(zone_id=args.zone_id, host=args.host, record_type=args.type, new_ip=local_ip, key=args.key, secret=args.secret)
