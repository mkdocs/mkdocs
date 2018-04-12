from __future__ import unicode_literals
import textwrap
import markdown
import os
import logging
import collections
import unittest


from mkdocs import toc
from mkdocs import config
from mkdocs import utils


def dedent(text):
    return textwrap.dedent(text).strip()


def markdown_to_toc(markdown_source):
    md = markdown.Markdown(extensions=['toc'])
    md.convert(markdown_source)
    toc_output = md.toc
    return toc.TableOfContents(toc_output)


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
    conf = config.Config(schema=config.DEFAULT_SCHEMA, config_file_path=cfg['config_file_path'])
    conf.load_dict(cfg)

    errors_warnings = conf.validate()
    assert(errors_warnings == ([], [])), errors_warnings
    return conf


# Backport unittest.TestCase.assertLogs for Python 2.7
# see https://github.com/python/cpython/blob/3.6/Lib/unittest/case.py

if not utils.PY3:
    _LoggingWatcher = collections.namedtuple("_LoggingWatcher",
                                             ["records", "output"])

    class _CapturingHandler(logging.Handler):
        """
        A logging handler capturing all (raw and formatted) logging output.
        """

        def __init__(self):
            logging.Handler.__init__(self)
            self.watcher = _LoggingWatcher([], [])

        def flush(self):
            pass

        def emit(self, record):
            self.watcher.records.append(record)
            msg = self.format(record)
            self.watcher.output.append(msg)

    class _AssertLogsContext(object):
        """A context manager used to implement TestCase.assertLogs()."""

        LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

        def __init__(self, test_case, logger_name, level):
            self.test_case = test_case
            self.logger_name = logger_name
            if level:
                self.level = logging._levelNames.get(level, level)
            else:
                self.level = logging.INFO
            self.msg = None

        def __enter__(self):
            if isinstance(self.logger_name, logging.Logger):
                logger = self.logger = self.logger_name
            else:
                logger = self.logger = logging.getLogger(self.logger_name)
            formatter = logging.Formatter(self.LOGGING_FORMAT)
            handler = _CapturingHandler()
            handler.setFormatter(formatter)
            self.watcher = handler.watcher
            self.old_handlers = logger.handlers[:]
            self.old_level = logger.level
            self.old_propagate = logger.propagate
            logger.handlers = [handler]
            logger.setLevel(self.level)
            logger.propagate = False
            return handler.watcher

        def __exit__(self, exc_type, exc_value, tb):
            self.logger.handlers = self.old_handlers
            self.logger.propagate = self.old_propagate
            self.logger.setLevel(self.old_level)
            if exc_type is not None:
                # let unexpected exceptions pass through
                return False
            if len(self.watcher.records) == 0:
                self._raiseFailure(
                    "no logs of level {} or higher triggered on {}"
                    .format(logging.getLevelName(self.level), self.logger.name))

        def _raiseFailure(self, standardMsg):
            msg = self.test_case._formatMessage(self.msg, standardMsg)
            raise self.test_case.failureException(msg)

    class LogTestCase(unittest.TestCase):
        def assertLogs(self, logger=None, level=None):
            """Fail unless a log message of level *level* or higher is emitted
            on *logger_name* or its children.  If omitted, *level* defaults to
            INFO and *logger* defaults to the root logger.
            This method must be used as a context manager, and will yield
            a recording object with two attributes: `output` and `records`.
            At the end of the context manager, the `output` attribute will
            be a list of the matching formatted log messages and the
            `records` attribute will be a list of the corresponding LogRecord
            objects.
            Example::
                with self.assertLogs('foo', level='INFO') as cm:
                    logging.getLogger('foo').info('first message')
                    logging.getLogger('foo.bar').error('second message')
                self.assertEqual(cm.output, ['INFO:foo:first message',
                                             'ERROR:foo.bar:second message'])
            """
            return _AssertLogsContext(self, logger, level)
else:
    LogTestCase = unittest.TestCase
