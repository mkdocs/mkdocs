#coding: utf-8

from mkdocs.build import build
from mkdocs.config import load_config
from watchdog import events
from watchdog.observers import Observer
import os
import posixpath
import SimpleHTTPServer
import SocketServer
import urllib


class BuildEventHandler(events.FileSystemEventHandler):
    """
    Perform a rebuild when anything in the theme or docs directory changes.
    """
    def on_any_event(self, event):
        if not isinstance(event, events.DirModifiedEvent):
            print 'Rebuilding documentation...',
            config = load_config()
            build(config)
            print ' done'


class ConfigEventHandler(BuildEventHandler):
    """
    Perform a rebuild when the config file changes.
    """
    def on_any_event(self, event):
        if os.path.basename(event.src_path) == 'mkdocs.yaml':
            super(ConfigEventHandler, self).on_any_event(event)


class FixedDirectoryHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    Override the default implementation to allow us to specify the served
    directory, instead of being hardwired to the current working directory.
    """
    base_dir = os.getcwd()

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_dir
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


def serve(config):
    config_event_handler = ConfigEventHandler()
    event_handler = BuildEventHandler()
    observer = Observer()
    observer.schedule(config_event_handler, '.')
    observer.schedule(event_handler, config['source_dir'], recursive=True)
    observer.schedule(event_handler, config['theme_dir'], recursive=True)
    observer.start()

    class TCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    class DocsDirectoryHandler(FixedDirectoryHandler):
        base_dir = config['output_dir']

    host, port = config['local_host'], config['local_port']
    server = TCPServer((host, port), DocsDirectoryHandler)

    print "Running at: http://%s:%s/" % (host, port)
    server.serve_forever()
    config_observer.stop()
    config_observer.join()
