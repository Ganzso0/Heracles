import json
from pathlib import Path

from database.database import JobDatabase
from cv.cv_adapter import adapt_cv
from cv.cv_renderer import generate_cv


BASE_DIR = Path(__file__).resolve().parent

RESULTS_DIR = BASE_DIR / "results"
PROFILE_FILE = BASE_DIR / "profile" / "master_profile.json"
INDEX_FILE = RESULTS_DIR / "index.json"


def find_result_folders():
    """
    Obtiene las carpetas de resultados y las ordena por número.
    """

    folders = []

    for path in RESULTS_DIR.iterdir():

        if not path.is_dir():
            continue

        try:
            number = int(
                path.name.split("_", 1)[0]
            )
        except (ValueError, IndexError):
            continue

        folders.append(
            (number, path)
        )

    folders.sort(
        key=lambda item: item[0]
    )

    return folders


def load_index():
    """
    Carga results/index.json.

    El index tiene esta estructura:

    {
        "url": {
            "title": "...",
            "company": "...",
            "folder": "...",
            "cv": "..."
        }
    }
    """

    if not INDEX_FILE.exists():

        raise FileNotFoundError(
            f"No existe {INDEX_FILE}"
        )

    with open(
        INDEX_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_folder_mapping(index):
    """
    Construye:

        carpeta -> URL

    utilizando index.json.
    """

    mapping = {}

    for url, data in index.items():

        folder = data.get("folder")

        if not folder:
            continue

        if folder in mapping:

            raise ValueError(
                f"La carpeta {folder} aparece "
                f"más de una vez en index.json."
            )

        mapping[folder] = url

    return mapping


def find_job_by_url(jobs_by_url, url):
    """
    Busca una oferta mediante su URL.
    """

    return jobs_by_url.get(url)


def clear_cv_files(folder):
    """
    Elimina únicamente los CV anteriores.

    NO elimina:
    - link.txt
    - la carpeta
    - index.json
    """

    files_to_remove = [
        folder / "CV_Gonzalo_Vega_Ramos.docx",
        folder / "CV_Gonzalo_Vega_Ramos.pdf"
    ]

    for file in files_to_remove:

        if file.exists():

            print(
                f"   🗑️ Eliminando: {file.name}"
            )

            file.unlink()


def save_offer_link(folder, url):
    """
    Guarda la URL correcta en link.txt.
    """

    link_file = folder / "link.txt"

    with open(
        link_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(url)


def main():

    print()
    print("========================================")
    print(" REGENERACIÓN DE CV")
    print("========================================")
    print()

    # --------------------------------------------------
    # Perfil
    # --------------------------------------------------

    print(
        "Cargando perfil del candidato..."
    )

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        candidate_profile = json.load(file)

    print(
        "✅ Perfil cargado"
    )

    # --------------------------------------------------
    # Index
    # --------------------------------------------------

    print()
    print(
        "Cargando index.json..."
    )

    index = load_index()

    print(
        f"✅ Entradas en index.json: {len(index)}"
    )

    folder_mapping = build_folder_mapping(
        index
    )

    # --------------------------------------------------
    # Base de datos
    # --------------------------------------------------

    db = JobDatabase()

    try:

        print()
        print(
            "Buscando ofertas ACCEPTED..."
        )

        jobs = db.get_jobs(
            status="ACCEPTED"
        )

        print(
            f"✅ Ofertas ACCEPTED encontradas: "
            f"{len(jobs)}"
        )

        # --------------------------------------------------
        # Crear índice URL -> job
        # --------------------------------------------------

        jobs_by_url = {}

        for job in jobs:

            url = job.get("url")

            if not url:
                continue

            if url in jobs_by_url:

                print()
                print(
                    "⚠️ URL duplicada en jobs:"
                )

                print(
                    f"   DB ID anterior: "
                    f"{jobs_by_url[url]['id']}"
                )

                print(
                    f"   DB ID actual: "
                    f"{job['id']}"
                )

            jobs_by_url[url] = job

        # --------------------------------------------------
        # Carpetas
        # --------------------------------------------------

        folders = find_result_folders()

        print()
        print(
            f"📁 Carpetas encontradas: "
            f"{len(folders)}"
        )

        # --------------------------------------------------
        # Comprobar estructura
        # --------------------------------------------------

        if len(folders) != len(index):

            print()
            print(
                "❌ ERROR"
            )

            print(
                f"Carpetas: {len(folders)}"
            )

            print(
                f"Entradas index.json: {len(index)}"
            )

            print(
                "No se generará ningún CV."
            )

            return

        # --------------------------------------------------
        # Construir correspondencias
        # --------------------------------------------------

        print()
        print("========================================")
        print(" COMPROBANDO CORRESPONDENCIAS")
        print("========================================")
        print()

        mappings = []
        errors = []

        for number, folder in folders:

            # ------------------------------------------
            # Buscar URL en index.json
            # ------------------------------------------

            url = folder_mapping.get(
                folder.name
            )

            if not url:

                errors.append(
                    f"{folder.name}: "
                    "no aparece en index.json"
                )

                print(
                    f"❌ {folder.name}"
                )

                print(
                    "   No aparece en index.json"
                )

                continue

            # ------------------------------------------
            # Buscar job en SQLite
            # ------------------------------------------

            job = find_job_by_url(
                jobs_by_url,
                url
            )

            if job is None:

                errors.append(
                    f"{folder.name}: "
                    "URL no encontrada en jobs"
                )

                print(
                    f"❌ {folder.name}"
                )

                print(
                    f"   URL: {url}"
                )

                print(
                    "   No encontrada en jobs"
                )

                continue

            mappings.append(
                (
                    number,
                    folder,
                    job,
                    url
                )
            )

            print(
                f"✅ {number:03d} → "
                f"DB ID {job['id']} → "
                f"{job['title']} → "
                f"{job['company']}"
            )

        # --------------------------------------------------
        # Detectar ofertas ACCEPTED sin carpeta
        # --------------------------------------------------

        mapped_job_ids = {
            job["id"]
            for _, _, job, _ in mappings
        }

        missing_jobs = [
            job
            for job in jobs
            if job["id"] not in mapped_job_ids
        ]

        if missing_jobs:

            print()
            print(
                "⚠️ Ofertas ACCEPTED sin carpeta:"
            )

            for job in missing_jobs:

                print(
                    f"   DB ID {job['id']} → "
                    f"{job['title']}"
                )

        # --------------------------------------------------
        # Si hay errores NO generar
        # --------------------------------------------------

        if errors or missing_jobs:

            print()
            print("========================================")
            print(" ❌ NO SE GENERARÁN LOS CV")
            print("========================================")
            print()

            print(
                f"Correspondencias correctas: "
                f"{len(mappings)}"
            )

            print(
                f"Errores: {len(errors)}"
            )

            print(
                f"Ofertas sin carpeta: "
                f"{len(missing_jobs)}"
            )

            print()
            print(
                "Corrige las correspondencias "
                "antes de continuar."
            )

            return

        # --------------------------------------------------
        # Mostrar correspondencia final
        # --------------------------------------------------

        print()
        print("========================================")
        print(" CORRESPONDENCIA FINAL")
        print("========================================")
        print()

        for number, folder, job, url in mappings:

            print(
                f"{number:03d} → "
                f"DB ID {job['id']} → "
                f"{job['title']} → "
                f"{job['company']}"
            )

        # --------------------------------------------------
        # Inicio
        # --------------------------------------------------

        print()
        print("========================================")
        print(" INICIO DE REGENERACIÓN")
        print("========================================")
        print()

        successful = 0
        failed = 0

        # --------------------------------------------------
        # Generación
        # --------------------------------------------------

        for index_number, (
            number,
            folder,
            job,
            url
        ) in enumerate(
            mappings,
            start=1
        ):

            print()
            print("----------------------------------------")

            print(
                f"[{index_number:03d}/{len(mappings):03d}] "
                f"{job['title']}"
            )

            print(
                f"DB ID: {job['id']}"
            )

            print(
                f"Empresa: {job['company']}"
            )

            print(
                f"Carpeta: {folder.name}"
            )

            print("----------------------------------------")

            try:

                # ------------------------------------------
                # job_profile
                # ------------------------------------------

                if not job.get(
                    "job_profile"
                ):

                    raise ValueError(
                        "La oferta no tiene "
                        "job_profile almacenado."
                    )

                job_profile = json.loads(
                    job["job_profile"]
                )

                # ------------------------------------------
                # match_result
                # ------------------------------------------

                if job.get(
                    "match_result"
                ):

                    match_result = json.loads(
                        job["match_result"]
                    )

                else:

                    match_result = {}

                # ------------------------------------------
                # Limpiar CV anterior
                # ------------------------------------------

                clear_cv_files(
                    folder
                )

                # ------------------------------------------
                # Restaurar link.txt correcto
                # ------------------------------------------

                save_offer_link(
                    folder,
                    url
                )

                print(
                    "🔗 Link restaurado"
                )

                # ------------------------------------------
                # CV Adapter
                # ------------------------------------------

                print(
                    "🤖 Ejecutando CV Adapter..."
                )

                adapted_profile = adapt_cv(
                    job_profile,
                    candidate_profile
                )

                print(
                    "✅ CV Adapter completado"
                )

                # ------------------------------------------
                # Renderer
                # ------------------------------------------

                print(
                    "📄 Generando DOCX + PDF..."
                )

                generated_files = generate_cv(
                    profile=candidate_profile,
                    adapted=adapted_profile,
                    job=job,
                    match=match_result,
                    output_dir=folder
                )

                print(
                    "✅ CV generado"
                )

                print(
                    f"   DOCX: "
                    f"{generated_files['docx']}"
                )

                print(
                    f"   PDF: "
                    f"{generated_files['pdf']}"
                )

                successful += 1

            except Exception as error:

                failed += 1

                print()
                print(
                    "❌ ERROR"
                )

                print(
                    str(error)
                )

                print(
                    "La siguiente oferta continuará normalmente."
                )

        # --------------------------------------------------
        # Resultado
        # --------------------------------------------------

        print()
        print()
        print("========================================")
        print(" REGENERACIÓN FINALIZADA")
        print("========================================")
        print()

        print(
            f"✅ Generados correctamente: "
            f"{successful}"
        )

        print(
            f"❌ Errores: {failed}"
        )

        print(
            f"📦 Total: {len(mappings)}"
        )

        print()

    finally:

        db.close()


if __name__ == "__main__":
    main()