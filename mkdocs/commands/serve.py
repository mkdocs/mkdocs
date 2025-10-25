from __future__ import annotations

import logging
import os.path
import shutil
import tempfile
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.livereload import LiveReloadServer, _serve_url
from mkdocs.structure.files import Files

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger(__name__)


def serve(
    config_file: str | None = None,
    livereload: bool = True,
    build_type: str | None = None,
    watch_theme: bool = False,
    watch: list[str] = [],
    *,
    open_in_browser: bool = False,
    **kwargs,
) -> None:
    """
    Start the MkDocs development server.

    By default it will serve the documentation on http://localhost:8000/ and
    it will rebuild the documentation and refresh the page automatically
    whenever a file is edited.
    """
    # Create a temporary build directory, and set some options to serve it
    site_dir = tempfile.mkdtemp(prefix='mkdocs_')

    def get_config():
        config = load_config(
            config_file=config_file,
            site_dir=site_dir,
            **kwargs,
        )
        config.watch.extend(watch)
        return config

    is_clean = build_type == 'clean'
    is_dirty = build_type == 'dirty'

    config = get_config()
    config.plugins.on_startup(command=('build' if is_clean else 'serve'), dirty=is_dirty)

    host, port = config.dev_addr
    mount_path = urlsplit(config.site_url or '/').path
    config.site_url = serve_url = _serve_url(host, port, mount_path)

    files: Files = Files(())

    def builder(config: MkDocsConfig | None = None):
        log.info("Building documentation...")
        if config is None:
            config = get_config()
            config.site_url = serve_url

        nonlocal files
        files = build(config, serve_url=None if is_clean else serve_url, dirty=is_dirty)

    def file_hook(path: str) -> str | None:
        f = files.get_file_from_path(path)
        if f is not None and f.is_copyless_static_file:
            return f.abs_src_path
        return None

    def get_file(path: str) -> str | None:
        if new_path := file_hook(path):
            return os.path.join(site_dir, new_path)
        if os.path.isfile(try_path := os.path.join(site_dir, path)):
            return try_path
        return None

    server = LiveReloadServer(
        builder=builder,
        host=host,
        port=port,
        root=site_dir,
        file_hook=file_hook,
        mount_path=mount_path,
    )

    def error_handler(code) -> bytes | None:
        if code in (404, 500):
            if error_page := get_file(f'{code}.html'):
                with open(error_page, 'rb') as f:
                    return f.read()
        return None

    server.error_handler = error_handler

    try:
        # Perform the initial build
        builder(config)

        if livereload:
            # Watch the documentation files, the config file and the theme files.
            server.watch(config.docs_dir)
            if config.config_file_path:
                server.watch(config.config_file_path)

            if watch_theme:
                for d in config.theme.dirs:
                    server.watch(d)

            # Run `serve` plugin events.
            server = config.plugins.on_serve(server, config=config, builder=builder)

            for item in config.watch:
                server.watch(item)

        try:
            server.serve(open_in_browser=open_in_browser)
        except KeyboardInterrupt:
            log.info("Shutting down...")
        finally:
            server.shutdown()
    finally:
        config.plugins.on_shutdown()
        if os.path.isdir(site_dir):
            shutil.rmtree(site_dir)
