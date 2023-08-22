import datetime
import hashlib
import logging
import os
import urllib.parse
import urllib.request

import click
import platformdirs

log = logging.getLogger(__name__)


def download_and_cache_url(
    url: str,
    cache_duration: datetime.timedelta,
    comment: bytes = b'# ',
) -> bytes:
    """
    Downloads a file from the URL, stores it under ~/.cache/, and returns its content.

    If the URL is a local path, it is simply read and returned instead.

    For tracking the age of the content, a prefix is inserted into the stored file, rather than relying on mtime.

    Parameters:
        url: URL or local path of the file to use.
        cache_duration: how long to consider the URL content cached.
        comment: The appropriate comment prefix for this file format.
    """

    if urllib.parse.urlsplit(url).scheme not in ('http', 'https'):
        with open(url, 'rb') as f:
            return f.read()

    directory = os.path.join(platformdirs.user_cache_dir('mkdocs'), 'mkdocs_url_cache')
    name_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
    path = os.path.join(directory, name_hash + os.path.splitext(url)[1])

    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    prefix = b'%s%s downloaded at timestamp ' % (comment, url.encode())
    # Check for cached file and try to return it
    if os.path.isfile(path):
        try:
            with open(path, 'rb') as f:
                line = f.readline()
                if line.startswith(prefix):
                    line = line[len(prefix) :]
                    timestamp = int(line)
                    if datetime.timedelta(seconds=(now - timestamp)) <= cache_duration:
                        log.debug(f"Using cached '{path}' for '{url}'")
                        return f.read()
        except (OSError, ValueError) as e:
            log.debug(f'{type(e).__name__}: {e}')

    # Download and cache the file
    log.debug(f"Downloading '{url}' to '{path}'")
    with urllib.request.urlopen(url) as resp:
        content = resp.read()
    os.makedirs(directory, exist_ok=True)
    with click.open_file(path, 'wb', atomic=True) as f:
        f.write(b'%s%d\n' % (prefix, now))
        f.write(content)
    return content
