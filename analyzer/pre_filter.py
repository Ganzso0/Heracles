class PreFilter:
    def __init__(self, profile: dict):
        self.profile = profile

        self.target_keywords = [
            ".net", "c#", "asp.net", "backend", "software engineer",
            "software developer", "developer", "desarrollador",
            "programador", "python", "ai engineer", "machine learning",
            "data engineer", "data scientist", "cloud engineer",
            "cloud architect", "cloud developer", "azure", "aws", "gcp",
            "devops", "docker", "kubernetes", "microservices",
            "microservicios",
        ]

        self.excluded_keywords = [
            "cocinero", "chef de partie", "camarero", "fontanero",
            "carnicero", "cerrajero", "pintor", "montador de ventanas",
            "montador de máquinas", "montador de ventilación",
            "recepcionista", "personal de hotel",
        ]

        self.excluded_domains = [
            "jobleads.com",
        ]

    def check(self, job: dict) -> bool:
        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()
        url = (job.get("url") or "").lower()

        # Fuentes que no queremos
        for domain in self.excluded_domains:
            if domain in url:
                return False

        text = f"{title} {description}"

        for keyword in self.excluded_keywords:
            if keyword in title:
                return False

        for keyword in self.target_keywords:
            if keyword in text:
                return True

        return False