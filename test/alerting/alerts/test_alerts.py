import unittest
from datetime import datetime

from src.alerting.alerts.alerts import StillCannotAccessNodeAlert, \
    ExperiencingDelaysAlert, NowAccessibleAlert, NewGitHubReleaseAlert, \
    MissedBlocksAlert, TimedMissedBlocksAlert, NoLongerMissingBlocksAlert, \
    VotingPowerIncreasedAlert, VotingPowerDecreasedAlert, \
    VotingPowerDecreasedByAlert, VotingPowerIncreasedByAlert, \
    IsCatchingUpAlert, IsNoLongerCatchingUpAlert, PeersIncreasedAlert, \
    PeersIncreasedOutsideDangerRangeAlert, CouldNotFindLiveFullNodeAlert, \
    ErrorWhenReadingDataFromNode, CannotAccessGitHubPageAlert, \
    TerminatedDueToExceptionAlert, ProblemWithTelegramBot, \
    ProblemWhenCheckingIfCallsAreSnoozedAlert, ProblemWhenDialingNumberAlert, \
    CannotAccessNodeAlert, PeersDecreasedAlert


class TestAlerts(unittest.TestCase):
    def test_cannot_access_node_alert(self):
        node = 'Node Name'

        self.assertEqual('I cannot access {}.'.format(node),
                         str(CannotAccessNodeAlert(node)))

    def test_still_cannot_access_node_alert(self):
        node = 'Node Name'
        went_down_at = datetime.max
        downtime = '1 hours, 2 minutes, 3 seconds'

        self.assertEqual(
            'I still cannot access {}. Node became inaccessible at {} '
            'and has been inaccessible for (at most) {}.'.format(
                node, went_down_at, downtime),
            str(StillCannotAccessNodeAlert(node, went_down_at, downtime)))

    def test_experiencing_delays_alert(self):
        node = 'Node Name'

        self.assertEqual(
            'Experiencing delays when trying to access {}.'.format(node),
            str(ExperiencingDelaysAlert(node)))

    def test_now_accessible_alert(self):
        node = 'Node Name'
        went_down_at = datetime.max
        downtime = '1 hours, 2 minutes, 3 seconds'

        self.assertEqual(
            '{} is now accessible. Node became inaccessible '
            'at {} and was inaccessible for (at most) {}.'
            ''.format(node, went_down_at, downtime),
            str(NowAccessibleAlert(node, went_down_at, downtime)))

    def test_new_github_release_alert(self):
        release_name = 'v1.2.3.4'
        repo_name = 'Cosmos SDK'

        self.assertEqual(
            '{} of {} has just been released.'.format(release_name, repo_name),
            str(NewGitHubReleaseAlert(release_name, repo_name)))

    def test_missed_blocks_alert(self):
        node = 'Node Name'
        blocks = 1000000
        height = 2000000
        missing_validators = 3000000

        self.assertEqual(
            '{} missed {} blocks in a row (height: {}, total validators '
            'missing: {}).'.format(node, blocks, height, missing_validators),
            str(MissedBlocksAlert(node, blocks, height, missing_validators)))

    def test_timed_missed_blocks_alert(self):
        node = 'Node Name'
        blocks = 1000000
        time_interval = 'Time Interval'
        height = 2000000
        missing_validators = 3000000

        self.assertEqual(
            '{} missed {} blocks in time interval {} (height: {}, '
            'total validators missing: {}).'.format(
                node, blocks, time_interval, height, missing_validators),
            str(TimedMissedBlocksAlert(
                node, blocks, time_interval, height, missing_validators)))

    def test_no_longer_missing_blocks_alert(self):
        node = 'Node Name'
        consecutive_blocks = 1000000

        self.assertEqual(
            '{} is no longer missing blocks (Total missed in a row: {}).'
            ''.format(node, consecutive_blocks),
            str(NoLongerMissingBlocksAlert(node, consecutive_blocks)))

    def test_voting_power_increased_alert(self):
        node = 'Node Name'
        old_power = 1000000
        new_power = 2000000

        self.assertEqual(
            '{} voting power INCREASED from {} to {}.'.format(
                node, old_power, new_power),
            str(VotingPowerIncreasedAlert(node, old_power, new_power)))

    def test_voting_power_decreased_alert(self):
        node = 'Node Name'
        old_power = 1000000
        new_power = 2000000

        self.assertEqual(
            '{} voting power DECREASED from {} to {}.'.format(
                node, old_power, new_power),
            str(VotingPowerDecreasedAlert(node, old_power, new_power)))

    def test_voting_power_increased_by_alert_with_positive_change(self):
        node = 'Node Name'
        old_power = 1000000
        new_power = 2000000
        change = new_power - old_power

        self.assertEqual(
            '{} voting power INCREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power),
            str(VotingPowerIncreasedByAlert(node, old_power, new_power)))

    def test_voting_power_increased_by_alert_with_negative_change(self):
        node = 'Node Name'
        old_power = 2000000
        new_power = 1000000
        change = new_power - old_power

        self.assertEqual(
            '{} voting power INCREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power),
            str(VotingPowerIncreasedByAlert(node, old_power, new_power)))

    def test_voting_power_decreased_by_alert_with_positive_change(self):
        node = 'Node Name'
        old_power = 2000000
        new_power = 1000000
        change = old_power - new_power

        self.assertEqual(
            '{} voting power DECREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power),
            str(VotingPowerDecreasedByAlert(node, old_power, new_power)))

    def test_voting_power_decreased_by_alert_with_negative_change(self):
        node = 'Node Name'
        old_power = 1000000
        new_power = 2000000
        change = old_power - new_power

        self.assertEqual(
            '{} voting power DECREASED by {} from {} to {}.'.format(
                node, change, old_power, new_power),
            str(VotingPowerDecreasedByAlert(node, old_power, new_power)))

    def test_is_catching_up_alert(self):
        node = 'Node Name'

        self.assertEqual('{} is in a catching-up state.'.format(node),
                         str(IsCatchingUpAlert(node)))

    def test_is_no_longer_catching_up_alert(self):
        node = 'Node Name'

        self.assertEqual('{} is no longer catching-up.'.format(node),
                         str(IsNoLongerCatchingUpAlert(node)))

    def test_peers_increased_alert(self):
        node = 'Node Name'
        old_peers = 1000000
        new_peers = 2000000

        self.assertEqual(
            '{} peers INCREASED from {} to {}.'.format(
                node, old_peers, new_peers),
            str(PeersIncreasedAlert(node, old_peers, new_peers)))

    def test_peers_decreased_alert(self):
        node = 'Node Name'
        old_peers = 1000000
        new_peers = 2000000

        self.assertEqual(
            '{} peers DECREASED from {} to {}.'.format(
                node, old_peers, new_peers),
            str(PeersDecreasedAlert(node, old_peers, new_peers)))

    def test_peers_increased_outside_danger_range_alert(self):
        node = 'Node Name'
        danger = 1000000

        self.assertEqual(
            '{} peers INCREASED to more than {} peers. No further peer change '
            'alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, danger, danger),
            str(PeersIncreasedOutsideDangerRangeAlert(node, danger)))

    def test_could_not_find_live_full_node_alert(self):
        net_monitor_name = 'cosmoshub-2 network monitor'
        self.assertEqual('{} could not find a live full node to use as a '
                         'data source.'.format(net_monitor_name),
                         str(CouldNotFindLiveFullNodeAlert(net_monitor_name)))

    def test_error_when_reading_data_from_node(self):
        node = 'Node Name'

        self.assertEqual(
            'Error when reading data from {}. Alerter '
            'will continue running normally.'.format(node),
            str(ErrorWhenReadingDataFromNode(node)))

    def test_cannot_access_github_page_alert(self):
        page = 'GitHubPage.com'

        self.assertEqual('I cannot access GitHub page {}.'.format(page),
                         str(CannotAccessGitHubPageAlert(page)))

    def test_terminated_due_to_exception_alert(self):
        component = 'Some Monitor'
        exception = Exception('Some Exception')

        self.assertEqual(
            '{} terminated due to exception: {}'.format(component, exception),
            str(TerminatedDueToExceptionAlert(component, exception)))

    def test_problem_with_telegram_bot(self):
        description = 'Something went wrong'

        self.assertEqual(
            'Problem encountered with telegram bot: {}'.format(description),
            str(ProblemWithTelegramBot(description)))

    def test_problem_when_checking_if_calls_are_snoozed_alert(self):
        self.assertEqual('Problem encountered when checking if '
                         'calls are snoozed. Calling anyways.',
                         str(ProblemWhenCheckingIfCallsAreSnoozedAlert()))

    def test_problem_when_dialing_number_alert(self):
        number = 'Some Number'
        exception = Exception('Some Exception')

        self.assertEqual(
            'Problem encountered when dialing {}: {}'.format(number, exception),
            str(ProblemWhenDialingNumberAlert(number, exception)))
