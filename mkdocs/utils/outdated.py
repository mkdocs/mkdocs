from __future__ import absolute_import

import datetime
import json
import logging
import os.path
import sys

from pip._vendor import lockfile
from pip._vendor.packaging import version as packaging_version

from pip.compat import total_seconds, WINDOWS
from pip.locations import USER_CACHE_DIR, running_under_virtualenv
from pip.utils.filesystem import check_path_owner

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

SELFCHECK_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


logger = logging.getLogger(__name__)

def ensure_dir(path):
    """os.path.makedirs without EEXIST."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class VirtualenvSelfCheckState(object):
    def __init__(self):
        self.statefile_path = os.path.join(sys.prefix, "mkdocs-selfcheck.json")

        try:
            with open(self.statefile_path) as statefile:
                self.state = json.load(statefile)
        except (IOError, ValueError):
            self.state = {}

    def save(self, pypi_version, current_time):
        with open(self.statefile_path, "w") as statefile:
            json.dump(
                {
                    "last_check": current_time.strftime(SELFCHECK_DATE_FMT),
                    "pypi_version": pypi_version,
                },
                statefile,
                sort_keys=True,
                separators=(",", ":")
            )


class GlobalSelfCheckState(object):
    def __init__(self):
        self.statefile_path = os.path.join(USER_CACHE_DIR, "mkdocs-selfcheck.json")

        try:
            with open(self.statefile_path) as statefile:
                self.state = json.load(statefile)[sys.prefix]
        except (IOError, ValueError, KeyError):
            self.state = {}

    def save(self, pypi_version, current_time):
        # Check to make sure that we own the directory
        if not check_path_owner(os.path.dirname(self.statefile_path)):
            return

        # Now that we've ensured the directory is owned by this user, we'll go
        # ahead and make sure that all our directories are created.
        ensure_dir(os.path.dirname(self.statefile_path))

        # Attempt to write out our version check file
        with lockfile.LockFile(self.statefile_path):
            if os.path.exists(self.statefile_path):
                with open(self.statefile_path) as statefile:
                    state = json.load(statefile)
            else:
                state = {}

            state[sys.prefix] = {
                "last_check": current_time.strftime(SELFCHECK_DATE_FMT),
                "pypi_version": pypi_version,
            }

            with open(self.statefile_path, "w") as statefile:
                json.dump(state, statefile, sort_keys=True,
                          separators=(",", ":"))


def load_selfcheck_statefile():
    if running_under_virtualenv():
        return VirtualenvSelfCheckState()
    else:
        return GlobalSelfCheckState()


def pypi_mkdocs_version():
    url = 'http://pypi.python.org/pypi/MkDocs/json'

    response = urlopen(url)
    data = response.read().decode('UTF-8')

    return json.loads(data)['info']['version']


def mkdocs_version_check():
    """Check for an update for mkdocs.
    Limit the frequency of checks to once per week. State is stored either in
    the active virtualenv or in the user's USER_CACHE_DIR keyed off the prefix
    of the pip script path.
    """
    import mkdocs  # imported here to prevent circular imports
    pypi_version = None

    try:
        state = load_selfcheck_statefile()

        current_time = datetime.datetime.utcnow()
        # Determine if we need to refresh the state
        if "last_check" in state.state and "pypi_version" in state.state:
            last_check = datetime.datetime.strptime(
                state.state["last_check"],
                SELFCHECK_DATE_FMT
            )
            if total_seconds(current_time - last_check) < 7 * 24 * 60 * 60:
                pypi_version = state.state["pypi_version"]

        # Refresh the version if we need to or just see if we need to warn
        if pypi_version is None:
            pypi_version = pypi_mkdocs_version()

            # save that we've performed a check
            state.save(pypi_version, current_time)

        mkdocs_version = packaging_version.parse(mkdocs.__version__)
        remote_version = packaging_version.parse(pypi_version)

        # Determine if our pypi_version is older
        if (mkdocs_version < remote_version and
                mkdocs_version.base_version != remote_version.base_version):
            # Advise "python -m pip" on Windows to avoid issues
            # with overwriting pip.exe.
            if WINDOWS:
                pip_cmd = "python -m pip"
            else:
                pip_cmd = "pip"
            logger.warning(
                "You are using mkdocs version %s, however version %s is "
                "available.\nYou should consider upgrading via the "
                "'%s install --upgrade mkdocs' command." % (
                    mkdocs.__version__,
                    pypi_version,
                    pip_cmd)
            )

    except Exception:
        logger.debug(
            "There was an error checking the latest version of mkdocs",
            exc_info=True,
        )
