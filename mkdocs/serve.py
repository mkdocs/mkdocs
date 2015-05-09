import tempfile

from livereload import Server

from mkdocs.build import build


def serve(config):
    """
    Start the devserver, and rebuild the docs whenever any changes take effect.
    """
    # Create a temporary build directory, and set some options to serve it
    tempdir = tempfile.mkdtemp()
    config['site_dir'] = tempdir

    def builder():
        build(config, live_server=True)

    # Perform the initial build
    builder()

    server = Server()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config_file_path'], builder)

    for d in config['theme_dir']:
        server.watch(d, builder)

    host, port = config['dev_addr'].split(':', 1)
    server.serve(root=tempdir, host=host, port=int(port), restart_delay=0)
