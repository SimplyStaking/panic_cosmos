from datetime import datetime


class Alert:

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self.message


class ExperiencingDelaysAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            'Experiencing delays when trying to access {}.'.format(node))


class CannotAccessNodeAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            'I cannot access {}. Node became inaccessible at {} '
            'and has been inaccessible for (at most) {}.'.format(
                node, went_down_at, downtime))


class StillCannotAccessNodeAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            'I still cannot access {}. Node became inaccessible at {} '
            'and has been inaccessible for (at most) {}.'.format(
                node, went_down_at, downtime))


class NowAccessibleAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            '{} is now accessible. Node became inaccessible '
            'at {} and was inaccessible for (at most) {}.'
            ''.format(node, went_down_at, downtime))


class CouldNotFindLiveFullNodeAlert(Alert):

    def __init__(self, network_monitor: str) -> None:
        super().__init__('{} could not find a live full node to use as a '
                         'data source.'.format(network_monitor))


class MissedBlocksAlert(Alert):

    def __init__(self, node: str, blocks: int, height: int,
                 missing_validators: int) -> None:
        super().__init__(
            '{} missed {} blocks in a row (height: {}, total validators '
            'missing: {}).'.format(node, blocks, height, missing_validators))


class TimedMissedBlocksAlert(Alert):

    def __init__(self, node: str, blocks: int, time_interval: str,
                 height: int, missing_validators: int) -> None:
        super().__init__(
            '{} missed {} blocks in time interval {} (height: {}, '
            'total validators missing: {}).'.format(
                node, blocks, time_interval, height, missing_validators))


class NoLongerMissingBlocksAlert(Alert):

    def __init__(self, node: str, consecutive_blocks: int) -> None:
        super().__init__(
            '{} is no longer missing blocks (Total missed in a row: {}).'
            ''.format(node, consecutive_blocks))


class VotingPowerIncreasedAlert(Alert):

    def __init__(self, node: str, old_power: int, new_power: int) -> None:
        super().__init__(
            '{} voting power INCREASED from {} to {}.'.format(
                node, old_power, new_power))


class VotingPowerDecreasedAlert(Alert):

    def __init__(self, node: str, old_power: int, new_power: int) -> None:
        super().__init__(
            '{} voting power DECREASED from {} to {}.'.format(
                node, old_power, new_power))


class VotingPowerIncreasedByAlert(Alert):

    def __init__(self, node: str, old_power: int, new_power: int) -> None:
        change = new_power - old_power
        super().__init__(
            '{} voting power INCREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power))


class VotingPowerDecreasedByAlert(Alert):

    def __init__(self, node: str, old_power: int, new_power: int) -> None:
        change = old_power - new_power
        super().__init__(
            '{} voting power DECREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power))


class PeersIncreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            '{} peers INCREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class PeersIncreasedOutsideDangerRangeAlert(Alert):

    def __init__(self, node: str, danger: int) -> None:
        super().__init__(
            '{} peers INCREASED to more than {} peers. No further peer change '
            'alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, danger, danger))


class PeersIncreasedOutsideSafeRangeAlert(Alert):

    def __init__(self, node: str, safe: int) -> None:
        super().__init__(
            '{} peers INCREASED to more than {} peers. No further peer change'
            ' alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, safe, safe))


class PeersDecreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            '{} peers DECREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class IsCatchingUpAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} is in a catching-up state.'.format(node))


class IsNoLongerCatchingUpAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} is no longer catching-up.'.format(node))


class ProblemWhenDialingNumberAlert(Alert):

    def __init__(self, number: str, exception: Exception) -> None:
        super().__init__(
            'Problem encountered when dialing {}: {}'.format(number, exception))


class ProblemWhenCheckingIfCallsAreSnoozedAlert(Alert):

    def __init__(self) -> None:
        super().__init__('Problem encountered when checking if '
                         'calls are snoozed. Calling anyways.')


class NewGitHubReleaseAlert(Alert):

    def __init__(self, release_name: str, repo_name: str) -> None:
        super().__init__(
            '{} of {} has just been released.'.format(release_name, repo_name))


class CannotAccessGitHubPageAlert(Alert):

    def __init__(self, page: str) -> None:
        super().__init__('I cannot access GitHub page {}.'.format(page))


class ErrorWhenReadingDataFromNode(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            'Error when reading data from {}. Alerter '
            'will continue running normally.'.format(node))


class TerminatedDueToExceptionAlert(Alert):

    def __init__(self, component: str, exception: Exception) -> None:
        super().__init__(
            '{} terminated due to exception: {}'.format(component, exception))


class ProblemWithTelegramBot(Alert):

    def __init__(self, description: str) -> None:
        super().__init__(
            'Problem encountered with telegram bot: {}'.format(description))


class AlerterAliveAlert(Alert):

    def __init__(self) -> None:
        super().__init__('Still running.')


class NodeInaccessibleDuringStartup(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            'Node {} was not accessible during PANIC startup. {} will NOT be '
            'monitored until it is accessible and PANIC restarted afterwards. '
            'Some features of PANIC might be affected.'.format(node, node))


class RepoInaccessibleDuringStartup(Alert):

    def __init__(self, repo: str) -> None:
        super().__init__(
            'Repo {} was not accessible during PANIC startup. {} will NOT be '
            'monitored until it is accessible and PANIC restarted afterwards. '
            ''.format(repo, repo))
