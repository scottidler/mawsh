#!/usr/bin/env python3

import os
import sys
import json
import requests
sys.dont_write_bytecode = True

from functools import wraps
from configparser import ConfigParser
from argparse import ArgumentParser, RawDescriptionHelpFormatter

class DownloadAccountsJsonError(Exception):
    def __init__(self, result):
        msg = 'Error during download of accounts.json'
        super().__init__(msg)
OB = '{'
CB = '}'
GITHUB_TOKEN = '~/.config/mawsh/GITHUB_TOKEN'
GITHUB_API = 'https://api.github.com/repos'
GITHUB_API_VERSION = 'application/vnd.github.v3.raw'
REPONAME = 'mozilla-it/itsre-accounts'
FILEPATH = 'accounts.json'
ROLE_SUFFIXES = [
    'admin',
    'readonly',
    'poweruser',
    'viewonly',
]
ACTIONS = [
    'exec',
    'login',
    'role-arn',
]

def strip(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).strip()
    return wrapper

def rstrip(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).rstrip()
    return wrapper

def load_profiles(filepath):
    GITHUB_TOKEN = open(os.path.expanduser(filepath)).read().strip()
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': GITHUB_API_VERSION,
    }
    url = f'{GITHUB_API}/{REPONAME}/contents/{FILEPATH}'
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        raise DownloadAccountsJsonError(result)
    cfg = json.loads(result.content)
    return cfg

@strip
def role_suffixes():
    return ','.join(ROLE_SUFFIXES)

@strip
def actions():
    return '|'.join(ACTIONS)

@strip
def usage():
    return f'''
usage: paws [-h] [-G FILEPATH] [-r {role_suffixes()}] [{actions()}] profile
'''

@rstrip
def profiles(cfg, prefix='\n  - '):
    return prefix + prefix.join(sorted(cfg.keys()))

@strip
def usage_func():
    return f'''
function usage() {OB}
    cat <<EOF
{usage()}
EOF
{CB}
'''

@strip
def help_func(cfg):
    return f'''
function help() {OB}
    cat <<EOF
{usage()}

profiles:{profiles(cfg)}

positional arguments:
  action                [{actions()}]
  profile               choose a profile to look up its role arn

optional arguments:
  -r|--role-suffix      [{role_suffixes()}]
                        default="admin"; select role suffix
  -h, --help            show this help message and exit
EOF
{CB}
'''

def associative_array(cfg):
    return ' '.join([
        f'[{profile}]={account}' for
        profile, account in cfg.items()
    ])

@strip
def role_arn_func(cfg):
    return '''
function role_arn() {
    profile="$1"
    declare -A P2A ( {associative_array(cfg)} )
    echo ${OB}P2A[$profile]{CB}
}
'''


@strip
def kubeconfig():
    return ''

@strip
def mawsh():
    cfg = load_profiles(GITHUB_TOKEN)
    return f'''
#!/bin/bash

{usage_func()}

{help_func(cfg)}

case "$1" in
(exec)
    echo "exec"
    ;;
(login)
    echo "login"
    ;;
(role-arn)
    echo "role-arn"
    ;;
(-h|--help)
    help
    ;;
(*)
    usage
    ;;
esac
'''

def main(args):
    if args and args[0] in ('-x', '--execute'):
        with open('mawsh.sh', 'w') as f:
            f.write(mawsh())
        check_call('./mawsh.sh', args[1:])
    else:
        print(mawsh())

if __name__ == '__main__':
    main(sys.argv[1:])

#def main(args=None):
#    parser = ArgumentParser(
#        description=__doc__,
#        formatter_class=RawDescriptionHelpFormatter,
#        add_help=False)
#    parser.add_argument(
#        '-G', '--github-token',
#        metavar='FILEPATH',
#        default='~/.config/paws/GITHUB_TOKEN',
#        help='default="%(default)s"; filepath to github token')
#    ns, rem = parser.parse_known_args(args)
#    cfg = load_accounts(ns.github_token)
#    parser = ArgumentParser(
#        parents=[parser])
#    parser.add_argument(
#        '-r', '--role-suffix',
#        default=ROLE_SUFFIXES[0],
#        choices=ROLE_SUFFIXES,
#        help='default="%(default)s"; select role suffix')
#    parser.add_argument(
#        'profile',
#        choices=sorted(cfg.keys()),
#        help='choose a profile to look up its role arn')
#    ns = parser.parse_args(rem)
#    account = cfg[ns.profile]
#    arn = f'arn:aws:iam::{account}:role/maws-{ns.role_suffix}'
#    print(arn)


