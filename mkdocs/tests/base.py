import textwrap
import markdown
import os
from functools import wraps
from tempfile import TemporaryDirectory

from mkdocs import config
from mkdocs import utils


def dedent(text):
    return textwrap.dedent(text).strip()


def get_markdown_toc(markdown_source):
    """ Return TOC generated by Markdown parser from Markdown source text. """
    md = markdown.Markdown(extensions=['toc'])
    md.convert(markdown_source)
    return md.toc_tokens


def load_config(**cfg):
    """ Helper to build a simple config for testing. """
    path_base = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'integration', 'minimal'
    )
    cfg = cfg or {}
    if 'site_name' not in cfg:
        cfg['site_name'] = 'Example'
    if 'config_file_path' not in cfg:
        cfg['config_file_path'] = os.path.join(path_base, 'mkdocs.yml')
    if 'docs_dir' not in cfg:
        # Point to an actual dir to avoid a 'does not exist' error on validation.
        cfg['docs_dir'] = os.path.join(path_base, 'docs')
    conf = config.Config(schema=config.defaults.get_schema(), config_file_path=cfg['config_file_path'])
    conf.load_dict(cfg)

    errors_warnings = conf.validate()
    assert(errors_warnings == ([], [])), errors_warnings
    return conf


def tempdir(files=None, **kw):
    """
    A decorator for building a temporary directory with prepopulated files.

    The temporary directory and files are created just before the wrapped function is called and are destroyed
    immediately after the wrapped function returns.

    The `files` keyword should be a dict of file paths as keys and strings of file content as values.
    If `files` is a list, then each item is assumed to be a path of an empty file. All other
    keywords are passed to `tempfile.TemporaryDirectory` to create the parent directory.

    In the following example, two files are created in the temporary directory and then are destroyed when
    the function exits:

        @tempdir(files={
            'foo.txt': 'foo content',
            'bar.txt': 'bar content'
        })
        def example(self, tdir):
            assert os.path.isfile(os.path.join(tdir, 'foo.txt'))
            pth = os.path.join(tdir, 'bar.txt')
            assert os.path.isfile(pth)
            with open(pth, 'r', encoding='utf-8') as f:
                assert f.read() == 'bar content'
    """
    files = {f: '' for f in files} if isinstance(files, (list, tuple)) else files or {}

    kw['prefix'] = 'mkdocs_test-' + kw.get('prefix', '')

    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args):
            with TemporaryDirectory(**kw) as td:
                for path, content in files.items():
                    pth = os.path.join(td, path)
                    utils.write_file(content.encode(encoding='utf-8'), pth)
                return fn(self, td, *args)
        return wrapper
    return decorator


class PathAssertionMixin:
    """
    Assertion methods for testing paths.

    Each method accepts one or more strings, which are first joined using os.path.join.
    """

    def assertPathsEqual(self, a, b, msg=None):
        self.assertEqual(a.replace('\\', '/'), b.replace('\\', '/'))

    def assertPathExists(self, *parts):
        path = os.path.join(*parts)
        if not os.path.exists(path):
            msg = self._formatMessage(None, f"The path '{path}' does not exist")
            raise self.failureException(msg)

    def assertPathNotExists(self, *parts):
        path = os.path.join(*parts)
        if os.path.exists(path):
            msg = self._formatMessage(None, f"The path '{path}' does exist")
            raise self.failureException(msg)

    def assertPathIsFile(self, *parts):
        path = os.path.join(*parts)
        if not os.path.isfile(path):
            msg = self._formatMessage(None, f"The path '{path}' is not a file that exists")
            raise self.failureException(msg)

    def assertPathNotFile(self, *parts):
        path = os.path.join(*parts)
        if os.path.isfile(path):
            msg = self._formatMessage(None, f"The path '{path}' is a file that exists")
            raise self.failureException(msg)

    def assertPathIsDir(self, *parts):
        path = os.path.join(*parts)
        if not os.path.isdir(path):
            msg = self._formatMessage(None, f"The path '{path}' is not a directory that exists")
            raise self.failureException(msg)

    def assertPathNotDir(self, *parts):
        path = os.path.join(*parts)
        if os.path.isfile(path):
            msg = self._formatMessage(None, f"The path '{path}' is a directory that exists")
            raise self.failureException(msg)
