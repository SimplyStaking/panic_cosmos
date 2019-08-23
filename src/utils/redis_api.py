import logging
from datetime import timedelta
from typing import Dict, Optional, Union, List

import redis

from src.utils.timing import TimedTaskLimiter

RedisType = Union[bytes, str, int, float]


class RedisApi:

    def __init__(self, logger: logging.Logger, db: int,
                 host: str = 'localhost', port: int = 6379,
                 password: str = '', namespace: str = '',
                 live_check_time_interval: timedelta = timedelta(seconds=60)) \
            -> None:
        self._logger = logger
        if password == '':
            self._redis = redis.Redis(host=host, port=port, db=db)
        else:
            self._redis = redis.Redis(host=host, port=port, db=db,
                                      password=password)
        self._namespace = namespace

        # The live check limiter means that we don't wait for connection
        # errors to occur to be able to continue, thus speeding everything up
        self._live_check_limiter = TimedTaskLimiter(live_check_time_interval)
        self._is_live = True  # This is necessary to initialise the variable
        self._set_as_live()

        self._logger.info('Redis initialised.')

    @property
    def is_live(self) -> bool:
        return self._is_live

    def _add_namespace(self, key: str) -> str:
        if not key.startswith(self._namespace + ':'):
            return self._namespace + ':' + key
        else:
            return key  # prevent adding namespace twice

    def _remove_namespace(self, key: str) -> str:
        if not key.startswith(self._namespace + ':'):
            return key  # prevent removing namespace twice
        else:
            return key.replace(self._namespace + ':', '', 1)

    def _set_as_live(self) -> None:
        if not self._is_live:
            self._logger.info('Redis is now accessible again.')
        self._is_live = True

    def _set_as_down(self) -> None:
        # If Redis is live or if we can check whether it is live (because the
        # live check time interval has passed), reset the live check limiter
        # so that usage of Redis is skipped for as long as the time interval
        if self._is_live or self._live_check_limiter.can_do_task():
            self._live_check_limiter.did_task()
            self._logger.warning('Redis is unusable for some reason. Stopping '
                                 'usage temporarily to improve performance.')
        self._is_live = False

    def _do_not_use_if_recently_went_down(self) -> bool:
        # If Redis is not live and cannot check if it is live (by using it)
        # then stop the function called from happening by returning True
        return not self._is_live and not self._live_check_limiter.can_do_task()

    def set_unsafe(self, key: str, value: RedisType):
        key = self._add_namespace(key)

        set_ret = self._redis.set(key, value)
        return set_ret

    def set_multiple_unsafe(self, key_values: Dict[str, RedisType]):
        # Add namespace to keys
        keys = list(key_values.keys())
        unique_keys = [self._add_namespace(k) for k in keys]
        for k, uk in zip(keys, unique_keys):
            key_values[uk] = key_values.pop(k)

        # Set multiple
        pipe = self._redis.pipeline()
        for key, value in key_values.items():
            pipe.set(key, value if value is not None else 'None')
        exec_ret = pipe.execute()
        return exec_ret

    def set_for_unsafe(self, key: str, value: RedisType, time: timedelta):
        key = self._add_namespace(key)

        pipe = self._redis.pipeline()
        pipe.set(key, value)
        pipe.expire(key, time)
        exec_ret = pipe.execute()
        return exec_ret

    def get_unsafe(self, key: str, default=None) -> Optional[bytes]:
        key = self._add_namespace(key)

        if self.exists_unsafe(key):
            get_ret = self._redis.get(key)
            if get_ret.decode('UTF-8') == 'None':
                return None
            else:
                return get_ret
        else:
            return default

    def get_int_unsafe(self, key: str, default=None) -> Optional[int]:
        key = self._add_namespace(key)

        get_ret = self.get_unsafe(key, None)
        try:
            return int(get_ret) if get_ret is not None else default
        except ValueError:
            self._logger.error(
                'Could not convert value %s of key %s to an integer. '
                'Defaulting to value %s.', get_ret, key, default)
            return default

    def get_bool_unsafe(self, key: str, default=None) -> Optional[bool]:
        key = self._add_namespace(key)

        get_ret = self.get_unsafe(key, None)
        return (get_ret.decode() == 'True') if get_ret is not None else default

    def exists_unsafe(self, key: str) -> bool:
        key = self._add_namespace(key)

        exists_ret = self._redis.exists(key)
        return bool(exists_ret)

    def get_keys_unsafe(self, pattern: str = "*") -> List[str]:
        pattern = self._add_namespace(pattern)

        # Decode and remove namespace
        keys_list = self._redis.keys(pattern)
        keys_list = [k.decode('utf8') for k in keys_list]
        keys_list = [self._remove_namespace(k) for k in keys_list]

        return keys_list

    def remove_unsafe(self, *keys):
        keys = [self._add_namespace(k) for k in keys]

        delete_ret = self._redis.delete(*keys)
        return delete_ret

    def delete_all_unsafe(self):
        flushdb_ret = self._redis.flushdb()
        return flushdb_ret

    def set(self, key: str, value: RedisType):
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self.set_unsafe(key, value)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in set: %s', e)
            self._set_as_down()
            return None

    def set_multiple(self, key_values: Dict[str, RedisType]):
        # Add namespace to keys
        keys = list(key_values.keys())
        unique_keys = [self._add_namespace(k) for k in keys]
        for k, uk in zip(keys, unique_keys):
            key_values[uk] = key_values.pop(k)

        # Set multiple
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self.set_multiple_unsafe(key_values)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in set_multiple: %s', e)
            self._set_as_down()
            return None

    def set_for(self, key: str, value: RedisType, time: timedelta):
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self.set_for_unsafe(key, value, time)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in set_for: %s', e)
            self._set_as_down()
            return None

    def get(self, key: str, default=None) -> Optional[bytes]:
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return default
            ret = self.get_unsafe(key, default)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in get: %s', e)
            self._set_as_down()
            return default

    def get_int(self, key: str, default=None) -> Optional[int]:
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return default
            ret = self.get_int_unsafe(key, default)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in get_int: %s', e)
            self._set_as_down()
            return default

    def get_bool(self, key: str, default=None) -> Optional[bool]:
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return default
            ret = self.get_bool_unsafe(key, default)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in get_bool: %s', e)
            self._set_as_down()
            return default

    def exists(self, key: str) -> bool:
        key = self._add_namespace(key)
        try:
            if self._do_not_use_if_recently_went_down():
                return False
            ret = self.exists_unsafe(key)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in exists: %s', e)
            self._set_as_down()
            return False

    def get_keys(self, pattern: str = "*") -> List[str]:
        pattern = self._add_namespace(pattern)

        try:
            if self._do_not_use_if_recently_went_down():
                return []
            ret = self.get_keys_unsafe(pattern)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in get_keys: %s', e)
            self._set_as_down()
            return []

    def remove(self, *keys):
        keys = [self._add_namespace(k) for k in keys]
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self.remove_unsafe(*keys)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in remove: %s', e)
            self._set_as_down()
            return None

    def delete_all(self):
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self.delete_all_unsafe()
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Redis error in delete_all: %s', e)
            self._set_as_down()
            return None

    def ping_unsafe(self) -> bool:
        return self._redis.ping()
