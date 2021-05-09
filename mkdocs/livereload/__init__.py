import functools
import http.server
import io
import logging
import os.path
import re
import socketserver
import threading
import time
import warnings

import watchdog.events
import watchdog.observers

log = logging.getLogger(__name__)


class LiveReloadServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    poll_response_timeout = 60

    def __init__(
        self, builder, host, port, root=".", build_delay=0.1, shutdown_delay=0.25, **kwargs
    ):
        self.builder = builder
        self.url = f"http://{host}:{port}/"
        self.build_delay = build_delay
        # To allow custom error pages.
        self.error_handler = lambda code: None

        root = os.path.abspath(root)
        handler = functools.partial(LiveReloadRequestHandler, directory=root)
        super().__init__((host, port), handler, **kwargs)

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
                log.debug("Detected file changes")
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


class LiveReloadRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/js/livereload.js":
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "livereload.js")
        return super().translate_path(path)

    def send_head(self):
        epoch = self.server._visible_epoch

        file = super().send_head()
        if file and getattr(file, "name", "").endswith(".html"):
            try:
                content = file.read()
            finally:
                file.close()
            try:
                body_end = content.rindex(b"</body>")
            except ValueError:
                body_end = len(content)
            # The page will reload if the livereload poller returns a newer epoch than what it knows.
            # The other timestamp becomes just a unique identifier for the initiating page.
            file = io.BytesIO(
                b'%b<script src="/js/livereload.js"></script><script>livereload(%d, %d);</script>%b'
                % (content[:body_end], epoch, _timestamp(), content[body_end:])
            )
        return file

    def do_GET(self):
        m = re.fullmatch(r"/livereload/([0-9]+)/([0-9]+)", self.path)
        if m:
            return self._do_poll_response(epoch=int(m[1]), request_id=int(m[2]))

        self.server.wait_for_build()  # Otherwise we may be looking at a half-built site.
        return super().do_GET()

    def _do_poll_response(self, epoch, request_id):
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self._log_poll_request(self.headers.get("referer"), epoch, request_id)
        # Stall the browser, respond as soon as there's something new.
        # If there's not, respond anyway after a minute.
        epoch = self.server.wait_for_epoch(epoch, timeout=self.server.poll_response_timeout)
        self.wfile.write(b"%d" % epoch)

    @classmethod
    @functools.lru_cache()  # "Cache" to not repeat the same message for the same browser tab.
    def _log_poll_request(cls, url, epoch, request_id):
        log.info(f"Browser connected: {url}")

    def log_message(self, format, *args):
        log.debug(format, *args)

    def log_error(self, format, *args):
        log.warning('"%s" ' + format, self.requestline, *args)

    def send_error(self, code, message=None, *args, **kwargs):
        try:
            error_content = self.server.error_handler(code)
        except Exception:
            log.exception("Failed to render an error message")
        else:
            if error_content is not None:
                self.log_error("code %d", code)
                self.send_response(code, message)
                self.end_headers()
                self.wfile.write(error_content)
                return

        return super().send_error(code, message, *args, **kwargs)


def _timestamp():
    return round(time.monotonic() * 1000)
