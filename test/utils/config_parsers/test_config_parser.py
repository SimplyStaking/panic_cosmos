import unittest

from src.utils.config_parsers.config_parser import ConfigParser
from src.utils.exceptions import ConfigNotFoundException


class TestConfigParser(unittest.TestCase):

    def test_config_parser_throws_exception_if_file_does_not_exist(
            self) -> None:
        try:
            ConfigParser(['test/inexistent_file'])
            self.fail('Expected ConfigNotFoundException')
        except ConfigNotFoundException:
            pass

    def test_config_parser_throws_exception_if_at_least_one_file_does_not_exist(
            self) -> None:

        # Check that first file exists
        ConfigParser(['test/test_internal_config.ini'])

        # Now check inexistent file with file that exists
        try:
            ConfigParser(['test/test_internal_config.ini',
                          'test/inexistent_file'])
            self.fail('Expected ConfigNotFoundException')
        except ConfigNotFoundException:
            pass
