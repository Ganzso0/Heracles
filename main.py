import json
from pathlib import Path

from database.database import JobDatabase
from sources.source_manager import SourceManager
from analyzer.pre_filter import PreFilter
from analyzer.job_analyzer import analyze_job
from matcher.match_engine import match_job
from cv.cv_adapter import adapt_cv
from cv.cv_renderer import generate_cv
from cv.cover_letter import generate_cover_letter


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
CONFIG_FILE = BASE_DIR / "config" / "config.json"
PROFILE_FILE = BASE_DIR / "profile" / "master_profile.json"
INDEX_FILE = RESULTS_DIR / "index.json"


def create_result_directory(job):

    title = job["title"] or "Sin_titulo"
    company = job["company"] or "Sin_empresa"

    invalid_chars = '<>:"/\\|?*'

    folder_name = f"{title}_{company}"

    for char in invalid_chars:
        folder_name = folder_name.replace(char, "_")

    folder_name = folder_name.replace(" ", "_")
    folder_name = folder_name[:120]

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    existing = [
        path
        for path in RESULTS_DIR.iterdir()
        if path.is_dir()
    ]

    number = len(existing) + 1

    output_dir = (
        RESULTS_DIR /
        f"{number:03d}_{folder_name}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return output_dir


def save_offer_link(output_dir, job):

    with open(
        output_dir / "link.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            job["url"]
        )


def main():

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(file)

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        candidate_profile = json.load(file)

    # ==================================================
    # DATABASE
    # ==================================================

    db = JobDatabase()

    # ==================================================
    # SOURCE MANAGER
    # ==================================================

    source_manager = SourceManager(
        config,
        db
    )

    # ==================================================
    # PRE-FILTER
    # ==================================================

    prefilter = PreFilter({})

    try:

        # ==================================================
        # BÚSQUEDA
        # ==================================================

        print()
        print("==============================")
        print("BUSCANDO OFERTAS")
        print("==============================")

        new_jobs = source_manager.search_all()

        print(
            "Ofertas nuevas encontradas:",
            len(new_jobs)
        )

        # ==================================================
        # PROCESAMIENTO
        # ==================================================

        jobs = db.get_jobs("NEW")

        print()
        print("==============================")
        print("PROCESANDO OFERTAS")
        print("==============================")

        print(
            "Ofertas nuevas:",
            len(jobs)
        )

        for job in jobs:

            print()
            print("------------------------------")
            print("ID:", job["id"])
            print("Título:", job["title"])
            print("Empresa:", job["company"])

            try:

                # ==========================================
                # PRE-FILTER
                # ==========================================

                if not prefilter.check(job):

                    print(
                        "❌ Descartada por PreFilter"
                    )

                    db.update_status(
                        source=job["source"],
                        external_id=job["external_id"],
                        status="PREFILTER_REJECTED"
                    )

                    continue

                print("✅ Pasa PreFilter")

                # ==========================================
                # JOB ANALYZER
                # ==========================================

                print(
                    "🤖 Analizando oferta..."
                )

                job_text = f"""
TÍTULO:
{job["title"]}

EMPRESA:
{job["company"]}

UBICACIÓN:
{job["location"]}

DESCRIPCIÓN:
{job["description"]}
"""

                job_profile = analyze_job(
                    job_text
                )

                print(
                    "✅ JobAnalyzer completado"
                )

                db.update_analysis(
                    source=job["source"],
                    external_id=job["external_id"],
                    job_profile=json.dumps(
                        job_profile,
                        ensure_ascii=False
                    ),
                    status="ANALYZED"
                )

                # ==========================================
                # MATCH ENGINE
                # ==========================================

                print(
                    "📊 Calculando compatibilidad..."
                )

                match_result = match_job(
                    job_profile,
                    candidate_profile
                )

                summary = match_result["summary"]

                match_percentage = summary[
                    "match_percentage"
                ]

                # ==========================================
                # RECHAZADA
                # ==========================================

                if match_percentage < 80:

                    status = "REJECTED"

                    print(
                        "❌ Oferta rechazada:",
                        match_percentage,
                        "%"
                    )

                    db.update_analysis(
                        source=job["source"],
                        external_id=job["external_id"],
                        job_profile=json.dumps(
                            job_profile,
                            ensure_ascii=False
                        ),
                        match_result=json.dumps(
                            match_result,
                            ensure_ascii=False
                        ),
                        match_percentage=match_percentage,
                        status=status,
                        error=None
                    )

                    continue

                # ==========================================
                # ACEPTADA
                # ==========================================

                status = "ACCEPTED"

                print(
                    "✅ Oferta aceptada:",
                    match_percentage,
                    "%"
                )

                db.update_analysis(
                    source=job["source"],
                    external_id=job["external_id"],
                    job_profile=json.dumps(
                        job_profile,
                        ensure_ascii=False
                    ),
                    match_result=json.dumps(
                        match_result,
                        ensure_ascii=False
                    ),
                    match_percentage=match_percentage,
                    status=status,
                    error=None
                )

                # ==========================================
                # CV ADAPTER
                # ==========================================

                print(
                    "📝 Adaptando CV..."
                )

                adapted_profile = adapt_cv(
                    job_profile,
                    candidate_profile
                )

                print(
                    "✅ CV adaptado"
                )

                # ==========================================
                # RESULT DIRECTORY
                # ==========================================

                output_dir = create_result_directory(
                    job
                )

                print(
                    "📁 Carpeta:",
                    output_dir
                )

                # ==========================================
                # LINK
                # ==========================================

                save_offer_link(
                    output_dir,
                    job
                )

                # ==========================================
                # CV RENDERER
                # ==========================================

                print(
                    "📄 Generando CV..."
                )

                generate_cv(
                    profile=candidate_profile,
                    adapted=adapted_profile,
                    job=job,
                    match=match_result,
                    output_dir=output_dir
                )

                update_cv_index(
                    job,
                    output_dir
                )

                print(
                    "✅ CV generado"
                )

                print("✉️ Generando carta de presentación...")

                cover_letter = generate_cover_letter(
                    job_profile=job_profile,
                    candidate_profile=candidate_profile,
                    match_result=match_result
                )

                with open(output_dir / "carta_presentacion.txt", "w", encoding="utf-8") as file:
                    file.write(cover_letter)

                print("✅ Carta de presentación generada")

                # ==========================================
                # FINAL
                # ==========================================

                print()
                print("==============================")
                print("OFERTA COMPLETADA")
                print("==============================")

                print(
                    "Match:",
                    match_percentage,
                    "%"
                )

                print(
                    "Resultado:",
                    output_dir
                )

            except Exception as error:

                print()
                print(
                    "❌ ERROR PROCESANDO OFERTA"
                )

                print(
                    error
                )

                db.update_status(
                    source=job["source"],
                    external_id=job["external_id"],
                    status="ERROR",
                    error=str(error)
                )

    finally:

        db.close()

def update_cv_index(job, output_dir):
    index = {}

    if INDEX_FILE.exists():
        with open(
            INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            index = json.load(file)

    relative_path = output_dir.relative_to(BASE_DIR)

    index[job["url"]] = {
        "title": job["title"],
        "company": job["company"],
        "folder": output_dir.name,
        "cv": str(
            relative_path /
            "CV_Gonzalo_Vega_Ramos.pdf"
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


if __name__ == "__main__":
    main()