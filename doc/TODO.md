# Pending Features and Improvements

We reiterate that any support from the community will be greatly appreciated. If you are interested in tackling a missing feature or a possible improvement, kindly read through the [contribution guidelines](./CONTRIBUTING.md) before checking out the lists below.

### For Node Operators

- Alerting
    - Add a daily summary alert
    - Add alert for N missed in the last M precommits
    - Add alert for in and out of validator set (but this is essentially the voting power going to zero or non-zero)
    - Do not send 'missed block' alerts when validator is not in active set
    - Add a proposal monitor for 'new proposal' alerts.
    - Add more data sources (prometheus, node exporter, LCD REST, ...)
    - Improve alert limiting to prevent alert spam, especially in:
        - Validator peer change alerts (by adding a safe boundary)
        - Experiencing delays alerts
    - Reduced alert severity for nodes running on a testnet.
    - Add ability to switch on/off specific alerts and using different email/chat/number for different severity.
    - Have a list of outstanding alerts that can then be dismissed once acknowledged.
    - Alerts become less critical and should be toned down for testnet validators.
    - Add single alert when P.A.N.I.C. starts up, with state of all nodes.
    - Zero voting power for a validator currently causes "Jailed" alert, but this occurs in three cases: (i) actually jailed, (ii) out of validator set, (iii) catching up. A more specific and correct alert should be sent.
    - Consider using UTC time for any alert.
    - Consider adding ability to block all alerts temporarily, similar to snoozing calls.

- Telegram commands/status
    - Consider using UTC time for any status.
    - Add more node-specific information to the status using Redis, which already stores information such as number of peers, latest block, etc.
    
- Easier configuration and control
    - Use more of Telegram
    - Build a web-interface

- Install/Setup
    - Improve installation process, possibly with more automation by scripts
    - Improve the nodes/repos parts of the setup process. Currently these do not permit editing of the nodes/repos lists if they were already set up.
    - Add more documentation or a setup script for internal config.
    - Add documentation about the utility scripts.
    - Allow starting of P.A.N.I.C. even if some nodes not reachable using some special argument to the program.
    
- Problems to solve
    - If the network monitor is off for a long time, it has to go through all heights unless Redis is reset, possibly taking a long time to start checking the current heights, which are potentially more important.
    - If one of the monitors runs into an error, there is no way of restarting it without having to restart the whole alerter. There should be a way to restart each monitor, or at least the monitor restarts itself.
    - Some logs do not use RotatingFileHandler. However, these should not log as often, so this is not a critical issue
    - The `/validators`, `/tx`, and `/block` Telegram commands are network-dependent. These are currently useless for any non Cosmos Hub 2 chain.
    - Have a way to prove that the validator is still running, possibly by (i) signing a message, (ii) sending the current block number alongside the Telegram status, (iii) sending a current UTC time.
    
- Add support for more languages

### For Developers

- More unit testing to improve coverage
- Continuous integration
- Improve logging (especially debug logging)
- More commenting where necessary
- Possibly store alerter's state and data that it extracts in a database for later reference

### Other

- Use new context-based Telegram bot callbacks.

---
[Back to front page](../README.md)
