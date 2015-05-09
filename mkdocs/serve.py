import tempfile

from livereload import Server

from mkdocs.build import build
from mkdocs.config import load_config


def serve(config_file=None, dev_addr=None, strict=None, theme=None):
    """
    Start the devserver, and rebuild the docs whenever any changes take effect.
    """
    # Create a temporary build directory, and set some options to serve it
    tempdir = tempfile.mkdtemp()

    def builder():
        config = load_config(
            config_file=config_file,
            dev_addr=dev_addr,
            strict=strict,
            theme=theme,
        )
        config['site_dir'] = tempdir
        build(config, live_server=True)
        return config

    # Perform the initial build
    config = builder()

    server = Server()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config_file_path'], builder)

    for d in config['theme_dir']:
        server.watch(d, builder)

    host, port = config['dev_addr'].split(':', 1)
    server.serve(root=tempdir, host=host, port=int(port), restart_delay=0)
