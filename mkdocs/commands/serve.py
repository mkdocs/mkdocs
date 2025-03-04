from __future__ import annotations

import hashlib
import json
import logging
import os.path
import shutil
import tempfile
import urllib.request
from os.path import isdir, isfile, join
from typing import TYPE_CHECKING, Any, Mapping
from urllib.error import HTTPError
from urllib.parse import urlsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.exceptions import Abort
from mkdocs.livereload import LiveReloadServer, ServerBindError, _serve_url

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger(__name__)

DEFAULT_PORT = 8000


def serve(
    config_file: str | None = None,
    livereload: bool = True,
    build_type: str | None = None,
    watch_theme: bool = False,
    watch: list[str] = [],
    *,
    port: int | None = None,
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
    # PY2 returns a byte string by default. The Unicode prefix ensures a Unicode
    # string is returned. And it makes MkDocs temp dirs easier to identify.
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
    if port is None:
        port = DEFAULT_PORT

    origin_info = dict(
        path=os.path.dirname(config.config_file_path) if config.config_file_path else os.getcwd(),
        site_name=config.site_name,
        site_url=config.site_url,
    )

    mount_path = urlsplit(config.site_url or '/').path
    config.site_url = serve_url = _serve_url(host, port, mount_path)

    def builder(config: MkDocsConfig | None = None):
        log.info("Building documentation...")
        if config is None:
            config = get_config()
            config.site_url = serve_url

        build(config, serve_url=None if is_clean else serve_url, dirty=is_dirty)

    server = LiveReloadServer(
        builder=builder,
        host=host,
        port=port,
        root=site_dir,
        mount_path=mount_path,
        origin_info=origin_info,
    )

    def error_handler(code) -> bytes | None:
        if code in (404, 500):
            error_page = join(site_dir, f'{code}.html')
            if isfile(error_page):
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
        except ServerBindError as e:
            log.error(f"Could not start a server on port {port}: {e}")
            msg = diagnose_taken_port(port, url=server.url, origin_info=origin_info)
            raise Abort(msg)

        except KeyboardInterrupt:
            log.info("Shutting down...")
        finally:
            server.shutdown()
    finally:
        config.plugins.on_shutdown()
        if isdir(site_dir):
            shutil.rmtree(site_dir)


def diagnose_taken_port(port: int, *, url: str, origin_info: Mapping[str, Any]) -> str:
    origin_info = dict(origin_info)
    path: str = origin_info.pop('path')

    message = f"Attempted to listen on port {port} but "
    other_info = None
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/livereload/.info.json') as resp:
            if resp.status == 200:
                other_info = json.load(resp)
    except HTTPError as e:
        message += "some unrecognized HTTP server is already running on that port."
        server = e.headers.get('server')
        if server:
            message += f" ({server!r})"
    except ValueError:
        message += "some unrecognized HTTP server is already running on that port."
    except Exception:
        message += "failed. And there isn't an HTTP server running on that port, but maybe another process is occupying it anyway."

    if other_info:
        message += "a live-reload server is already running on that port."
        if other_info['origin_info'].get('path') == path and other_info.get('url') == url:
            message += f"\nIt actually serves the same path '{path}', try simply visiting {url}"
        else:
            message += f" It serves a different path '{path}'."

    if "the same path" not in message:
        new_port = get_random_port(origin_info)
        message += (
            f"\n\nTry serving on another port by passing the flag `-p {new_port}` (as an example)."
        )
        if port == DEFAULT_PORT:
            message += f" Or permanently use a distinct port for this site by adding `serve_port: {new_port}` to its config."

    return message


def get_random_port(origin_info: dict[str, Any]) -> int:
    """Produce a "random" port number in range 8001-8064 that is reproducible for the current site."""
    hasher = hashlib.sha256(json.dumps(origin_info, sort_keys=True).encode())
    return DEFAULT_PORT + 1 + hasher.digest()[0] % 64
