import logging
from typing import Optional

from src.alerting.alerts.alerts import NewGitHubReleaseAlert
from src.alerting.channels.channel import ChannelSet
from src.monitoring.monitor_utils.get_json import get_json
from src.monitoring.monitors.monitor import Monitor
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.redis_api import RedisApi


class GitHubMonitor(Monitor):

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 repo_name: str, releases_page: str,
                 redis_github_releases_key_prefix: str,
                 internal_conf: InternalConfig = InternalConf):
        super().__init__(monitor_name, channels, logger, redis, internal_conf)

        self.repo_name = repo_name
        self.releases_page = releases_page

        # The repo name is suffixed for uniqueness of key names in Redis
        self._redis_github_releases_key = \
            redis_github_releases_key_prefix + repo_name

        self._prev_no_of_releases = None

        self.load_state()

    def load_state(self) -> None:
        # If Redis is enabled, restore any previously stored number of releases
        if self.redis_enabled:
            self._prev_no_of_releases = self.redis.get_int(
                self._redis_github_releases_key, None)

            self.logger.debug(
                'Restored github monitor state: %s=%s',
                self._redis_github_releases_key, self._prev_no_of_releases)

    def save_state(self) -> None:
        # If Redis is enabled, save the currently known number of releases
        if self.redis_enabled:
            if self._prev_no_of_releases is None:
                self.logger.debug('Skipping github monitor state save '
                                  'due to None previous number of releases.')
                return

            self.logger.debug(
                'Saving github monitor state: %s=%s',
                self._redis_github_releases_key, self._prev_no_of_releases)
            self.redis.set(
                self._redis_github_releases_key, self._prev_no_of_releases)

    def monitor(self) -> None:
        # Get list of releases
        releases = get_json(self.releases_page, self._logger)

        # If response contains a message, skip monitoring this time round
        # since the presence of a message indicates an error in the API call
        if 'message' in releases:
            self.logger.warning('GitHub message: %s', releases['message'])
            return

        # Check that number of releases has not changed
        no_of_releases = len(releases)
        if self._prev_no_of_releases not in [None, no_of_releases]:
            if self._prev_no_of_releases < no_of_releases:
                self.channels.alert_info(NewGitHubReleaseAlert(
                    releases[0]['name'], self.repo_name))
            else:
                # Something went wrong; reset number of releases
                self.logger.error('The number of releases decreased from {} '
                                  'to {}: {}'.format(self._prev_no_of_releases,
                                                     no_of_releases, releases))
                self._prev_no_of_releases = None

        self._prev_no_of_releases = no_of_releases
