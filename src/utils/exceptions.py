class NoLiveFullNodeException(Exception):
    pass


class ConfigNotFoundException(Exception):

    def __init__(self, config_file: str) -> None:
        super().__init__('File {} not found.'.format(config_file))


class InitialisationException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
