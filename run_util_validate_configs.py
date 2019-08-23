from src.utils.exceptions import ConfigNotFoundException

if __name__ == '__main__':
    try:
        from src.utils.config_parsers.internal_parsed import InternalConf

        print('Internal configuration is valid.')
    except ConfigNotFoundException as cnfe:
        print(cnfe)
    except KeyError as ke:
        print('Internal configuration has missing section/key:', ke)

    try:
        from src.utils.config_parsers.user_parsed import UserConf

        print('User configuration is valid.')
    except ConfigNotFoundException as cnfe:
        print(cnfe)
    except KeyError as ke:
        print('User configuration has missing section/key:', ke)
