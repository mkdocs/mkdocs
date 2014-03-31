# coding: utf-8

from watchdog import events, observers
from mkdocs.build import build
from mkdocs.config import load_config
import os
import posixpath
import SimpleHTTPServer
import SocketServer
import shutil
import sys
import tempfile
import time
import urllib


class BuildEventHandler(events.FileSystemEventHandler):
    """
    Perform a rebuild when anything in the theme or docs directory changes.
    """
    def __init__(self, options):
        super(BuildEventHandler, self).__init__()
        self.options = options

    def on_any_event(self, event):
        if not isinstance(event, events.DirModifiedEvent):
            time.sleep(0.05)
            print 'Rebuilding documentation...',
            config = load_config(options=self.options)
            build(config, live_server=True)
            print ' done'


class ConfigEventHandler(BuildEventHandler):
    """
    Perform a rebuild when the config file changes.
    """
    def on_any_event(self, event):
        if os.path.basename(event.src_path) == 'mkdocs.yml':
            super(ConfigEventHandler, self).on_any_event(event)


class FixedDirectoryHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    Override the default implementation to allow us to specify the served
    directory, instead of being hardwired to the current working directory.
    """
    base_dir = os.getcwd()

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_dir
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def log_message(self, format, *args):
        date_str = self.log_date_time_string()
        sys.stderr.write('[%s] %s\n' % (date_str, format % args))


def serve(config, options=None):
    """
    Start the devserver, and rebuild the docs whenever any changes take effect.
    """
    # Create a temporary build directory, and set some options to serve it
    tempdir = tempfile.mkdtemp()
    options['site_dir'] = tempdir

    # Perform the initial build
    config = load_config(options=options)
    build(config, live_server=True)

    # Note: We pass any command-line options through so that we
    #       can re-apply them if the config file is reloaded.
    event_handler = BuildEventHandler(options)
    config_event_handler = ConfigEventHandler(options)
    observer = observers.Observer()
    observer.schedule(event_handler, config['docs_dir'], recursive=True)
    observer.schedule(event_handler, config['theme_dir'], recursive=True)
    observer.schedule(config_event_handler, '.')
    observer.start()

    class TCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    class DocsDirectoryHandler(FixedDirectoryHandler):
        base_dir = config['site_dir']

    host, port = config['dev_addr'].split(':', 1)
    server = TCPServer((host, int(port)), DocsDirectoryHandler)

    print 'Running at: http://%s:%s/' % (host, port)
    print 'Live reload enabled.'
    print 'Hold ctrl+c to quit.'
    server.serve_forever()

    # Clean up
    observer.stop()
    observer.join()
    shutil.rmtree(tempdir)
