import unittest

from src.utils.config_parsers.user import UserConfig


class TestUserConfig(unittest.TestCase):

    def test_user_config_values_loaded_successfully(self) -> None:
        UserConfig('test/test_user_config_main.ini',
                   'test/test_user_config_nodes.ini',
                   'test/test_user_config_repos.ini')
