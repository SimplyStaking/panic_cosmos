# Installing and Running P.A.N.I.C.

This page will guide you through the steps required to get P.A.N.I.C. up and alerting, including the installation of preliminaries, setting up of 
P.A.N.I.C. itself, additional (optional) configuration, and running the alerter (directly or as a Linux service). Some steps are optional.

We recommend that the alerter is installed on a Linux system, given the simpler installation and running process. However, instructions on how to install P.A.N.I.C. on a Windows system are also provided. On a Debian-based Linux system, run the following before starting the installation process:
```bash
sudo apt-get update
sudo apt-get upgrade
```

## Requirements

The only major requirement to run P.A.N.I.C. is Python 3. However, to unlock the full potential of the alerter, we recommend that you install or set up as many of the below requirements as possible:
- Python v3.5.2+ with pip package manager and pipenv packaging tool.
- **Optional**: Telegram account and bots, for Telegram alerts and commands.
- **Optional**: Twilio account, for highly effective phone call alerts.
- **Optional**: Redis server, to keep a backup of the alerter state and to have some control over the alerter, such as to snooze phone call alerts using Telegram commands.

### Python (with pip and pipenv)

1. To install **Python v3.5.2 or greater**, you can [follow this guide](https://realpython.com/installing-python/).
2. To install **pip** package manager:
    - On Linux, run: `apt-get install python3-pip`
    - On Windows, it should come included in the installation.
3. To install **pipenv** packaging tool, run `pip install pipenv`.  
 (If 'pip' is not found, try using 'pip3' instead.)

**At the end, you should be able to:**
1. Get the Python version by running `python --version`.  
 (You may have to replace 'python' with 'python3.6', 'python3.7', etc.)
2. Get the pip version by running `pip --version`.
3. Get the pipenv version by running `pipenv --version`.

### Optional Features

- **Telegram**: [Click here](INSTALL_TELEGRAM.md) if you want to set up a Telegram account with bots.
- **Twilio**: [Click here](INSTALL_TWILIO.md) if you want to set up a Twilio account.
- **Redis server**: [Click here](INSTALL_REDIS.md) if you want to set up a Redis server.

## Setting up P.A.N.I.C.

P.A.N.I.C. requires its own setup process, involving three main parts, each of which generates its own respective config file:

- Linking up any of the optional features that you set up (`config/user_config_main.ini`)
- Providing a list of nodes that you wish to monitor (`config/user_config_nodes.ini`)
- Providing a list of GitHub repositories that you wish to monitor (`config/user_config_repos.ini`)

All of these steps are packaged into one setup process which is started up by running:
```bash
pipenv update
pipenv run python run_setup.py
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

Alternatively, you can take a look at the three `config/example_***.ini` files and perform the config file generation manually by copying the three example config files to the ones listed above and replacing the example pieces of information with actual ones.

The setup process is guided by instructions which we highly recommend that you read. The setup of any optional feature that was not set up in the previous section can be skipped. For convenience, any yes/no question can be answered with a *yes* just by pressing *ENTER*.

Lastly, note that if you wish to change some configurations and run the setup process again, it will detect the config files and will not simply overwrite the current configurations.

## Advanced Configuration

If you had a look in the `config/` folder, you may have seen the `config/internal_config.ini`. There is no setup process for the internal configuration because you do not have to modify it.

The internal configuration file defines values that are less likely to require changing. However, we encourage more advanced users to experiment with different configurations, if the consequences of any changes are realised and acknowledged beforehand.

This file consists of values such as:
- Which files to use for logging and the logging level
- Which Redis databases to use (10 and 11 by default)
- Which Redis keys to use to store values in Redis
- Timeout setting for certain temporary Redis keys
- **Data collection periods for each of the monitor types**
- **Alert frequency and severity modifiers (by time intervals and boundaries)**
- Links to use for the `/validators`, `/block`, and `/tx` Telegram commands.

## Running P.A.N.I.C.

After all of the setting-up, you will be glad to find out that running the alerter is a breeze. To start up P.A.N.I.C. simply run the following commands:
```bash
pipenv update
pipenv run python run_alerter.py
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

Assuming that the setup process was followed till the end, the above commands will start up all of the necessary node, network, and GitHub monitors. These will all start monitoring (and alerting) immediately.

It is recommended to check the console output or general log to make sure that all monitors started-up. Alternatively, you can run the `/status` command on Telegram if you set up both Telegram and Redis.

## Running P.A.N.I.C. as a Linux Service

Running the alerter as a service means that it start up automatically on boot and restarts automatically if it runs into some issue and stops running. To do so, we recommend the following steps:
```bash
# Add a new user to run the alerter
sudo adduser <USER>

# Grant permissions
sudo chown -R <USER>:<USER> <ALERTER_DIR>/  # ownership of alerter
sudo chmod -R 700 <ALERTER_DIR>/logs        # write permissions for logs
sudo chmod +x <ALERTER_DIR>/run_setup.py    # execute permission for runner (1)
sudo chmod +x <ALERTER_DIR>/run_alerter.py  # execute permission for runner (2)

# Create virtual environment using pipenv
cd <ALERTER_DIR>
su <USER> -c "pipenv update"
```

The service file will now be created:

```bash
# Create the service file
sudo nano /etc/systemd/system/panic_alerter.service
```

It should contain the following, replacing `<USER>` with the created user's name and the two `<ALERTER_DIR>` with the alerter's installation directory. This assumes that `pipenv` is found under `/usr/local/bin/pipenv` and that the Python executable is `python` (if multiple versions of Python are installed, the `python` executable may be `python3.6`, `python3.7`, etc.). We recommend that you run the command set for ExecStart manually to check that it works before starting the service.

```bash
[Unit]
Description=P.A.N.I.C.
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
User=<USER>
TimeoutStopSec=90s
WorkingDirectory=<ALERTER_DIR>/
ExecStart=/usr/local/bin/pipenv run python <ALERTER_DIR>/run_alerter.py

[Install]
WantedBy=multi-user.target
```

Lastly, we will *enable* and *start* the alerter service:

```bash
sudo systemctl enable panic_alerter.service
sudo systemctl start panic_alerter.service
```

Check out `systemctl status` or the logs in `<ALERTER_DIR>/logs/` to confirm that the alerter is running. Alternatively, if you set up Telegram, try interacting with the Telegram bot (using `/help`).

---
[Back to front page](../README.md)