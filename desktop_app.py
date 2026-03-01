from __future__ import annotations

import http.client
import logging
import os
import shlex
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from dataclasses import dataclass

if sys.platform.startswith("linux"):
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
    os.environ.setdefault("QT_LOGGING_RULES", "qt.webenginecontext.debug=false")

try:
    import webview  # type: ignore
except Exception:
    webview = None


@dataclass(frozen=True)
class AppConfig:
    title: str = "Job Search Tracker Dashboard"
    host: str = "127.0.0.1"
    port: int = 8501
    app_path: str = "app.py"
    startup_timeout_seconds: int = 45
    poll_interval_seconds: float = 0.2
    browser_probe_timeout_seconds: float = 2.0
    window_width: int = 1280
    window_height: int = 800
    healthcheck_path: str = "/_stcore/health"

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class StreamlitServer:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._process: subprocess.Popen | None = None

    def start(self) -> None:
        if self._process is not None and self._process.poll() is None:
            return

        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            self._config.app_path,
            "--server.headless",
            "true",
            "--server.address",
            self._config.host,
            "--server.port",
            str(self._config.port),
        ]

        self._process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def wait_until_ready(self) -> None:
        deadline = time.time() + self._config.startup_timeout_seconds

        while time.time() < deadline:
            if self._process is not None and self._process.poll() is not None:
                if self._is_service_ready(self._config.host, self._config.port):
                    return
                raise RuntimeError("Streamlit process exited before startup completed")

            if self._is_service_ready(self._config.host, self._config.port):
                return

            time.sleep(self._config.poll_interval_seconds)

        raise TimeoutError("Streamlit server startup timed out")

    def wait_until_stopped(self) -> None:
        if self._process is None:
            return

        while self._process.poll() is None:
            time.sleep(0.5)

    def stop(self) -> None:
        if self._process is None:
            return

        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=5)

    def _is_service_ready(self, host: str, port: int) -> bool:
        if not self._is_port_open(host, port):
            return False

        return self._is_http_ready(host, port)

    def _is_http_ready(self, host: str, port: int) -> bool:
        connection = http.client.HTTPConnection(host=host, port=port, timeout=1)

        try:
            connection.request("GET", self._config.healthcheck_path)
            response = connection.getresponse()
            response.read()
            return 200 <= response.status < 300
        except (OSError, http.client.HTTPException):
            return False
        finally:
            connection.close()

    @staticmethod
    def _is_port_open(host: str, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(1)
                return client.connect_ex((host, port)) == 0
        except OSError:
            return False


class BrowserLauncher:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def launch(self, url: str) -> None:
        for base_command in self._candidate_commands():
            if self._launch_with_command(base_command, url):
                return

        if webbrowser.open(url, new=2):
            return

        raise RuntimeError(f"Failed to open browser for {url}")

    def _candidate_commands(self) -> list[list[str]]:
        commands: list[list[str]] = []

        browser_env = os.getenv("BROWSER", "").strip()
        if browser_env:
            for entry in browser_env.split(os.pathsep):
                parsed = shlex.split(entry.strip())
                if parsed:
                    commands.append(parsed)

        if sys.platform.startswith("linux"):
            commands.extend([
                ["xdg-open"],
                ["gio", "open"],
                ["sensible-browser"],
            ])
        elif sys.platform == "darwin":
            commands.append(["open"])
        elif os.name == "nt":
            commands.append(["cmd", "/c", "start", ""])

        deduplicated: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for command in commands:
            key = tuple(command)
            if key not in seen:
                seen.add(key)
                deduplicated.append(command)

        return deduplicated

    def _launch_with_command(self, base_command: list[str], url: str) -> bool:
        executable = base_command[0]
        if os.path.sep not in executable and shutil.which(executable) is None:
            return False

        command = self._build_command(base_command, url)

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError:
            return False

        try:
            exit_code = process.wait(timeout=self._config.browser_probe_timeout_seconds)
            return exit_code == 0
        except subprocess.TimeoutExpired:
            return True

    @staticmethod
    def _build_command(base_command: list[str], url: str) -> list[str]:
        if any("%s" in token for token in base_command):
            return [token.replace("%s", url) for token in base_command]
        return [*base_command, url]


class DesktopLauncher:
    def __init__(self, config: AppConfig, browser_launcher: BrowserLauncher | None = None) -> None:
        self._config = config
        self._browser_launcher = browser_launcher or BrowserLauncher(config)

    def launch(self, server: StreamlitServer) -> None:
        server.start()
        server.wait_until_ready()

        if self._launch_webview():
            return

        self._browser_launcher.launch(self._config.url)
        server.wait_until_stopped()

    def _launch_webview(self) -> bool:
        if webview is None:
            return False

        try:
            webview.create_window(
                self._config.title,
                self._config.url,
                width=self._config.window_width,
                height=self._config.window_height,
            )
            webview.start(debug=False)
            return True
        except Exception as exc:
            logging.warning(str(exc))
            return False


def main() -> None:
    logging.basicConfig(level=logging.ERROR)
    config = AppConfig()
    server = StreamlitServer(config)
    launcher = DesktopLauncher(config)

    try:
        launcher.launch(server)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logging.error(str(exc))
        sys.exit(1)
    finally:
        server.stop()


if __name__ == "__main__":
    main()
