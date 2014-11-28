# coding: utf-8
from __future__ import print_function

from watchdog import events
from watchdog.observers.polling import PollingObserver
from mkdocs.build import build
from mkdocs.compat import httpserver, socketserver, urlunquote, urlparse, urlunparse
from mkdocs.config import load_config
import os
import posixpath
import shutil
import sys
import tempfile


class BuildEventHandler(events.FileSystemEventHandler):
    """
    Perform a rebuild when anything in the theme or docs directory changes.
    """
    def __init__(self, options):
        super(BuildEventHandler, self).__init__()
        self.options = options

    def on_any_event(self, event):
        if not isinstance(event, events.DirModifiedEvent):
            print('Rebuilding documentation...', end='')
            config = load_config(options=self.options)
            build(config, live_server=True)
            print(' done')


class ConfigEventHandler(BuildEventHandler):
    """
    Perform a rebuild when the config file changes.
    """
    def on_any_event(self, event):
        try:
            if os.path.basename(event.src_path) == 'mkdocs.yml':
                super(ConfigEventHandler, self).on_any_event(event)
        except Exception as e:
            print(e)


class FixedDirectoryHandler(httpserver.SimpleHTTPRequestHandler):
    """
    Override the default implementation to allow us to specify the served
    directory, instead of being hardwired to the current working directory.
    """
    base_dir = os.getcwd()

    def do_GET(self):
        """
        The SimpleHTTPRequestHandler isn't designed to work with query strings.
        Everything we do with the query string is handle on the client-side, so
        throw it away here.
        """
        scheme, netloc, path, query, query, fragment = urlparse(self.path)
        if query is not '':
            self.path = urlunparse((scheme, netloc, path, '', '', fragment))
        return httpserver.SimpleHTTPRequestHandler.do_GET(self)

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urlunquote(path))
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

    # Only use user-friendly URLs when running the live server
    options['use_directory_urls'] = True

    # Perform the initial build
    config = load_config(options=options)
    build(config, live_server=True)

    # Note: We pass any command-line options through so that we
    #       can re-apply them if the config file is reloaded.
    event_handler = BuildEventHandler(options)
    config_event_handler = ConfigEventHandler(options)

    # We could have used `Observer()`, which can be faster, but
    # `PollingObserver()` works more universally.
    observer = PollingObserver()
    observer.schedule(event_handler, config['docs_dir'], recursive=True)
    for theme_dir in config['theme_dir']:
        observer.schedule(event_handler, theme_dir, recursive=True)
    observer.schedule(config_event_handler, '.')
    observer.start()

    class TCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    class DocsDirectoryHandler(FixedDirectoryHandler):
        base_dir = config['site_dir']

    host, port = config['dev_addr'].split(':', 1)
    server = TCPServer((host, int(port)), DocsDirectoryHandler)

    print('Running at: http://%s:%s/' % (host, port))
    print('Live reload enabled.')
    print('Hold ctrl+c to quit.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping server...')

    # Clean up
    observer.stop()
    observer.join()
    shutil.rmtree(tempdir)
    print('Quit complete')
