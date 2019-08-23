import sys

from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.exceptions import InitialisationException
from src.utils.logging import create_logger
from src.utils.redis_api import RedisApi


def run() -> None:
    # Check if Redis enabled
    if not UserConf.redis_enabled:
        raise InitialisationException('Redis is not set up. Run the setup '
                                      'script to configure Redis.')

    logger = create_logger(InternalConf.redis_log_file, 'redis',
                           InternalConf.logging_level)

    print('Deleting all Redis keys.')

    # Redis database
    try:
        RedisApi(
            logger, InternalConf.redis_database, UserConf.redis_host,
            UserConf.redis_port, password=UserConf.redis_password,
            namespace=UserConf.unique_alerter_identifier
        ).delete_all_unsafe()
    except Exception as e:
        sys.exit(e)

    # Redis test database
    try:
        RedisApi(
            logger, InternalConf.redis_test_database, UserConf.redis_host,
            UserConf.redis_port, password=UserConf.redis_password,
            namespace=UserConf.unique_alerter_identifier
        ).delete_all_unsafe()
    except Exception as e:
        sys.exit(e)

    print('Done deleting all Redis keys.')


if __name__ == '__main__':
    try:
        run()
    except InitialisationException as ie:
        sys.exit(ie)
