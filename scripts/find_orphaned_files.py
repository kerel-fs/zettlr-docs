#!/usr/bin/env python
# Usage: ./find_orphaned_files.py

import subprocess
import requests

GIT_LOG_COMMAND =  'git log --diff-filter=D --name-status docs/ | grep "^D\s"'
BASE_URL = 'https://docs.zettlr.com/'


def git_list_all_deleted_markdown_files():
    """
    List all files which have been deleted at some point from the repository
    in the current working directory.
    """
    cmd = subprocess.run(GIT_LOG_COMMAND, shell=True, capture_output=True)
    lines = cmd.stdout.decode('utf-8').strip().split('\n')
    all_deleted_filenames = list(l.removeprefix('D\t') for l in lines)
    
    deleted_markdown_files = list(l for l in all_deleted_filenames if l.endswith('.md'))

    return deleted_markdown_files


def check_orphaned_file_exists(filename):
    """
    For a given relative path in the zettlr-docs repo,
    check if there exists a corresponding page on https://docs.zettlr.com

    Arguments
    ---------
    filename: A relative path to a markdown file in the zettlr-docs repo

    Returns
    -------
    True or False
    """
    relative_path = filename.removeprefix('docs/').removesuffix('.md')
    url = BASE_URL + relative_path
    response = requests.get(url)

    return url, response.status_code == 200


if __name__ == '__main__':
    deleted_markdown_files = git_list_all_deleted_markdown_files()

    output = []
    for filename in deleted_markdown_files:
        print(f'Check {filename}...', end='', flush=True)
        url, status_exists = check_orphaned_file_exists(filename)
        if status_exists:
            print('STALE')
            output.append(url)
        else:
            print('DELETED')

    print('\n' * 2)
    print('The following files on docs.zettlr.com are STALE and do not have a corresponding'
          ' markdown file in the zettlr-docs repo anymore:')
    for url in output:
        print(url)
