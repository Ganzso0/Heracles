from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

EXTENSIONS = {
    ".pdf",
    ".docx"
}


def main():

    if not RESULTS_DIR.exists():
        print("❌ No existe la carpeta results/")
        return

    deleted = 0

    for folder in RESULTS_DIR.iterdir():

        if not folder.is_dir():
            continue

        for file in folder.iterdir():

            if not file.is_file():
                continue

            if file.suffix.lower() not in EXTENSIONS:
                continue

            print(f"🗑️ {file}")

            file.unlink()

            deleted += 1

    print()
    print("==============================")
    print("LIMPIEZA COMPLETADA")
    print("==============================")
    print(f"Archivos eliminados: {deleted}")


if __name__ == "__main__":
    main()