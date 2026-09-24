import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
INDEX_FILE = RESULTS_DIR / "index.json"


def build_index():

    index = {}

    if not RESULTS_DIR.exists():
        print("❌ No existe la carpeta results/")
        return

    for folder in RESULTS_DIR.iterdir():

        if not folder.is_dir():
            continue

        link_file = folder / "link.txt"
        pdf_file = folder / "CV_Gonzalo_Vega_Ramos.pdf"

        if not link_file.exists():
            continue

        if not pdf_file.exists():
            continue

        with open(
            link_file,
            "r",
            encoding="utf-8"
        ) as file:

            url = file.read().strip()

        if not url:
            continue

        parts = folder.name.split("_", 1)

        if len(parts) == 2:
            folder_name = parts[1]
        else:
            folder_name = folder.name

        index[url] = {
            "title": folder_name,
            "company": "",
            "folder": folder.name,
            "cv": str(
                folder.relative_to(BASE_DIR) /
                pdf_file.name
            ).replace("\\", "/")
        }

    with open(
        INDEX_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            index,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"✅ Index generado: {INDEX_FILE}"
    )

    print(
        f"📄 CVs encontrados: {len(index)}"
    )


if __name__ == "__main__":
    build_index()