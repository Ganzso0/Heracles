import json
import re


# ============================================================
# CONFIGURACIÓN DEL MATCHER
# ============================================================

ROLE_WEIGHTS = {
    "python_developer": 1.0,
    "ai_engineer": 1.0,
    "ai_developer": 1.0,
    "llm_engineer": 1.0,
    "generative_ai": 1.0,
    "backend_developer": 0.9,
    "software_engineer": 0.8,
    "machine_learning": 0.8,
    "dotnet_developer": 0.6,
    "data_engineer": 0.5,
    "cloud_engineer": 0.4,
    "devops": 0.4,
    "full_stack": 0.6,
    "other": 0.2,
}


TARGET_ROLES = [
    "python_developer",
    "ai_engineer",
    "ai_developer",
    "llm_engineer",
    "generative_ai",
    "backend_developer",
]


# ============================================================
# UTILIDADES
# ============================================================

def normalize(text: str) -> str:
    return str(text).lower().strip()


# ============================================================
# EVIDENCIA DEL CANDIDATO
# ============================================================

def collect_skill_evidence(profile: dict) -> list[dict]:
    """
    Recoge todas las skills del perfil manteniendo
    información sobre dónde aparecen.
    """

    evidence = []

    # --------------------------------------------------------
    # Skills declaradas
    # --------------------------------------------------------

    for category, skills in profile.get("skills", {}).items():

        for skill in skills:

            evidence.append({
                "name": skill,
                "source": "skills",
                "category": category
            })

    # --------------------------------------------------------
    # Tecnologías utilizadas en experiencia profesional
    # --------------------------------------------------------

    for experience in profile.get("experience", []):

        for technology in experience.get("technologies", []):

            evidence.append({
                "name": technology,
                "source": "professional_experience",
                "company": experience.get("company"),
                "role": experience.get("role")
            })

    # --------------------------------------------------------
    # Tecnologías utilizadas en proyectos
    # --------------------------------------------------------

    for project in profile.get("projects", []):

        for technology in project.get("technologies", []):

            evidence.append({
                "name": technology,
                "source": "project",
                "project": project.get("name")
            })

    return evidence


# ============================================================
# MATCHING DE SKILLS
# ============================================================

def find_skill_matches(
    requirement_name: str,
    evidence: list[dict]
) -> list[dict]:

    requirement = normalize(requirement_name)

    matches = []

    for item in evidence:

        skill = normalize(item["name"])

        if requirement == skill:
            matches.append(item)

    return matches


def match_requirement(
    requirement: dict,
    evidence: list[dict]
) -> dict:

    name = requirement["name"]

    matches = find_skill_matches(
        name,
        evidence
    )

    result = {
        "requirement": name,
        "category": requirement.get("category"),
        "required": requirement.get("required", True),
        "match_type": requirement.get(
            "match_type",
            "individual"
        ),
        "group": requirement.get("group"),
        "status": "matched" if matches else "not_demonstrated",
        "evidence": matches
    }

    return result


# ============================================================
# EXPERIENCIA PROFESIONAL
# ============================================================

def parse_duration_to_months(duration: str) -> float:
    """
    Convierte duraciones habituales del perfil a meses.

    Ejemplos:
        "3 months"  -> 3
        "2 years"   -> 24
        "1.5 years" -> 18
        "2022-2023" -> 12
    """

    if not duration:
        return 0.0

    duration = str(duration).lower().strip()

    # --------------------------------------------------------
    # Formato: "3 months"
    # --------------------------------------------------------

    month_match = re.search(
        r"(\d+(?:\.\d+)?)\s*months?",
        duration
    )

    if month_match:
        return float(month_match.group(1))

    # --------------------------------------------------------
    # Formato: "2 years" / "1.5 years"
    # --------------------------------------------------------

    year_match = re.search(
        r"(\d+(?:\.\d+)?)\s*years?",
        duration
    )

    if year_match:
        return float(year_match.group(1)) * 12

    # --------------------------------------------------------
    # Formato: "2022-2023"
    # --------------------------------------------------------

    range_match = re.search(
        r"\b(20\d{2})\s*[-/]\s*(20\d{2})\b",
        duration
    )

    if range_match:

        start_year = int(range_match.group(1))
        end_year = int(range_match.group(2))

        if end_year >= start_year:
            return (end_year - start_year) * 12

    return 0.0


def calculate_professional_experience(
    profile: dict
) -> float:
    """
    Calcula los años de experiencia profesional
    a partir de los periodos declarados.
    """

    total_months = 0.0

    for experience in profile.get("experience", []):

        duration = experience.get(
            "duration",
            ""
        )

        total_months += parse_duration_to_months(
            duration
        )

    return total_months / 12


