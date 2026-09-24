import time
import requests

from sources.base_source import JobSource


class JoobleSource(JobSource):

    BASE_URL = "https://es.jooble.org/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_jobs(
        self,
        keyword: str,
        location: str,
        page: int = 1
    ) -> list[dict]:

        url = f"{self.BASE_URL}/{self.api_key}"

        payload = {
            "keywords": keyword,
            "location": location,
            "radius": "40",
            "page": str(page)
        }

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = requests.post(
                    url,
                    json=payload,
                    timeout=30
                )

                response.raise_for_status()

                data = response.json()

                jobs = []

                for job in data.get("jobs", []):

                    jobs.append({
                        "external_id": str(job.get("id")),
                        "source": "jooble",
                        "title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "description": job.get("snippet"),
                        "url": job.get("link"),
                        "published_at": job.get("updated")
                    })

                return jobs

            except requests.RequestException:

                if attempt == max_retries - 1:
                    raise

                print(
                    f"Jooble error para '{keyword}' "
                    f"(intento {attempt + 1}/{max_retries}). "
                    f"Reintentando..."
                )

                time.sleep(2 ** attempt)

        return []