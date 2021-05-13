import functools
import http.server
import io
import logging
import os
import os.path
import re
import socketserver
import threading
import time
import warnings
import wsgiref.simple_server

import watchdog.events
import watchdog.observers

log = logging.getLogger(__name__)


class LiveReloadServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    daemon_threads = True
    poll_response_timeout = 60

    def __init__(
        self, builder, host, port, root=".", build_delay=0.25, shutdown_delay=0.25, **kwargs
    ):
        self.builder = builder
        self.server_name = host
        self.server_port = port
        self.url = f"http://{host}:{port}/"
        self.root = os.path.abspath(root)
        self.build_delay = build_delay
        # To allow custom error pages.
        self.error_handler = lambda code: None

        super().__init__((host, port), _Handler, **kwargs)
        self.set_app(self.serve_request)

        self._wanted_epoch = _timestamp()  # The version of the site that started building.
        self._visible_epoch = self._wanted_epoch  # Latest fully built version of the site.
        self._epoch_cond = threading.Condition()  # Must be held when accessing _visible_epoch.

        self._to_rebuild = {}  # Used as an ordered set of functions to call.
        self._rebuild_cond = threading.Condition()  # Must be held when accessing _to_rebuild.

        self._shutdown = False
        self.serve_thread = threading.Thread(target=lambda: self.serve_forever(shutdown_delay))
        self.observer = watchdog.observers.Observer(timeout=shutdown_delay)

    def wait_for_build(self):
        """Wait until the ongoing rebuild (if any) finishes."""
        with self._epoch_cond:
            self._epoch_cond.wait_for(lambda: self._visible_epoch == self._wanted_epoch)

    def wait_for_epoch(self, epoch, timeout):
        """Wait until the site's version is newer than this (or timeout). Return the actual version"""
        with self._epoch_cond:
            self._epoch_cond.wait_for(lambda: self._visible_epoch > epoch, timeout=timeout)
            return self._visible_epoch

    def watch(self, path, func=None, recursive=True):
        """Add the 'path' to watched paths, call the function and reload when any file changes under it."""
        path = os.path.abspath(path)
        if func in (None, self.builder):
            func = self.builder
        else:
            warnings.warn(
                "Plugins should not pass the 'func' parameter of watch(). "
                "The ability to execute custom callbacks will be removed soon.",
                DeprecationWarning,
                stacklevel=2,
            )

        def callback(event):
            # Text editors always cause a "file close" event in addition to "modified" when saving
            # a file. Some editors also have "swap" functionality that keeps writing into another
            # file that's never closed. Prevent such write events from causing a rebuild.
            if isinstance(event, watchdog.events.FileModifiedEvent):
                # But FileClosedEvent is implemented only on Linux, otherwise we mustn't skip this:
                if type(self.observer).__name__ == "InotifyObserver":
                    return
            with self._rebuild_cond:
                self._to_rebuild[func] = True
                self._rebuild_cond.notify_all()

        handler = watchdog.events.FileSystemEventHandler()
        handler.on_any_event = callback
        self.observer.schedule(handler, path, recursive=recursive)

    def serve(self):
        self.observer.start()

        log.info(f"Serving on {self.url}")
        self.serve_thread.start()

        self._build_loop()

    def _build_loop(self):
        while True:
            with self._rebuild_cond:
                self._rebuild_cond.wait_for(lambda: self._to_rebuild or self._shutdown)
                if self._shutdown:
                    break
                log.info("Detected file changes")
                while self._rebuild_cond.wait(timeout=self.build_delay):
                    log.debug("Waiting for file changes to stop happening")

                self._wanted_epoch = _timestamp()
                funcs = list(self._to_rebuild)
                self._to_rebuild.clear()

            for func in funcs:
                func()

            with self._epoch_cond:
                log.info("Reloading browsers")
                self._visible_epoch = self._wanted_epoch
                self._epoch_cond.notify_all()

    def shutdown(self):
        self.observer.stop()
        with self._rebuild_cond:
            self._shutdown = True
            self._rebuild_cond.notify_all()

        if self.serve_thread.is_alive():
            super().shutdown()
            self.serve_thread.join()
            self.observer.join()

    def serve_request(self, environ, start_response):
        try:
            result = self._serve_request(environ, start_response)
        except Exception:
            code = 500
            msg = "500 Internal Server Error"
            log.exception(msg)
        else:
            if result is not None:
                return result
            code = 404
            msg = "404 Not Found"

        error_content = None
        try:
            error_content = self.error_handler(code)
        except Exception:
            log.exception(f"Failed to render an error message!")
        if error_content is None:
            error_content = msg.encode()

        start_response(msg, [("Content-Type", "text/html")])
        return [error_content]

    def _serve_request(self, environ, start_response):
        path = environ["PATH_INFO"]

        m = re.fullmatch(r"/livereload/([0-9]+)/[0-9]+", path)
        if m:
            epoch = int(m[1])
            self._log_poll_request(environ.get("HTTP_REFERER"), request_id=path)
            start_response("200 OK", [("Content-Type", "text/plain")])
            # Stall the browser, respond as soon as there's something new.
            # If there's not, respond anyway after a minute.
            epoch = self.wait_for_epoch(epoch, timeout=self.poll_response_timeout)
            return [b"%d" % epoch]

        if path == "/js/livereload.js":
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livereload.js")
        else:
            if path.endswith("/"):
                path += "index.html"
            file_path = os.path.join(self.root, path.lstrip("/"))

        self.wait_for_build()  # Otherwise we may be looking at a half-built site.
        epoch = self._visible_epoch
        try:
            file = open(file_path, "rb")
        except OSError:
            return None  # Not found

        if path.endswith(".html"):
            with file:
                content = file.read()
            content = self._inject_js_into_html(content, epoch)
            file = io.BytesIO(content)
            content_length = len(content)
        else:
            content_length = os.path.getsize(file_path)

        content_type = self.guess_type(file_path)
        start_response(
            "200 OK", [("Content-Type", content_type), ("Content-Length", str(content_length))]
        )
        return wsgiref.util.FileWrapper(file)

    @classmethod
    def _inject_js_into_html(cls, content, epoch):
        try:
            body_end = content.rindex(b"</body>")
        except ValueError:
            body_end = len(content)
        # The page will reload if the livereload poller returns a newer epoch than what it knows.
        # The other timestamp becomes just a unique identifier for the initiating page.
        return (
            b'%b<script src="/js/livereload.js"></script><script>livereload(%d, %d);</script>%b'
            % (content[:body_end], epoch, _timestamp(), content[body_end:])
        )

    @classmethod
    @functools.lru_cache()  # "Cache" to not repeat the same message for the same browser tab.
    def _log_poll_request(cls, url, request_id):
        log.info(f"Browser connected: {url}")

    # MkDocs only ensures a few common types (as seen in livereload_tests.py::test_mime_types).
    # Other uncommon types will not be accepted.
    extensions_map = {
        ".gz": "application/gzip",
        ".js": "application/javascript",
    }
    guess_type = http.server.SimpleHTTPRequestHandler.guess_type


class _Handler(wsgiref.simple_server.WSGIRequestHandler):
    def log_request(self, code="-", size="-"):
        level = logging.DEBUG if str(code) == "200" else logging.WARNING
        log.log(level, f'"{self.requestline}" code {code}')

    def log_message(self, format, *args):
        log.debug(format, *args)


def _timestamp():
    return round(time.monotonic() * 1000)
