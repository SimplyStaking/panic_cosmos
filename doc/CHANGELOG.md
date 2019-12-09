# Change Log

## 1.1.0

Released on December 05, 2019.

### Update Instructions

To update an instance of P.A.N.I.C. to this version:
```shell script
git fetch            # Fetch these changes
git checkout v1.1.0  # Switch to this version

pipenv update        # Update dependencies
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