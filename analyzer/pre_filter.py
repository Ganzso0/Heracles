class PreFilter:
    def __init__(self, profile: dict):
        self.profile = profile

        self.target_keywords = [
            # Python
            "python",
            "python developer",
            "python backend",
            "fastapi",
            "django",
            "flask",

            # AI / LLM
            "ai engineer",
            "ai developer",
            "ai software engineer",
            "artificial intelligence engineer",
            "artificial intelligence developer",
            "llm engineer",
            "llm developer",
            "generative ai",
            "generative ai engineer",
            "generative ai developer",
            "applied ai",
            "applied ai engineer",
            "rag",
            "rag engineer",
            "retrieval augmented generation",
            "ai agents",
            "llm applications",

            # Machine Learning / NLP
            "machine learning engineer",
            "machine learning developer",
            "nlp engineer",
            "nlp developer",
            "natural language processing",

            # Backend
            "backend developer",
            "backend engineer",
            "software engineer",
            "software developer",
            "developer",
            "desarrollador",
            "programador",

            # .NET / C# — secundarios
            ".net",
            "c#",
            "asp.net",

            # Arquitectura / tecnologías que pueden aparecer
            "microservices",
            "microservicios",
            "rest api",
            "restful api",
            "docker",
        ]

        self.excluded_keywords = [
            "cocinero",
            "chef de partie",
            "camarero",
            "fontanero",
            "carnicero",
            "cerrajero",
            "pintor",
            "montador de ventanas",
            "montador de máquinas",
            "montador de ventilación",
            "recepcionista",
            "personal de hotel",
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

        # Nunca aceptar determinadas profesiones
        for keyword in self.excluded_keywords:
            if keyword in title:
                return False

        text = f"{title} {description}"

        # Debe contener al menos una tecnología/rol objetivo
        for keyword in self.target_keywords:
            if keyword in text:
                return True

        return False