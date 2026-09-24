import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
INDEX_FILE = RESULTS_DIR / "index.json"


class CVHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # ==========================================
        # API
        # ==========================================

        if parsed.path == "/api/find":

            params = parse_qs(parsed.query)
            url = params.get("url", [None])[0]

            if not url:
                self.send_json({
                    "found": False,
                    "error": "URL no proporcionada"
                })
                return

            if not INDEX_FILE.exists():

                self.send_json({
                    "found": False
                })

                return

            with open(
                INDEX_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                index = json.load(file)

            result = index.get(url)

            if not result:

                self.send_json({
                    "found": False
                })

                return

            self.send_json({
                "found": True,
                **result
            })

            return

        # ==========================================
        # ARCHIVOS DE RESULTS
        # ==========================================

        if parsed.path.startswith("/results/"):

            relative_path = unquote(
                parsed.path
            ).lstrip("/")

            file_path = BASE_DIR / relative_path

            try:
                file_path = file_path.resolve()
                results_root = RESULTS_DIR.resolve()

                file_path.relative_to(results_root)

            except ValueError:

                self.send_error(
                    403,
                    "Acceso denegado"
                )

                return

            if file_path.exists() and file_path.is_file():

                self.send_response(200)

                if file_path.suffix.lower() == ".pdf":
                    self.send_header(
                        "Content-Type",
                        "application/pdf"
                    )

                else:
                    self.send_header(
                        "Content-Type",
                        "application/octet-stream"
                    )

                self.end_headers()

                with open(
                    file_path,
                    "rb"
                ) as file:

                    self.wfile.write(
                        file.read()
                    )

                return

        self.send_error(
            404,
            "No encontrado"
        )

    def send_json(self, data):

        content = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)


def main():

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    server = ThreadingHTTPServer(
        ("127.0.0.1", 8765),
        CVHandler
    )

    print(
        "CV Server activo en http://127.0.0.1:8765"
    )

    print(
        "Pulsa Ctrl+C para detenerlo."
    )

    server.serve_forever()


if __name__ == "__main__":
    main()