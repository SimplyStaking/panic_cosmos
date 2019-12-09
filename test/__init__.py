import os

from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.user import UserConfig

# Get path of this __init__.py file and go two steps up
os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print('Current working directory set to ' + os.getcwd())

TestInternalConf = InternalConfig(
    'test/test_internal_config.ini')
TestUserConf = UserConfig(
    'test/test_user_config_main.ini',
    'test/test_user_config_nodes.ini',
    'test/test_user_config_repos.ini')
