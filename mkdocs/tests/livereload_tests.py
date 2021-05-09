#!/usr/bin/env python

import contextlib
import email
import io
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from mkdocs.livereload import LiveReloadServer
from mkdocs.tests.base import tempdir


class FakeRequest:
    def __init__(self, content):
        self.in_file = io.BytesIO(content.encode())
        self.out_file = io.BytesIO()
        self.out_file.close = lambda: None

    def makefile(self, *args, **kwargs):
        return self.in_file

    def sendall(self, data):
        self.out_file.write(data)


@contextlib.contextmanager
def testing_server(root, builder=lambda: None):
    """Create the server and start most of its parts, but don't listen on a socket."""
    with mock.patch("socket.socket"):
        server = LiveReloadServer(
            builder, host="localhost", port=0, root=root, bind_and_activate=False
        )
    server.observer.start()
    thread = threading.Thread(target=server._build_loop, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    thread.join()


def do_request(server, content):
    request = FakeRequest(content + " HTTP/1.1")
    server.RequestHandlerClass(request, ("127.0.0.1", 0), server)
    response = request.out_file.getvalue()
    headers, _, content = response.partition(b"\r\n\r\n")
    message, _, headers = headers.partition(b"\r\n")
    return email.message_from_bytes(headers), content.decode()


SCRIPT_REGEX = (
    r'<script src="/js/livereload.js"></script><script>livereload\([0-9]+, [0-9]+\);</script>'
)


class BuildTests(unittest.TestCase):
    @tempdir({"index.html": "<body>aaa</body>", "foo/index.html": "<body>bbb</body>"})
    def test_serves_index(self, site_dir):
        with testing_server(site_dir) as server:
            headers, output = do_request(server, "GET /")
            self.assertRegex(output, "^<body>aaa<")
            self.assertEqual(headers["content-type"], "text/html")

            _, output = do_request(server, "GET /foo/")
            self.assertRegex(output, "^<body>bbb<")

    @tempdir({"foo.docs": "a"})
    @tempdir({"foo.site": "original"})
    def test_basic_rebuild(self, site_dir, docs_dir):
        started_building = threading.Event()

        def rebuild():
            started_building.set()
            content = Path(docs_dir, "foo.docs").read_text()
            Path(site_dir, "foo.site").write_text(content * 5)

        with testing_server(site_dir, rebuild) as server:
            server.watch(docs_dir, rebuild)

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "original")

            Path(docs_dir, "foo.docs").write_text("b")
            started_building.wait()

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "bbbbb")

    @tempdir({"foo.docs": "a"})
    @tempdir({"foo.site": "original"})
    def test_rebuild_after_delete(self, site_dir, docs_dir):
        started_building = threading.Event()

        def rebuild():
            started_building.set()
            Path(site_dir, "foo.site").unlink()

        with testing_server(site_dir, rebuild) as server:
            server.watch(docs_dir, rebuild)

            Path(docs_dir, "foo.docs").write_text("b")
            started_building.wait()

            with self.assertLogs("mkdocs.livereload"):
                _, output = do_request(server, "GET /foo.site")

            self.assertIn("404", output)

    @tempdir({"foo.docs": "a"})
    @tempdir({"foo.site": "original"})
    def test_custom_action_warns(self, site_dir, docs_dir):
        started_building = threading.Event()

        def rebuild():
            started_building.set()
            content = Path(docs_dir, "foo.docs").read_text()
            Path(site_dir, "foo.site").write_text(content * 5)

        with testing_server(site_dir) as server:
            with self.assertWarnsRegex(DeprecationWarning, "func") as cm:
                server.watch(docs_dir, rebuild)
            self.assertIn("livereload_tests.py", cm.filename)

            Path(docs_dir, "foo.docs").write_text("b")
            started_building.wait()

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "bbbbb")

    @tempdir({"foo.docs": "docs1"})
    @tempdir({"foo.extra": "extra1"})
    @tempdir({"foo.site": "original"})
    def test_multiple_dirs_changes_rebuild_only_once(self, site_dir, extra_dir, docs_dir):
        started_building = threading.Event()

        def rebuild():
            self.assertFalse(started_building.is_set())
            started_building.set()
            content1 = Path(docs_dir, "foo.docs").read_text()
            content2 = Path(extra_dir, "foo.extra").read_text()
            Path(site_dir, "foo.site").write_text(content1 + content2)

        with testing_server(site_dir, rebuild) as server:
            server.watch(docs_dir)
            server.watch(extra_dir)

            _, output = do_request(server, "GET /foo.site")
            Path(docs_dir, "foo.docs").write_text("docs2")
            Path(extra_dir, "foo.extra").write_text("extra2")
            started_building.wait()

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "docs2extra2")

    @tempdir({"foo.docs": "a"})
    @tempdir({"foo.site": "original"})
    def test_change_is_detected_while_building(self, site_dir, docs_dir):
        before_finished_building = threading.Barrier(2)
        can_finish_building = threading.Event()

        def rebuild():
            content = Path(docs_dir, "foo.docs").read_text()
            Path(site_dir, "foo.site").write_text(content * 5)
            before_finished_building.wait()
            can_finish_building.wait()

        with testing_server(site_dir, rebuild) as server:
            server.watch(docs_dir)

            Path(docs_dir, "foo.docs").write_text("b")
            before_finished_building.wait()
            Path(docs_dir, "foo.docs").write_text("c")
            can_finish_building.set()

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "bbbbb")

            before_finished_building.wait()

            _, output = do_request(server, "GET /foo.site")
            self.assertEqual(output, "ccccc")

    @tempdir(
        {
            "normal.html": "<html><body>hello</body></html>",
            "no_body.html": "<p>hi",
            "empty.html": "",
            "multi_body.html": "<body>foo</body><body>bar</body>",
        }
    )
    def test_serves_modified_html(self, site_dir):
        with testing_server(site_dir) as server:
            headers, output = do_request(server, "GET /normal.html")
            self.assertRegex(output, fr"^<html><body>hello{SCRIPT_REGEX}</body></html>$")
            self.assertEqual(headers["content-type"], "text/html")

            _, output = do_request(server, "GET /no_body.html")
            self.assertRegex(output, fr"^<p>hi{SCRIPT_REGEX}$")

            _, output = do_request(server, "GET /empty.html")
            self.assertRegex(output, fr"^{SCRIPT_REGEX}$")

            _, output = do_request(server, "GET /multi_body.html")
            self.assertRegex(output, fr"^<body>foo</body><body>bar{SCRIPT_REGEX}</body>$")

    @tempdir()
    def test_serves_js(self, site_dir):
        with testing_server(site_dir) as server:
            headers, output = do_request(server, "GET /js/livereload.js")
            self.assertIn("function livereload", output)
            self.assertEqual(headers["content-type"], "application/javascript")

    @tempdir()
    def test_serves_polling_instantly(self, site_dir):
        with testing_server(site_dir) as server:
            _, output = do_request(server, "GET /livereload/0/0")
            self.assertTrue(output.isdigit())

    @tempdir()
    @tempdir()
    def test_serves_polling_after_event(self, site_dir, docs_dir):
        with testing_server(site_dir) as server:
            server.watch(docs_dir)
            initial_epoch = server._visible_epoch

            Path(docs_dir, "foo.docs").write_text("b")

            _, output = do_request(server, f"GET /livereload/{initial_epoch}/0")

            self.assertNotEqual(server._visible_epoch, initial_epoch)
            self.assertEqual(output, str(server._visible_epoch))

    @tempdir()
    def test_serves_polling_with_timeout(self, site_dir):
        with testing_server(site_dir) as server:
            server.poll_response_timeout = 0.2
            initial_epoch = server._visible_epoch

            start_time = time.monotonic()
            _, output = do_request(server, f"GET /livereload/{initial_epoch}/0")
            self.assertGreaterEqual(time.monotonic(), start_time + 0.2)
            self.assertEqual(output, str(initial_epoch))

    @tempdir()
    def test_error_handler(self, site_dir):
        with testing_server(site_dir) as server:
            server.error_handler = lambda code: b"[%d]" % code
            with self.assertLogs("mkdocs.livereload") as cm:
                _, output = do_request(server, "GET /missing")

            self.assertEqual(output, "[404]")
            self.assertEqual(
                cm.output, ['WARNING:mkdocs.livereload:"GET /missing HTTP/1.1" code 404']
            )

    @tempdir()
    def test_bad_error_handler(self, site_dir):
        self.maxDiff = None
        with testing_server(site_dir) as server:
            server.error_handler = lambda code: 0 / 0
            with self.assertLogs("mkdocs.livereload") as cm:
                _, output = do_request(server, "GET /missing")

            self.assertIn("404", output)
            self.assertRegex(
                "\n".join(cm.output), r"Failed to render an error message[\s\S]+/missing.+code 404"
            )