def match_experience(
    job_profile: dict,
    profile: dict
) -> dict:

    experience = job_profile.get(
        "experience",
        {}
    )

    required_years = experience.get(
        "minimum_years"
    )

    required = experience.get(
        "required",
        False
    )

    # --------------------------------------------------------
    # La oferta no especifica experiencia mínima
    # --------------------------------------------------------

    if required_years is None:

        return {
            "required": False,
            "status": "not_required",
            "required_years": None,
            "candidate_years": None,
            "ratio": 1.0
        }

    candidate_years = calculate_professional_experience(
        profile
    )

    # --------------------------------------------------------
    # Cumple experiencia
    # --------------------------------------------------------

    if candidate_years >= required_years:

        status = "matched"
        ratio = 1.0

    # --------------------------------------------------------
    # No cumple experiencia
    # --------------------------------------------------------

    elif required_years > 0:

        status = "not_met"

        ratio = min(
            candidate_years / required_years,
            1.0
        )

    # --------------------------------------------------------
    # Caso extraño: required_years = 0
    # --------------------------------------------------------

    else:

        status = "matched"
        ratio = 1.0

    return {
        "required": required,
        "status": status,
        "required_years": required_years,
        "candidate_years": round(
            candidate_years,
            2
        ),
        "ratio": round(
            ratio,
            2
        )
    }


# ============================================================
# ALTERNATIVAS
# ============================================================

def resolve_alternative_groups(
    results: list[dict]
) -> list[dict]:

    groups = {}

    # --------------------------------------------------------
    # Agrupar alternativas
    # --------------------------------------------------------

    for result in results:

        group = result.get("group")

        if (
            result.get("match_type") == "alternative"
            and group
        ):

            groups.setdefault(
                group,
                []
            ).append(result)

    # --------------------------------------------------------
    # Resolver cada grupo
    # --------------------------------------------------------

    for group_name, group_results in groups.items():

        matched = any(
            result["status"] == "matched"
            for result in group_results
        )

        for result in group_results:

            if matched:

                if result["status"] != "matched":

                    result["status"] = (
                        "alternative_satisfied"
                    )

            else:

                result["status"] = (
                    "alternative_not_met"
                )

    return results


# ============================================================
# SCORE DE REQUISITOS
# ============================================================

def build_requirement_units(
    results: list[dict]
) -> list[dict]:
    """
    Convierte los requisitos en unidades reales de evaluación.

    Un requisito individual cuenta como una unidad.

    Un grupo de alternativas cuenta como UNA única unidad:
        Python OR Java OR C#

    Esto evita que tres alternativas hagan que el requisito
    pese tres veces.
    """

    units = []

    alternative_groups = {}

    for result in results:

        if (
            result.get("match_type") == "alternative"
            and result.get("group")
        ):

            group = result["group"]

            alternative_groups.setdefault(
                group,
                []
            ).append(result)

        else:

            units.append({
                "type": "individual",
                "required": result["required"],
                "matched": result["status"] == "matched",
                "results": [result]
            })

    # --------------------------------------------------------
    # Añadir grupos de alternativas
    # --------------------------------------------------------

    for group_name, group_results in alternative_groups.items():

        matched = any(
            result["status"] == "matched"
            for result in group_results
        )

        units.append({
            "type": "alternative",
            "group": group_name,
            "required": group_results[0]["required"],
            "matched": matched,
            "results": group_results
        })

    return units


def calculate_requirement_score(
    results: list[dict]
) -> dict:

    units = build_requirement_units(
        results
    )

    required_units = [
        unit
        for unit in units
        if unit["required"]
    ]

    desirable_units = [
        unit
        for unit in units
        if not unit["required"]
    ]

    # --------------------------------------------------------
    # Requisitos obligatorios
    # --------------------------------------------------------

    required_matched = sum(
        1
        for unit in required_units
        if unit["matched"]
    )

    if required_units:

        required_score = (
            required_matched
            / len(required_units)
        ) * 100

    else:

        required_score = 100.0

    # --------------------------------------------------------
    # Requisitos deseables
    # --------------------------------------------------------

    desirable_matched = sum(
        1
        for unit in desirable_units
        if unit["matched"]
    )

    if desirable_units:

        desirable_score = (
            desirable_matched
            / len(desirable_units)
        ) * 100

    else:

        desirable_score = 100.0

    return {
        "required_score": round(
            required_score,
            2
        ),
        "desirable_score": round(
            desirable_score,
            2
        ),
        "required_total": len(
            required_units
        ),
        "required_matched": required_matched,
        "desirable_total": len(
            desirable_units
        ),
        "desirable_matched": desirable_matched
    }


# ============================================================
# ROLE MATCHING
# ============================================================

