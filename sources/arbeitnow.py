import time
import requests

from sources.base_source import JobSource


class ArbeitnowSource(JobSource):

    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self):
        self.page_cache = {}

    def search_jobs(
        self,
        keyword: str,
        location: str,
        page: int = 1
    ) -> list[dict]:

        jobs = self._get_page(page)

        keyword_lower = keyword.lower()
        location_lower = location.lower()

        filtered_jobs = []

        for job in jobs:

            title = job.get("title") or ""
            description = job.get("description") or ""
            job_location = job.get("location") or ""

            search_text = (
                f"{title} "
                f"{description}"
            ).lower()

            # Keyword
            if keyword_lower not in search_text:
                continue

            # Location
            if location_lower not in job_location.lower():
                continue

            filtered_jobs.append({
                "external_id": str(job.get("slug")),
                "source": "arbeitnow",
                "title": title,
                "company": job.get("company_name"),
                "location": job_location,
                "description": description,
                "url": job.get("url"),
                "published_at": job.get("created_at")
            })

        return filtered_jobs

    def _get_page(self, page: int) -> list[dict]:

        if page in self.page_cache:
            return self.page_cache[page]

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = requests.get(
                    self.BASE_URL,
                    params={"page": page},
                    timeout=30
                )

                response.raise_for_status()

                data = response.json()

                jobs = data.get("data", [])

                self.page_cache[page] = jobs

                return jobs

            except requests.RequestException:

                if attempt == max_retries - 1:
                    raise

                print(
                    f"Arbeitnow error "
                    f"(página {page}, "
                    f"intento {attempt + 1}/{max_retries}). "
                    f"Reintentando..."
                )

                time.sleep(2 ** attempt)

        return []