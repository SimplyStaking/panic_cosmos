from configparser import ConfigParser

from src.setup import setup_user_config_main, setup_user_config_nodes, \
    setup_user_config_repos


def run() -> None:
    # Initialise parsers
    cp_main = ConfigParser()
    cp_main.read('config/user_config_main.ini')
    cp_nodes = ConfigParser()
    cp_nodes.read('config/user_config_nodes.ini')
    cp_repos = ConfigParser()
    cp_repos.read('config/user_config_repos.ini')

    # Start setup
    print('Welcome to the PANIC alerter!')
    try:
        setup_user_config_main.setup_all(cp_main)
        with open('config/user_config_main.ini', 'w') as f:
            cp_main.write(f)
        print('Saved config/user_config_main.ini\n')

        setup_user_config_nodes.setup_nodes(cp_nodes)
        with open('config/user_config_nodes.ini', 'w') as f:
            cp_nodes.write(f)
        print('Saved config/user_config_nodes.ini\n')

        setup_user_config_repos.setup_repos(cp_repos)
        with open('config/user_config_repos.ini', 'w') as f:
            cp_repos.write(f)
        print('Saved config/user_config_repos.ini\n')

        print('Setup completed!')
    except KeyboardInterrupt:
        print('Setup process stopped.')
        return


if __name__ == '__main__':
    run()
