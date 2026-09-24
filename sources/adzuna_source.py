import time
import requests

from sources.base_source import JobSource


class AdzunaSource(JobSource):

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, app_id: str, app_key: str, country: str = "es"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country

    def search_jobs(
        self,
        keyword: str,
        location: str,
        page: int = 1
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/"
            f"{self.country}/search/"
            f"{page}"
        )

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": keyword,
            "where": location,
            "results_per_page": 50
        }

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

                response.raise_for_status()

                data = response.json()

                jobs = []

                for job in data.get("results", []):

                    jobs.append({
                        "external_id": str(job.get("id")),
                        "source": "adzuna",
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("display_name"),
                        "location": job.get("location", {}).get("display_name"),
                        "description": job.get("description"),
                        "url": job.get("redirect_url"),
                        "published_at": job.get("created")
                    })

                return jobs

            except requests.RequestException as e:

                if attempt == max_retries - 1:
                    raise

                print(
                    f"Adzuna error para '{keyword}' "
                    f"(intento {attempt + 1}/{max_retries}). "
                    f"Reintentando..."
                )

                time.sleep(2 ** attempt)

        return []