def match_role(
    job_profile: dict,
    candidate_profile: dict
) -> dict:

    role = job_profile.get(
        "role",
        {}
    )

    primary = normalize(
        role.get(
            "primary",
            "other"
        )
    )

    secondary = [
        normalize(value)
        for value in role.get(
            "secondary",
            []
        )
    ]

    candidate_roles = candidate_profile.get(
        "target_roles",
        TARGET_ROLES
    )

    candidate_roles = [
        normalize(role)
        for role in candidate_roles
    ]

    # --------------------------------------------------------
    # Coincidencia con role principal
    # --------------------------------------------------------

    primary_match = primary in candidate_roles

    # --------------------------------------------------------
    # Coincidencias secundarias
    # --------------------------------------------------------

    secondary_matches = [
        role
        for role in secondary
        if role in candidate_roles
    ]

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    if primary_match:

        role_score = 100.0

    elif secondary_matches:

        role_score = 75.0

    else:

        weight = ROLE_WEIGHTS.get(
            primary,
            ROLE_WEIGHTS["other"]
        )

        role_score = weight * 100

    return {
        "primary": primary,
        "secondary": secondary,
        "primary_match": primary_match,
        "secondary_matches": secondary_matches,
        "score": round(
            role_score,
            2
        )
    }


# ============================================================
# SCORE FINAL
# ============================================================

def calculate_weighted_score(
    requirement_score: dict,
    role_score: float,
    experience: dict
) -> dict:

    skills_score = (
        requirement_score["required_score"]
    )

    desirable_score = (
        requirement_score["desirable_score"]
    )

    experience_score = (
        experience.get(
            "ratio",
            1.0
        ) * 100
    )

    # --------------------------------------------------------
    # Distribución del score
    #
    # Skills obligatorias → 60%
    # Role fit             → 25%
    # Experiencia          → 10%
    # Deseables            → 5%
    # --------------------------------------------------------

    final_score = (
        skills_score * 0.60
        + role_score * 0.25
        + experience_score * 0.10
        + desirable_score * 0.05
    )

    return {
        "match_percentage": round(
            final_score,
            2
        ),
        "skills_score": round(
            skills_score,
            2
        ),
        "role_score": round(
            role_score,
            2
        ),
        "experience_score": round(
            experience_score,
            2
        ),
        "desirable_score": round(
            desirable_score,
            2
        )
    }


# ============================================================
# SUMMARY
# ============================================================

def calculate_summary(
    results: list[dict],
    experience: dict,
    role: dict
) -> dict:

    requirement_score = calculate_requirement_score(
        results
    )

    weighted_score = calculate_weighted_score(
        requirement_score,
        role["score"],
        experience
    )

    return {
        **weighted_score,

        "required_total": requirement_score[
            "required_total"
        ],

        "required_matched": requirement_score[
            "required_matched"
        ],

        "required_not_met": (
            requirement_score[
                "required_total"
            ]
            - requirement_score[
                "required_matched"
            ]
        ),

        "desirable_total": requirement_score[
            "desirable_total"
        ],

        "desirable_matched": requirement_score[
            "desirable_matched"
        ],

        "experience": experience,

        "role": role
    }


# ============================================================
# MATCH JOB
# ============================================================

def match_job(
    job_profile: dict,
    candidate_profile: dict
) -> dict:

    # --------------------------------------------------------
    # Recoger evidencia del candidato
    # --------------------------------------------------------

    evidence = collect_skill_evidence(
        candidate_profile
    )

    # --------------------------------------------------------
    # Evaluar requisitos
    # --------------------------------------------------------

    results = []

    for requirement in job_profile.get(
        "requirements",
        []
    ):

        result = match_requirement(
            requirement,
            evidence
        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # Resolver alternativas
    # --------------------------------------------------------

    results = resolve_alternative_groups(
        results
    )

    # --------------------------------------------------------
    # Evaluar experiencia
    # --------------------------------------------------------

    experience = match_experience(
        job_profile,
        candidate_profile
    )

    # --------------------------------------------------------
    # Evaluar role
    # --------------------------------------------------------

    role = match_role(
        job_profile,
        candidate_profile
    )

    # --------------------------------------------------------
    # Calcular resumen
    # --------------------------------------------------------

    summary = calculate_summary(
        results,
        experience,
        role
    )

    return {
        "job": {
            "title": job_profile.get(
                "title"
            ),
            "company": job_profile.get(
                "company"
            ),
            "location": job_profile.get(
                "location"
            )
        },

        "summary": summary,

        "experience": experience,

        "role": role,

        "requirements": results
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Cargar oferta analizada
    # --------------------------------------------------------

    with open(
        "output/job_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        job_profile = json.load(
            file
        )

    # --------------------------------------------------------
    # Cargar perfil del candidato
    # --------------------------------------------------------

    with open(
        "profile/master_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        candidate_profile = json.load(
            file
        )

    # --------------------------------------------------------
    # Ejecutar matching
    # --------------------------------------------------------

    result = match_job(
        job_profile,
        candidate_profile
    )

    # --------------------------------------------------------
    # Mostrar resultado
    # --------------------------------------------------------

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Guardar resultado
    # --------------------------------------------------------

    with open(
        "output/match_result.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )