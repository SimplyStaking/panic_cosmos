import os

from src.utils.config_parsers.user import UserConfig

USER_CONFIG_FILE_MAIN = 'config/user_config_main.ini'
USER_CONFIG_FILE_NODES = 'config/user_config_nodes.ini'
USER_CONFIG_FILE_REPOS = 'config/user_config_repos.ini'

USER_CONFIG_FILES = [USER_CONFIG_FILE_MAIN,
                     USER_CONFIG_FILE_NODES,
                     USER_CONFIG_FILE_REPOS]
MISSING_USER_CONFIG_FILES = [f for f in USER_CONFIG_FILES
                             if not os.path.isfile(f)]

if len(MISSING_USER_CONFIG_FILES) == 0:
    UserConf = UserConfig(USER_CONFIG_FILE_MAIN,
                          USER_CONFIG_FILE_NODES,
                          USER_CONFIG_FILE_REPOS)
else:
    UserConf = None
