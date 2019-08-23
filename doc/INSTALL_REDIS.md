# Redis Server

Before installing Redis, we recommend that you read through the [security model of Redis](https://redis.io/topics/security), which is meant to be run within a strictly trusted environment. The below installation, and P.A.N.I.C. in general, takes this security model into account and includes the suggested security boosts.

1. To install **Redis server** on your system:
    - On Linux, run:
      ```bash
      sudo apt-get install redis-server           # install Redis
      sudo systemctl enable redis-server.service  # set Redis to start on boot
      ```
    - On Windows, follow the installation steps [here](https://riptutorial.com/redis/example/29962/installing-and-running-redis-server-on-windows)
2. To **configure Redis**:
    1. First access the `redis.conf` file:
        - On Linux: `sudo nano /etc/redis/redis.conf`
        - On Windows: this is in the `conf/` folder of the installation directory.
    2. In the `GENERAL` section, add (or uncomment) the line `bind 127.0.0.1` to bind Redis only to localhost. This assumes that Redis is installed on the same system that will run the alerter.
    3. In the `SECURITY` section, add (or uncomment) the line `requirepass <PASS>`, where `<PASS>` is a complex password of your choosing. The alerter will ask for this password during setup.
    4. In the `SECURITY` section, you can also choose to disable some commands to prevent some actions from taking place. For each command, add a line: `rename-command <COMMAND> ""`.
        -  The following commands are *not* used by P.A.N.I.C. and can thus be disabled: `FLUSHALL`, `PEXPIRE`, `CONFIG`, `SHUTDOWN`, `BGREWRITEAOF`, `BGSAVE`, `SAVE`, `SPOP`, `SREM`, `RENAME` and `DEBUG`.
    5. On Linux, restart Redis to apply changes: `sudo service redis-server restart`

3. To **run Redis**:
    - On Linux, the Redis server should already be running.
    - On Windows, run `redis-server.exe` from the installation directory as administrator with the config file as an argument: `.\redis-server.exe conf\redis.conf`

**At the end, you should have:**
1. Redis server installed, secured, and running.
2. Ability to use Redis via the `redis-cli` command.
    - On Windows, `redis-cli.exe` is found in the installation directory.
    - To use Redis via the `redis-cli`, remember to authenticate using your password: `AUTH <PASSWORD>`.
    - Note that you do not have to have the *cli* running for the alerter to work.

## References and Further Reading:
- <https://redis.io/topics/security>
- <https://redislabs.com/blog/3-critical-points-about-security/>
- <https://www.digitalocean.com/community/tutorials/how-to-encrypt-traffic-to-redis-with-spiped-on-ubuntu-16-04>
- <https://www.digitalocean.com/community/tutorials/how-to-secure-your-redis-installation-on-ubuntu-14-04>
- <https://www.digitalocean.com/community/tutorials/how-to-secure-your-redis-installation-on-ubuntu-18-04>
- <https://stackoverflow.com/questions/40114913/allow-redis-connections-from-only-localhost>

---
[Back to main installation page](INSTALL_AND_RUN.md)