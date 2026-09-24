from sources.adzuna_source import AdzunaSource
from database.database import JobDatabase


class SourceManager:

    def __init__(self, config: dict, database: JobDatabase):

        self.config = config
        self.database = database

        self.sources = []

        self._load_sources()

    def _load_sources(self):

        sources_config = self.config["sources"]

        adzuna_config = sources_config.get("adzuna")

        if adzuna_config and adzuna_config.get("enabled", False):

            adzuna = AdzunaSource(
                app_id=adzuna_config["app_id"],
                app_key=adzuna_config["app_key"],
                country=adzuna_config.get("country", "es")
            )

            self.sources.append(adzuna)

    def search_all(self) -> list[dict]:

        search_config = self.config["search"]

        keywords = search_config["keywords"]
        locations = search_config["locations"]

        all_jobs = []

        for source in self.sources:

            for location in locations:

                for keyword in keywords:

                    print(
                        f"Buscando: '{keyword}' "
                        f"en '{location}'"
                    )

                    jobs = source.search_jobs(
                        keyword=keyword,
                        location=location,
                        page=1
                    )

                    all_jobs.extend(jobs)

        unique_jobs = self._deduplicate(all_jobs)

        new_jobs = []

        for job in unique_jobs:

            if self.database.exists(
                job["source"],
                job["external_id"]
            ):
                continue

            self.database.add_job(job)

            new_jobs.append(job)

        return new_jobs

    def _deduplicate(
        self,
        jobs: list[dict]
    ) -> list[dict]:

        unique_jobs = {}

        for job in jobs:

            key = (
                job["source"],
                job["external_id"]
            )

            if key not in unique_jobs:

                unique_jobs[key] = job

        return list(unique_jobs.values())