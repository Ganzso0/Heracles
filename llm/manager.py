import subprocess
import threading
import time
from pathlib import Path

import requests


class LLMManager:

    def __init__(
        self,
        server_path: Path,
        model_path: Path,
        port: int = 8080
    ):
        self.server_path = server_path
        self.model_path = model_path
        self.port = port

        self.process = None

        self._ready = threading.Event()
        self._thread = None
        self._error = None

    def start(self):

        if self.process is not None:
            return

        command = [
            str(self.server_path),
            "-m",
            str(self.model_path),
            "--port",
            str(self.port),
        ]

        print("🚀 Iniciando servidor LLM...")

        print("Servidor:", self.server_path)
        print("Modelo:", self.model_path)
        print("Servidor existe:", self.server_path.exists())
        print("Modelo existe:", self.model_path.exists())

        self.process = subprocess.Popen(
            command,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        self._wait_until_ready()

        print("✅ Servidor LLM listo")

    def start_background(self):

        if self._thread is not None:
            return

        self._thread = threading.Thread(
            target=self._start_background_worker,
            daemon=True
        )

        self._thread.start()

    def _start_background_worker(self):

        try:

            self.start()

            self._ready.set()

        except Exception as error:

            self._error = error
            self._ready.set()

    def is_ready(self):

        return self._ready.is_set() and self._error is None

    def wait_until_ready(self):

        self._ready.wait()

        if self._error is not None:
            raise self._error

    def _wait_until_ready(self):

        url = f"http://127.0.0.1:{self.port}/health"

        for _ in range(30):

            try:

                response = requests.get(
                    url,
                    timeout=1
                )

                if response.status_code == 200:
                    return

            except requests.RequestException:
                pass

            time.sleep(1)

        self.stop()

        raise RuntimeError(
            "El servidor LLM no respondió a tiempo."
        )

    def stop(self):

        if self.process is None:
            return

        print("🛑 Deteniendo servidor LLM...")

        self.process.terminate()

        try:

            self.process.wait(timeout=5)

        except subprocess.TimeoutExpired:

            self.process.kill()
            self.process.wait()

        self.process = None

        self._ready.clear()

        print("✅ Servidor LLM detenido")