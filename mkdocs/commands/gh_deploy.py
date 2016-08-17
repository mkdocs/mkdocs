from __future__ import unicode_literals
import logging
import subprocess
import os

import mkdocs
from mkdocs.utils import ghp_import

log = logging.getLogger(__name__)

default_message = """Deployed {sha} with MkDocs version: {version}"""


def _is_cwd_git_repo():
    proc = subprocess.Popen(['git', 'rev-parse', '--is-inside-work-tree'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()
    return proc.wait() == 0


def _get_current_sha():

    proc = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, _ = proc.communicate()
    sha = stdout.decode('utf-8').strip()
    return sha


def _get_remote_url(remote_name):

    # No CNAME found.  We will use the origin URL to determine the GitHub
    # pages location.
    remote = "remote.%s.url" % remote_name
    proc = subprocess.Popen(["git", "config", "--get", remote],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, _ = proc.communicate()
    url = stdout.decode('utf-8').strip()

    host = None
    path = None
    if 'github.com/' in url:
        host, path = url.split('github.com/', 1)
    elif 'github.com:' in url:
        host, path = url.split('github.com:', 1)

    return host, path


def gh_deploy(config, message=None, force=False):

    if not _is_cwd_git_repo():
        log.error('Cannot deploy - this directory does not appear to be a git '
                  'repository')

    if message is None:
        sha = _get_current_sha()
        message = default_message.format(version=mkdocs.__version__, sha=sha)

    remote_branch = config['remote_branch']
    remote_name = config['remote_name']

    log.info("Copying '%s' to '%s' branch and pushing to GitHub.",
             config['site_dir'], config['remote_branch'])

    result, error = ghp_import.ghp_import(config['site_dir'], message, remote_name,
                                          remote_branch, force)
    if not result:
        log.error("Failed to deploy to GitHub with error: \n%s", error)
        raise SystemExit(1)
    else:
        cname_file = os.path.join(config['site_dir'], 'CNAME')
        # Does this repository have a CNAME set for GitHub pages?
        if os.path.isfile(cname_file):
            # This GitHub pages repository has a CNAME configured.
            with(open(cname_file, 'r')) as f:
                cname_host = f.read().strip()
            log.info('Based on your CNAME file, your documentation should be '
                     'available shortly at: http://%s', cname_host)
            log.info('NOTE: Your DNS records must be configured appropriately for '
                     'your CNAME URL to work.')
            return

        host, path = _get_remote_url(remote_name)

        if host is None:
            # This could be a GitHub Enterprise deployment.
            log.info('Your documentation should be available shortly.')
        else:
            username, repo = path.split('/', 1)
            if repo.endswith('.git'):
                repo = repo[:-len('.git')]
            url = 'https://%s.github.io/%s/' % (username, repo)
            log.info('Your documentation should shortly be available at: ' + url)
