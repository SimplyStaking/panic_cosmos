from configparser import ConfigParser
from typing import Optional

from src.monitoring.monitor_utils.get_json import get_json
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import RepoConfig
from src.utils.logging import DUMMY_LOGGER
from src.utils.user_input import yn_prompt


def get_repo() -> Optional[RepoConfig]:
    # Get repo name
    repo_name = input('GitHub repository name (to know which repository '
                      'triggered an alert, example: Cosmos SDK):\n')

    # Get repo page
    while True:
        repo_page = input('Official GitHub repository (example: '
                          'cosmos/cosmos-sdk/):\n')
        if not repo_page.endswith('/'):
            repo_page = repo_page + '/'

        releases_page = InternalConf.github_releases_template.format(repo_page)
        print('Trying to connect to {}'.format(releases_page))
        try:
            releases = get_json(releases_page, DUMMY_LOGGER)
            if 'message' in releases and releases['message'] == 'Not Found':
                if not yn_prompt('Connection successful, but URL is not valid.'
                                 'Do you want to try again? (Y/n)\n'):
                    return None
            else:
                break  # success message left to setup_repos function
        except Exception:
            if not yn_prompt('Failed to connect to page. Do '
                             'you want to try again? (Y/n)\n'):
                return None

    # Return node
    return RepoConfig(repo_name, repo_page, True)


def setup_repos(cp: ConfigParser) -> None:
    print('==== GitHub Repositories')
    print('The GitHub monitor alerts on new releases in repositories. The list '
          'of GitHub repositories to monitor will now be set up.')

    # Check if list already set up
    if len(cp.sections()) > 0 and \
            not yn_prompt('The list of repositories is already set up. Do you '
                          'wish to clear this list? You will then be asked to '
                          'set up a new list, if you wish to do so (Y/n)\n'):
        return

    # Clear config and initialise new list
    cp.clear()
    repos = []

    # Ask if they want to set it up
    if not yn_prompt('Do you wish to set up the list of repos? (Y/n)\n'):
        return

    # Get repository details and append them to the list of repositories
    while True:
        repo = get_repo()
        if repo is not None:
            repos.append(repo)
            print('Successfully added repository.')

        if not yn_prompt('Do you want to add another repo? (Y/n)\n'):
            break

    # Add repos to config
    for i, repo in enumerate(repos):
        section = 'repo_' + str(i)
        cp.add_section(section)
        cp[section]['repo_name'] = repo.repo_name
        cp[section]['repo_page'] = repo.repo_page
        cp[section]['include_in_github_monitor'] = \
            'true' if repo.include_in_github_monitor else 'false'
