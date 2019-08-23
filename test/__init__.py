from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.user import UserConfig

TestInternalConf = InternalConfig(
    'test/test_internal_config.ini')
TestUserConf = UserConfig(
    'test/test_user_config_main.ini',
    'test/test_user_config_nodes.ini',
    'test/test_user_config_repos.ini')
