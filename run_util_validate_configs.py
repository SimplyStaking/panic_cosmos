from src.utils.exceptions import ConfigNotFoundException

if __name__ == '__main__':
    try:
        from src.utils.config_parsers.internal_parsed import InternalConf, \
            INTERNAL_CONFIG_FILE_FOUND, INTERNAL_CONFIG_FILE

        if INTERNAL_CONFIG_FILE_FOUND:
            print('Internal configuration is valid.')
        else:
            print('Config file {} is missing.'.format(INTERNAL_CONFIG_FILE))
    except ConfigNotFoundException as cnfe:
        print(cnfe)
    except KeyError as ke:
        print('Internal configuration has missing section/key:', ke)

    try:
        from src.utils.config_parsers.user_parsed import UserConf, \
            MISSING_USER_CONFIG_FILES

        if len(MISSING_USER_CONFIG_FILES) == 0:
            print('User configuration is valid.')
        else:
            print('Config file {} is missing.'.format(
                MISSING_USER_CONFIG_FILES[0]))
    except ConfigNotFoundException as cnfe:
        print(cnfe)
    except KeyError as ke:
        print('User configuration has missing section/key:', ke)
