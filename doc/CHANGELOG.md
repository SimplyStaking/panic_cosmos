# Change Log

## Unreleased

### Bug Fixes
* (genesis) Network monitor no longer crashes if the chain of the nodes being monitored has not started
* (repos) Repository names are now forced to be unique during setup. This is necessary to prevent key clashes in Redis

### Tendermint Compatibility Fixes
* (alerts) Added support for Cosmos SDK chains that use Tendermint v0.33+ to solve a startup crash
* (alerts) For chains that use Tendermint v0.33+, fixed total number of missing validators outputted when the missed blocks alert is raised

### Changes and Improvements
* (startup) Alerter can now start even if one or more nodes/repos are not accessible. It sends a single alert per inaccessible node/repo
* (twilio) Added official support for [TwiML](https://www.twilio.com/docs/voice/twiml). Configurable from the internal config to either a URL or raw TwiML instructions
* (downtime) Can now specify a delay before getting high severity alerts for node downtime by modifying the `downtime_initial_alert_delay_seconds` field in `internal_config.ini`.

## 1.1.1

Released on January 21, 2020.

### Update Instructions
If still not updated to `v1.1.0`, check out the [`v1.1.0` update instructions](https://github.com/SimplyVC/panic_cosmos/releases/tag/v1.1.0).

For `v1.1.0` to `v1.1.1`:
```shell script
git fetch            # Fetch these changes
git checkout v1.1.1  # Switch to this version
pipenv sync          # Update dependencies
```

P.A.N.I.C. can now be started up. If the alerter was running as a Linux service, the service should now be restarted:
```shell script
sudo systemctl restart panic_alerter
```

User config files from `v1.1.0` are compatible with `v1.1.1`.

### Features
* `/snooze` command now snoozes for a default number of hours (1 hour)
* `/mute` command now mutes for a default number of hours (1 hour)

### Changes and Improvements
* Updated Telegram explorer links from cosmoshub-2 to cosmoshub-3
* More testing coverage and improved code testability
* Minor documentation updates and fixes
* Improved Telegram command replies, especially when snoozing and muting
* Added timeout for "last height" status message in Telegram, similar to other messages
* Cleaned-up Telegram command handler class

### Bug Fixes
* Fixed double-logging in general log due to logger object being created twice
* Fixed tests not running due to PANIC expecting non-testing config files to exist
* Fixed periodic alive reminder crashing if Redis is not set up
* Fixed setup procedure not clearing nodes/repos if user chooses to do so
* Time-spans now show number of days if they exceed 24 hours

## 1.1.0

Released on December 09, 2019.

### Update Instructions

To update an instance of P.A.N.I.C. to this version:
```shell script
git fetch            # Fetch these changes
git checkout v1.1.0  # Switch to this version

pipenv sync          # Install dependencies
pipenv run python run_util_update_to_v1.1.0.py
```

The `run_util_update_to_v1.1.0.py` script updates `user_config_main.ini` so that it becomes compatible with the v1.1.0 `user_config_main.ini` file.

P.A.N.I.C. can now be started up. If the alerter was running as a Linux service, the service should now be restarted:

```shell script
sudo systemctl restart panic_alerter
```

### Features
* Add **authenticated SMTP**, so that email channel can use public SMTP servers, such as smtp.gmail.com, by supplying a valid username and password.
* Add **periodic alive reminder** as a way for the alerter to inform the user that it is still running. It is turned on through the setup process and can be muted/unmuted using commands from Telegram.
* Add **validator peer safe boundary** (`validator_peer_safe_boundary`, default: 5) to limit peer change alerts up to a certain number of peers.
* Add **max catch up blocks** (`network_monitor_max_catchup_blocks`, default: 500) to limit the number of historical blocks that the network monitor checks if it is not in sync, so that it focuses on the more important present events.
* Add **current network monitor block height** to Telegram status message.

### Changes and Improvements
* Email channel now supports multiple recipients.
* Internal config
  * Changed default GitHub monitor period to 3600 seconds (1h).
  * Changed default `full_node_peer_danger_boundary` to 10 for less alerts.
* Other:
  * Updated Telegram bot to use new context-based callbacks.
  * Now .gitignoring numbered log files (e.g. `*.log.1`)

### Bug Fixes
* Fixed full node peer increase alert not sent if the new number of peers is equal to the danger boundary.
* Setup processes now clear config file before adding new entries.

## 1.0.0

Released on August 23, 2019.

### Added
* First version of the P.A.N.I.C. alerter by Simply VC
