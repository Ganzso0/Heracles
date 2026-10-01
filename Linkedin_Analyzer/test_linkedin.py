import requests

from pathlib import Path


HTML_FILE = Path(__file__).parent / "linkedin.html"

html = HTML_FILE.read_text(
    encoding="utf-8"
)

response = requests.post(
    "http://127.0.0.1:8000/analyze-html",
    json={
        "html": html
    }
)

print(response.status_code)
print(response.json())