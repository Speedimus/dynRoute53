import unittest
import route53_update
import creds
import boto3
import logging
import props


class TestMain(unittest.TestCase):

    @classmethod    # before all
    def setUpClass(cls) -> None:
        pass

    @classmethod    # after all
    def tearDownClass(cls) -> None:
        pass

    @classmethod    # before each
    def setUp(cls) -> None:
        pass

    @classmethod    # after each
    def tearDown(cls) -> None:
        pass

    # tests
    def test_should_get_ip_for_local_interface(self):
        # setup
        interface = props.interface
        expected = props.expected_ip

        # execute
        actual = route53_update.get_local_ip(interface)

        # assert
        self.assertEqual(expected, actual)

    def test_should_list_local_interfaces(self):
        # setup
        expected = ''

        # execute
        actual = route53_update.list_local_interfaces()

        # assert
        self.assertIsNotNone(actual)

    def test_should_get_aws_session(self):
        # setup
        expected = ''

        try:
            # execute
            actual = route53_update.get_aws_session()

            # assert
            self.assertTrue(True, True)
        except Exception as e:
            self.assertFalse(True, True)

    def test_should_get_route53_client(self):
        # setup
        expected = ''

        try:
            # execute
            # boto3.set_stream_logger('botocore', level=logging.DEBUG)
            actual = route53_update.get_route53_client(key=creds.aws_access_key_id, secret=creds.aws_secret_access_key)

            # assert
            self.assertTrue(True, True)
        except Exception as e:
            self.assertFalse(True, True)

    def test_should_get_route53_record(self):
        # setup
        zone_id = props.zone_id
        host = props.host
        expected = props.expected_record

        # execute
        # boto3.set_stream_logger('botocore', level=logging.DEBUG)
        actual = route53_update.get_route53_record(zone_id=zone_id,
                                                   host=host,
                                                   record_type='A',
                                                   key=creds.aws_access_key_id,
                                                   secret=creds.aws_secret_access_key)

        # assert
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_route53_ip_with_upper(self):
        # setup
        zone_id = props.zone_id
        host = props.host
        expected = props.expected_ip

        # execute
        actual = route53_update.get_route53_ip(zone_id=zone_id, host=host, record_type='A')

        # assert
        self.assertEqual(expected, actual)

        # teardown

    def test_should_update_route53_record(self):
        # setup
        zone_id = props.zone_id
        host = props.host
        expected = props.expected_ip

        # execute
        route53_update.update_route53_record(zone_id=zone_id, host=host, record_type='A', new_ip=expected)
        actual = route53_update.get_route53_ip(zone_id=zone_id, host=host, record_type='A')

        # assert
        self.assertEqual(expected, actual)

        # teardown


if __name__ == '__main__':
    unittest.main()
