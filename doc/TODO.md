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
    - Improve alert limiting, to prevent alert spam.
    - Reduced alert severity for nodes running on a testnet.
    - Add ability to switch on/off specific alerts and using different email/chat/number for different severity.
    - Have a list of outstanding alerts that can then be dismissed once acknowledged.
    
- Easier configuration and control
    - Use more of Telegram
    - Build a web-interface

- Install/Setup
    - Improve installation process, possibly with more automation by scripts
    - Improve the nodes/repos parts of the setup process. Currently these do not permit editing of the nodes/repos lists if they were already set up.
    
- Problems to solve
    - If the network monitor is off for a long time, it has to go through all heights unless Redis is reset, possibly taking a long time to start checking the current heights, which are potentially more important.
    - If one of the monitors runs into an error, there is no way of restarting it without having to restart the whole alerter.
    - Some logs do not use RotatingFileHandler. However, these should not log as often, so this is not a critical issue
    - The `/validators`, `/tx`, and `/block` Telegram commands are network-dependent. These are currently useless for any non Cosmos Hub 2 chain.
    
- Add support for more languages

### For Developers

- More unit testing to improve coverage
- Continuous integration
- Improve logging (especially debug logging)
- More commenting where necessary
- Possibly store alerter's state and data that it extracts in a database for later reference

---
[Back to front page](../README.md)