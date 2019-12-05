import os
from configparser import ConfigParser


def main():
    if not os.path.isfile('config/user_config_main.ini'):
        print('User config does not exist, so there is no need to update it.')
        print('To create this file, you can run the setup (run_setup.py).')
        return

    cp = ConfigParser()
    cp.read('config/user_config_main.ini')

    # Create periodic_alive_reminder section
    if 'periodic_alive_reminder' in cp:
        print('Periodic alive reminder config was ALREADY UPDATED.')
    else:
        cp.add_section('periodic_alive_reminder')
        cp['periodic_alive_reminder']['enabled'] = str(False)
        cp['periodic_alive_reminder']['interval_seconds'] = ''
        cp['periodic_alive_reminder']['email_enabled'] = ''
        cp['periodic_alive_reminder']['telegram_enabled'] = ''
        print('Periodic alive reminder config UPDATED.')

    # Set new SMTP user and pass to blank
    if 'user' in cp['email_alerts'] and 'pass' in cp['email_alerts']:
        print('User and pass in email_alerts config were ALREADY UPDATED.')
    else:
        cp['email_alerts']['user'] = ''
        cp['email_alerts']['pass'] = ''
        print('User and pass in email_alerts config UPDATED (set to blank).')

    with open('config/user_config_main.ini', 'w') as f:
        cp.write(f)
        print('Update process finished.')


if __name__ == '__main__':
    main()
