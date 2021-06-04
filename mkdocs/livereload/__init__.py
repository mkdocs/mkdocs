import functools
import io
import logging
import mimetypes
import os
import os.path
import pathlib
import re
import socketserver
import threading
import time
import warnings
import wsgiref.simple_server

import watchdog.events
import watchdog.observers


class _LoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return time.strftime("[%H:%M:%S] ") + msg, kwargs


log = _LoggerAdapter(logging.getLogger(__name__), {})


class LiveReloadServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    daemon_threads = True
    poll_response_timeout = 60

    def __init__(
        self,
        builder,
        host,
        port,
        root,
        mount_path="/",
        build_delay=0.25,
        shutdown_delay=0.25,
        **kwargs,
    ):
        self.builder = builder
        self.server_name = host
        self.server_port = port
        self.root = os.path.abspath(root)
        self.mount_path = ("/" + mount_path.lstrip("/")).rstrip("/") + "/"
        self.url = f"http://{self.server_name}:{self.server_port}{self.mount_path}"
        self.build_delay = build_delay
        self.shutdown_delay = shutdown_delay
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

        def callback(event, allowed_path=None):
            if isinstance(event, watchdog.events.DirCreatedEvent):
                return
            if allowed_path is not None and event.src_path != allowed_path:
                return
            # Text editors always cause a "file close" event in addition to "modified" when saving
            # a file. Some editors also have "swap" functionality that keeps writing into another
            # file that's never closed. Prevent such write events from causing a rebuild.
            if isinstance(event, watchdog.events.FileModifiedEvent):
                # But FileClosedEvent is implemented only on Linux, otherwise we mustn't skip this:
                if type(self.observer).__name__ == "InotifyObserver":
                    return
            log.debug(str(event))
            with self._rebuild_cond:
                self._to_rebuild[func] = True
                self._rebuild_cond.notify_all()

        dir_handler = watchdog.events.FileSystemEventHandler()
        dir_handler.on_any_event = callback

        seen = set()

        def schedule(path):
            seen.add(path)
            if path.is_file():
                # Watchdog doesn't support watching files, so watch its directory and filter by path
                handler = watchdog.events.FileSystemEventHandler()
                handler.on_any_event = lambda event: callback(event, allowed_path=os.fspath(path))

                parent = path.parent
                log.debug(f"Watching file '{path}' through directory '{parent}'")
                self.observer.schedule(handler, parent)
            else:
                log.debug(f"Watching directory '{path}'")
                self.observer.schedule(dir_handler, path, recursive=recursive)

        schedule(pathlib.Path(path).resolve())

        def watch_symlink_targets(path_obj):  # path is os.DirEntry or pathlib.Path
            if path_obj.is_symlink():
                path_obj = pathlib.Path(path_obj).resolve()
                if path_obj in seen or not path_obj.exists():
                    return
                schedule(path_obj)

            if path_obj.is_dir() and recursive:
                with os.scandir(os.fspath(path_obj)) as scan:
                    for entry in scan:
                        watch_symlink_targets(entry)

        watch_symlink_targets(pathlib.Path(path))

    def serve(self):
        self.observer.start()

        log.info(f"Serving on {self.url}")
        self.serve_thread.start()

        self._build_loop()

    def _build_loop(self):
        while True:
            with self._rebuild_cond:
                while not self._rebuild_cond.wait_for(
                    lambda: self._to_rebuild or self._shutdown, timeout=self.shutdown_delay
                ):
                    # We could have used just one wait instead of a loop + timeout, but we need
                    # occasional breaks, otherwise on Windows we can't receive KeyboardInterrupt.
                    pass
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
            log.exception("Failed to render an error message!")
        if error_content is None:
            error_content = msg.encode()

        start_response(msg, [("Content-Type", "text/html")])
        return [error_content]

    def _serve_request(self, environ, start_response):
        path = environ["PATH_INFO"]

        m = re.fullmatch(r"/livereload/([0-9]+)/[0-9]+", path)
        if m:
            epoch = int(m[1])
            start_response("200 OK", [("Content-Type", "text/plain")])

            def condition():
                return self._visible_epoch > epoch

            with self._epoch_cond:
                if not condition():
                    # Stall the browser, respond as soon as there's something new.
                    # If there's not, respond anyway after a minute.
                    self._log_poll_request(environ.get("HTTP_REFERER"), request_id=path)
                    self._epoch_cond.wait_for(condition, timeout=self.poll_response_timeout)
                return [b"%d" % self._visible_epoch]

        if path == "/js/livereload.js":
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livereload.js")
        elif path.startswith(self.mount_path):
            if path.endswith("/"):
                path += "index.html"
            path = path[len(self.mount_path):]
            file_path = os.path.join(self.root, path.lstrip("/"))
        elif path == "/":
            start_response("302 Found", [("Location", self.mount_path)])
            return []
        else:
            return None  # Not found

        # Wait until the ongoing rebuild (if any) finishes, so we're not serving a half-built site.
        with self._epoch_cond:
            self._epoch_cond.wait_for(lambda: self._visible_epoch == self._wanted_epoch)
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

        content_type = self._guess_type(file_path)
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

    def _guess_type(cls, path):
        # MkDocs only ensures a few common types (as seen in livereload_tests.py::test_mime_types).
        # Other uncommon types will not be accepted.
        if path.endswith((".js", ".JS")):
            return "application/javascript"
        if path.endswith(".gz"):
            return "application/gzip"

        guess, _ = mimetypes.guess_type(path)
        if guess:
            return guess
        return "application/octet-stream"


class _Handler(wsgiref.simple_server.WSGIRequestHandler):
    def log_request(self, code="-", size="-"):
        level = logging.DEBUG if str(code) == "200" else logging.WARNING
        log.log(level, f'"{self.requestline}" code {code}')

    def log_message(self, format, *args):
        log.debug(format, *args)


def _timestamp():
    return round(time.monotonic() * 1000)
