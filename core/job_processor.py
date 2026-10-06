import json

from analyzer.pre_filter import PreFilter

from analyzer.job_analyzer import analyze_job
from matcher.match_engine import match_job
from cv.cv_adapter import adapt_cv
from cv.cv_renderer import generate_cv
from cover_letter import generate_cover_letter

from results.results_manager import (
    create_result_directory,
    save_offer_link,
    update_cv_index
)

from llm.client import LLMClient


class JobProcessor:

    def __init__(
        self,
        config,
        candidate_profile,
        db,
        llm_manager
    ):

        self.config = config
        self.candidate_profile = candidate_profile
        self.db = db

        self.llm_manager = llm_manager
        self.llm_client = LLMClient()

        self.prefilter = PreFilter(
            config.get("prefilter", {})
        )

    def process(self, job):

        print()
        print("------------------------------")
        print("ID:", job["id"])
        print("Título:", job["title"])
        print("Empresa:", job["company"])

        try:

            # ==========================================
            # PRE-FILTER
            # ==========================================

            if not self.prefilter.check(job):

                print(
                    "❌ Descartada por PreFilter"
                )

                self.db.update_status(
                    source=job["source"],
                    external_id=job["external_id"],
                    status="PREFILTER_REJECTED"
                )

                return

            print("✅ Pasa PreFilter")

            # ==========================================
            # ESPERAR AL LLM
            # ==========================================

            self.llm_manager.wait_until_ready()

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
                job_text,
                self.llm_client
            )

            print(
                "✅ JobAnalyzer completado"
            )

            self.db.update_analysis(
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
                self.candidate_profile
            )

            summary = match_result["summary"]

            match_percentage = summary[
                "match_percentage"
            ]

            threshold = self.config.get(
                "match_threshold",
                80
            )

            # ==========================================
            # RECHAZADA
            # ==========================================

            if match_percentage < threshold:

                print(
                    "Oferta RECHAZADA:",
                    match_percentage,
                    "%"
                )

                self.db.update_analysis(
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
                    status="REJECTED",
                    error=None
                )

                return

            # ==========================================
            # ACEPTADA
            # ==========================================

            print(
                "Oferta ACEPTADA:",
                match_percentage,
                "%"
            )

            self.db.update_analysis(
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
                status="ACCEPTED",
                error=None
            )

            # ==========================================
            # CV ADAPTER
            # ==========================================

            print(
                "Adaptando CV..."
            )

            adapted_profile = adapt_cv(
                job_profile,
                self.candidate_profile,
                self.llm_client
            )

            print(
                "CV adaptado"
            )

            # ==========================================
            # RESULT DIRECTORY
            # ==========================================

            output_dir = create_result_directory(
                job
            )

            print(
                "Guardado en:",
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
                "Generando CV..."
            )

            generate_cv(
                profile=self.candidate_profile,
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
                "CV generado"
            )

            # ==========================================
            # COVER LETTER
            # ==========================================

            print(
                "Generando carta de presentación..."
            )

            cover_letter = generate_cover_letter(
                job_profile=job_profile,
                candidate_profile=self.candidate_profile,
                match_result=match_result,
                llm_client=self.llm_client
            )

            with open(
                output_dir / "carta_presentacion.txt",
                "w",
                encoding="utf-8"
            ) as file:

                file.write(cover_letter)

            print(
                "Carta de presentación generada"
            )

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
                "ERROR PROCESANDO OFERTA"
            )

            print(
                error
            )

            self.db.update_status(
                source=job["source"],
                external_id=job["external_id"],
                status="ERROR",
                error=str(error)
            )