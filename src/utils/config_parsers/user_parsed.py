from src.utils.config_parsers.user import UserConfig

USER_CONFIG_FILE_MAIN = 'config/user_config_main.ini'
USER_CONFIG_FILE_NODES = 'config/user_config_nodes.ini'
USER_CONFIG_FILE_REPOS = 'config/user_config_repos.ini'

UserConf = UserConfig(USER_CONFIG_FILE_MAIN,
                      USER_CONFIG_FILE_NODES,
                      USER_CONFIG_FILE_REPOS)
