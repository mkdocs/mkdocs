from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen
from tempfile import TemporaryDirectory
from time import sleep


@dataclass
class Sample_Repository:
    handler: TemporaryDirectory
    site_dir: str
    signature: str

    def __del__(self):
        self.handler.cleanup()


class shutdown_by_signal_tests(unittest.TestCase):
    SLEEPING_TIME_WAITING_FOR_START = 2
    SLEEPING_TIME_WAITING_FOR_SHUTDOWN = 2
    SLEEPING_TIME_WAITING_FOR_PROCESS = 6
    TRIES_TO_CHECK_FOR_DIRECTORY_CLEANUP = 4

    def _create_sample_repository(self) -> Sample_Repository:
        from os import mkdir
        from uuid import uuid4

        from yaml import dump

        handler = TemporaryDirectory(prefix='mkdocs_test-')
        site_dir = handler.name

        signature = uuid4().hex

        configuration = {'site_name': 'Testing case', 'docs_dir': 'docs'}

        docs_dir = f"{site_dir}/{configuration.get('docs_dir')}"
        mkdir(docs_dir)

        Path(site_dir, "mkdocs.yml").write_text(dump(configuration))
        Path(docs_dir, "index.md").write_text("# Index File")
        Path(docs_dir, "signature.md").write_text(f"# {signature} ")

        return Sample_Repository(
            handler=handler,
            site_dir=site_dir,
            signature=signature,
        )

    def _execute_mkdocs_as_liveserver(self, site_dir: str) -> Popen:
        from os import chdir, getcwd
        from sys import platform

        current_working_dir = getcwd()
        chdir(site_dir)

        if platform == "linux":
            from errno import EADDRINUSE
            from socket import AF_INET, SOCK_STREAM, socket
            from subprocess import DEVNULL

            port_testing = socket(AF_INET, SOCK_STREAM)

            try:
                port_testing.bind(("127.0.0.1", 8000))
            except OSError as exception:
                if exception.errno == EADDRINUSE:
                    Popen('killall mkdocs'.split(' ')).wait(
                        timeout=self.SLEEPING_TIME_WAITING_FOR_PROCESS
                    )

            port_testing.close()

        mkdocs = Popen('mkdocs serve'.split(' '), stdout=DEVNULL, stderr=DEVNULL, shell=False)
        sleep(self.SLEEPING_TIME_WAITING_FOR_START)

        chdir(current_working_dir)

        return mkdocs

    def _locate_mkdocs_directory(self, signature: str) -> Path | None:
        from pathlib import Path
        from tempfile import TemporaryDirectory

        temporary_directory_probe = TemporaryDirectory()
        temporary_directory = Path(f"{temporary_directory_probe.name}").parent

        for mkdocs_temporary_directory in temporary_directory.glob('mkdocs_*'):
            mkdocs_temporary_path = Path(mkdocs_temporary_directory)
            mkdocs_signature_path = Path(f"{mkdocs_temporary_path}/signature/index.html")

            if not mkdocs_temporary_path.exists():
                continue

            if not mkdocs_temporary_path.is_dir():
                continue

            if not mkdocs_signature_path.exists():
                continue

            with mkdocs_signature_path.open('r') as fp:
                signature_found = fp.read()

            if signature_found.find(signature) == -1:
                continue

            temporary_directory_probe.cleanup()

            return mkdocs_temporary_path

        return None

    def _is_active(self, mkdocs: Popen) -> bool:
        from errno import ESRCH
        from os import kill
        from signal import SIG_BLOCK

        if mkdocs.returncode is not None:
            return False

        try:
            kill(mkdocs.pid, SIG_BLOCK)
        except OSError as exception:
            if exception.errno == ESRCH:
                return True

        return False

    def _wait_for_shutdown(self, mkdocs: Popen, signal: int):
        from os import kill

        kill(mkdocs.pid, signal)

        while self._is_active(mkdocs):
            sleep(self.SLEEPING_TIME_WAITING_FOR_SHUTDOWN)

    def _was_directory_cleaned(self, path: Path) -> bool:
        for _ in range(self.TRIES_TO_CHECK_FOR_DIRECTORY_CLEANUP):
            if not path.exists():
                return True

            sleep(self.SLEEPING_TIME_WAITING_FOR_PROCESS)

        return False

    def test_shutdown_with_signal(self):
        from signal import SIGINT, SIGTERM, strsignal

        repository = self._create_sample_repository()

        for signal in [SIGINT, SIGTERM]:
            mkdocs = self._execute_mkdocs_as_liveserver(repository.site_dir)
            mkdocs_temporary_path = self._locate_mkdocs_directory(signature=repository.signature)

            self.assertTrue(
                mkdocs_temporary_path is not None, "Unable to locate the live server directory"
            )

            self._wait_for_shutdown(mkdocs, signal)

            was_cleaned = self._was_directory_cleaned(mkdocs_temporary_path)

            self.assertTrue(
                was_cleaned,
                f"The Mkdocs '{mkdocs_temporary_path}' was not cleaned "
                f"with signal '{strsignal(signal)}'",
            )

            # This is a flaw in 'liveserver' shutdown process
            # it seems mkdocs become zombie when testing.
            while mkdocs.returncode is None:
                mkdocs.wait(timeout=self.SLEEPING_TIME_WAITING_FOR_PROCESS)

            del mkdocs

        del repository


if __name__ == '__main__':
    shutdown_by_signal_tests()
