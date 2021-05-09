import functools
import http.server
import io
import logging
import os.path
import re
import socketserver
import threading
import time

import watchdog.events
import watchdog.observers

log = logging.getLogger(__name__)


class LiveReloadServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def __init__(self, builder, host, port, root="."):
        self.builder = builder

        self.url = f"http://{host}:{port}/"
        # To allow custom error pages.
        self.error_handler = lambda code: None

        root = os.path.abspath(root)
        handler = functools.partial(LiveReloadRequestHandler, server=self, directory=root)
        super().__init__((host, port), handler)

        self._epoch = _timestamp()  # The version of the site (time at which it was last built).
        self._epoch_cond = threading.Condition()  # Must be held when accessing _epoch.

        self._to_rebuild = {}  # Used as an ordered set of functions to call.
        self._rebuild_cond = threading.Condition()  # Must be held when accessing _to_rebuild.

        self.observer = watchdog.observers.Observer()

        self.serve_thread = threading.Thread(target=self.serve_forever)

    def wait_for_epoch(self, epoch, timeout):
        """Wait until the site's version is newer than this."""
        with self._epoch_cond:
            self._epoch_cond.wait_for(lambda: self._epoch > epoch, timeout=timeout)
            return self._epoch

    def watch(self, path, func=None, recursive=True):
        """Add the 'path' to watched paths, call the function and reload when any file changes under it."""
        path = os.path.abspath(path)
        if func is None:
            func = self.builder

        def callback():
            with self._rebuild_cond:
                self._to_rebuild[func] = True
                self._rebuild_cond.notify_all()

        handler = _ThrottledEventHandler(callback)
        self.observer.schedule(handler, path, recursive=recursive)

    def serve(self):
        self.observer.start()

        log.info(f"Serving on {self.url}")
        self.serve_thread.start()

        while True:
            with self._rebuild_cond:
                self._rebuild_cond.wait()
                log.debug("Detected file changes")
                now = _timestamp()
                funcs = list(self._to_rebuild)
                self._to_rebuild.clear()

            for func in funcs:
                func()

            with self._epoch_cond:
                log.info("Reloading browsers")
                self._epoch = now
                self._epoch_cond.notify_all()

    def shutdown(self):
        self.observer.stop()
        super().shutdown()
        self.observer.join()
        self.serve_thread.join()


class LiveReloadRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, server, **kwargs):
        self._server = server
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        if path == "/js/livereload.js":
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "livereload.js")
        return super().translate_path(path)

    def send_head(self):
        epoch = self._server._epoch

        file = super().send_head()
        if file and getattr(file, "name", "").endswith(".html"):
            parts = file.read().rpartition(b"</body>")
            # The page will reload if the livereload poller returns a newer epoch than what it knows.
            # The other timestamp becomes just a unique identifier for the initiating page.
            file = io.BytesIO(
                b'%b<script src="/js/livereload.js"></script><script>livereload(%d, %d);</script>%b%b'
                % (parts[0], epoch, _timestamp(), parts[1], parts[2])
            )
        return file

    def do_GET(self):
        m = re.fullmatch(r"/livereload/([0-9]+)/([0-9]+)", self.path)
        if m:
            return self._do_poll_response(epoch=int(m[1]), request_id=int(m[2]))
        return super().do_GET()

    def _do_poll_response(self, epoch, request_id):
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self._log_poll_request(self.headers.get("referer"), epoch, request_id)
        # Stall the browser, respond as soon as there's something new.
        # If there's not, respond anyway after a minute.
        epoch = self._server.wait_for_epoch(epoch, timeout=60)
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
            error_content = self._server.error_handler(code)
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


class _ThrottledEventHandler(watchdog.events.FileSystemEventHandler):
    """Event handler for Watchdog, calling the callback not more frequently than once per interval.

    That is done for the 2 purposes:
      * collapsing a burst of events for 1 file into one;
      * throttling in case files are modified too frequently.
    """

    def __init__(self, callback, interval=0.5):
        self.callback = callback
        self.interval = interval
        self.last_triggered = float("-inf")
        self._lock = threading.Lock()

    def on_any_event(self, event):
        with self._lock:
            now = time.monotonic()
            if now < self.last_triggered + self.interval:
                return
            self.last_triggered = now
            self.callback()
