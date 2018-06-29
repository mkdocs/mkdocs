from __future__ import unicode_literals

import logging
import shutil
import tempfile

from os.path import isfile, join
from mkdocs.commands.build import build
from mkdocs.config import load_config

log = logging.getLogger(__name__)


def _get_handler(site_dir, StaticFileHandler):

    from tornado.template import Loader

    class WebHandler(StaticFileHandler):

        def write_error(self, status_code, **kwargs):

            if status_code in (404, 500):
                error_page = '{}.html'.format(status_code)
                if isfile(join(site_dir, error_page)):
                    self.write(Loader(site_dir).load(error_page).generate())
                else:
                    super(WebHandler, self).write_error(status_code, **kwargs)

    return WebHandler


def _livereload(host, port, config, builder, site_dir):

    # We are importing here for anyone that has issues with livereload. Even if
    # this fails, the --no-livereload alternative should still work.
    from livereload import Server
    import livereload.handlers

    class LiveReloadServer(Server):

        def get_web_handlers(self, script):
            handlers = super(LiveReloadServer, self).get_web_handlers(script)
            # replace livereload handler
            return [(handlers[0][0], _get_handler(site_dir, livereload.handlers.StaticFileHandler), handlers[0][2],)]

    server = LiveReloadServer()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config_file_path'], builder)

    for d in config['theme'].dirs:
        server.watch(d, builder)

    # Run `serve` plugin events.
    server = config['plugins'].run_event('serve', server, config=config)

    server.serve(root=site_dir, host=host, port=port, restart_delay=0)


def _static_server(host, port, site_dir):

    # Importing here to seperate the code paths from the --livereload
    # alternative.
    from tornado import ioloop
    from tornado import web

    application = web.Application([
        (r"/(.*)", _get_handler(site_dir, web.StaticFileHandler), {
            "path": site_dir,
            "default_filename": "index.html"
        }),
    ])
    application.listen(port=port, address=host)

    log.info('Running at: http://%s:%s/', host, port)
    log.info('Hold ctrl+c to quit.')
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        log.info('Stopping server...')


def serve(config_file=None, dev_addr=None, strict=None, theme=None,
          theme_dir=None, livereload='livereload'):
    """
    Start the MkDocs development server

    By default it will serve the documentation on http://localhost:8000/ and
    it will rebuild the documentation and refresh the page automatically
    whenever a file is edited.
    """

    # Create a temporary build directory, and set some options to serve it
    # PY2 returns a byte string by default. The Unicode prefix ensures a Unicode
    # string is returned. And it makes MkDocs temp dirs easier to identify.
    site_dir = tempfile.mkdtemp(prefix='mkdocs_')

    def builder():
        log.info("Building documentation...")
        config = load_config(
            config_file=config_file,
            dev_addr=dev_addr,
            strict=strict,
            theme=theme,
            theme_dir=theme_dir,
            site_dir=site_dir
        )
        # Override a few config settings after validation
        config['site_url'] = 'http://{0}/'.format(config['dev_addr'])

        live_server = livereload in ['dirty', 'livereload']
        dirty = livereload == 'dirty'
        build(config, live_server=live_server, dirty=dirty)
        return config

    try:
        # Perform the initial build
        config = builder()

        host, port = config['dev_addr']

        if livereload in ['livereload', 'dirty']:
            _livereload(host, port, config, builder, site_dir)
        else:
            _static_server(host, port, site_dir)
    finally:
        shutil.rmtree(site_dir)
