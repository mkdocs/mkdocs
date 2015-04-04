import tempfile

from livereload import Server

from mkdocs.build import build
from mkdocs.config import load_config


def serve(config, options=None):
    """
    Start the devserver, and rebuild the docs whenever any changes take effect.
    """
    # Create a temporary build directory, and set some options to serve it
    tempdir = tempfile.mkdtemp()
    options['site_dir'] = tempdir

    def builder():
        config = load_config(options=options)
        build(config, live_server=True)

    # Perform the initial build
    builder()

    server = Server()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config'], builder)
    for d in config['theme_dir']:
        server.watch(d, builder)

    host, port = config['dev_addr'].split(':', 1)
    server.serve(root=tempdir, host=host, port=port, restart_delay=0)
