class PreFilter:

    def __init__(self, profile: dict):

        self.profile = profile

        # Tecnologías / roles que nos interesa detectar
        self.target_keywords = [
            ".net",
            "c#",
            "asp.net",
            "backend",
            "software engineer",
            "software developer",
            "developer",
            "desarrollador",
            "programador",
            "python",
            "ai engineer",
            "machine learning",
            "data engineer",
            "data scientist",
            "cloud engineer",
            "cloud architect",
            "cloud developer",
            "azure",
            "aws",
            "gcp",
            "devops",
            "docker",
            "kubernetes",
            "microservices",
            "microservicios",
        ]

        # Cosas que podemos descartar con bastante seguridad
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

    def check(self, job: dict) -> bool:

        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()

        text = f"{title} {description}"

        # --------------------------------
        # 1. DESCARTES OBVIOS
        # --------------------------------

        for keyword in self.excluded_keywords:

            if keyword in title:
                return False

        # --------------------------------
        # 2. BUSCAR SEÑALES DE TECNOLOGÍA
        # --------------------------------

        for keyword in self.target_keywords:

            if keyword in text:
                return True

        # --------------------------------
        # 3. SI NO HAY NINGUNA SEÑAL
        # --------------------------------

        return False