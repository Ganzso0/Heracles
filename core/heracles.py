import json

from database.database import JobDatabase
from sources.source_manager import SourceManager
from core.job_processor import JobProcessor


class Heracles:

    def __init__(
        self,
        config_file,
        profile_file,
        llm_manager
    ):

        self.llm_manager = llm_manager

        # ==============================
        # CONFIGURACIÓN
        # ==============================

        with open(
            config_file,
            "r",
            encoding="utf-8"
        ) as file:
            self.config = json.load(file)

        # ==============================
        # PERFIL
        # ==============================

        with open(
            profile_file,
            "r",
            encoding="utf-8"
        ) as file:
            self.candidate_profile = json.load(file)

        # ==============================
        # DATABASE
        # ==============================

        self.db = JobDatabase()

        # ==============================
        # SOURCE MANAGER
        # ==============================

        self.source_manager = SourceManager(
            self.config,
            self.db
        )

        # ==============================
        # JOB PROCESSOR
        # ==============================

        self.job_processor = JobProcessor(
            config=self.config,
            candidate_profile=self.candidate_profile,
            db=self.db,
            llm_manager=self.llm_manager
        )

    def run(self):

        try:

            # ==============================
            # BÚSQUEDA
            # ==============================

            print()
            print("==============================")
            print("BUSCANDO OFERTAS")
            print("==============================")

            new_jobs = self.source_manager.search_all()

            print(
                "Ofertas nuevas encontradas:",
                len(new_jobs)
            )

            # ==============================
            # PROCESAMIENTO
            # ==============================

            jobs = self.db.get_jobs_by_statuses([
    "NEW",
    "ERROR"
])

            print()
            print("==============================")
            print("PROCESANDO OFERTAS")
            print("==============================")

            print(
                "Ofertas nuevas:",
                len(jobs)
            )

            for job in jobs:

                self.job_processor.process(job)

        finally:

            self.db.close()