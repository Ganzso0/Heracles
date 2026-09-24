import json


def normalize(text: str) -> str:
    return text.lower().strip()


def collect_skill_evidence(profile: dict) -> list[dict]:
    """
    Recoge todas las skills del perfil y mantiene
    información sobre dónde aparecen.
    """

    evidence = []

    for category, skills in profile.get("skills", {}).items():

        for skill in skills:
            evidence.append({
                "name": skill,
                "source": "skills",
                "category": category
            })

    # Tecnologías utilizadas en experiencia profesional
    for experience in profile.get("experience", []):

        for technology in experience.get("technologies", []):

            evidence.append({
                "name": technology,
                "source": "professional_experience",
                "company": experience.get("company"),
                "role": experience.get("role")
            })

    # Tecnologías utilizadas en proyectos
    for project in profile.get("projects", []):

        for technology in project.get("technologies", []):

            evidence.append({
                "name": technology,
                "source": "project",
                "project": project.get("name")
            })

    return evidence


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

    if matches:

        return {
            "requirement": name,
            "category": requirement["category"],
            "required": requirement["required"],
            "match_type": requirement.get(
                "match_type",
                "individual"
            ),
            "group": requirement.get("group"),
            "status": "matched",
            "evidence": matches
        }

    return {
        "requirement": name,
        "category": requirement["category"],
        "required": requirement["required"],
        "match_type": requirement.get(
            "match_type",
            "individual"
        ),
        "group": requirement.get("group"),
        "status": "not_demonstrated",
        "evidence": []
    }


def calculate_professional_experience(
    profile: dict
) -> float:

    total_months = 0

    for experience in profile.get(
        "experience",
        []
    ):

        duration = experience.get(
            "duration",
            ""
        ).lower()

        if "month" in duration:

            try:
                months = int(
                    duration.split()[0]
                )
                total_months += months
            except ValueError:
                pass

        elif "year" in duration:

            try:
                years = float(
                    duration.split()[0]
                )
                total_months += years * 12
            except ValueError:
                pass

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

    if required_years is None:

        return {
            "required": False,
            "status": "not_required",
            "required_years": None,
            "candidate_years": None
        }

    candidate_years = calculate_professional_experience(
        profile
    )

    if candidate_years >= required_years:

        status = "matched"

    else:

        status = "not_met"

    return {
        "required": required,
        "status": status,
        "required_years": required_years,
        "candidate_years": round(
            candidate_years,
            2
        )
    }


def resolve_alternative_groups(
    results: list[dict]
) -> list[dict]:

    groups = {}

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

    for group_name, group_results in groups.items():

        matched = any(
            result["status"] == "matched"
            for result in group_results
        )

        for result in group_results:

            if matched:

                if result["status"] == "matched":

                    result["status"] = "matched"

                else:

                    result["status"] = "alternative_satisfied"

            else:

                result["status"] = "alternative_not_met"

    return results


def calculate_summary(
    results: list[dict],
    experience: dict
) -> dict:

    # Requisitos individuales obligatorios
    individual_required = [
        result
        for result in results
        if result["required"]
        and result.get("match_type") != "alternative"
    ]

    # Grupos de alternativas obligatorios
    alternative_groups = {}

    for result in results:

        if (
            result["required"]
            and result.get("match_type") == "alternative"
        ):

            group = result.get("group")

            if group:
                alternative_groups.setdefault(
                    group,
                    []
                ).append(result)

    # Número efectivo de requisitos obligatorios
    effective_required_total = (
        len(individual_required)
        + len(alternative_groups)
    )

    # Requisitos individuales cumplidos
    individual_matched = [
        result
        for result in individual_required
        if result["status"] == "matched"
    ]

    # Grupos de alternativas cumplidos
    alternative_matched = [
        group
        for group, group_results
        in alternative_groups.items()
        if any(
            result["status"] == "matched"
            for result in group_results
        )
    ]

    effective_required_matched = (
        len(individual_matched)
        + len(alternative_matched)
    )

    effective_required_not_met = (
        effective_required_total
        - effective_required_matched
    )

    # Porcentaje principal
    if effective_required_total > 0:

        match_percentage = (
            effective_required_matched
            / effective_required_total
        ) * 100

    else:

        match_percentage = 100.0

    # Deseables
    desirable = [
        result
        for result in results
        if not result["required"]
    ]

    desirable_matched = [
        result
        for result in desirable
        if result["status"] == "matched"
    ]

    return {
        "match_percentage": round(
            match_percentage,
            2
        ),

        "required_total": effective_required_total,

        "required_matched": effective_required_matched,

        "required_not_met": effective_required_not_met,

        "desirable_total": len(
            desirable
        ),

        "desirable_matched": len(
            desirable_matched
        ),

        "experience": experience
    }


def match_job(
    job_profile: dict,
    candidate_profile: dict
) -> dict:

    evidence = collect_skill_evidence(
        candidate_profile
    )

    results = []

    for requirement in job_profile.get(
        "requirements",
        []
    ):

        result = match_requirement(
            requirement,
            evidence
        )

        results.append(result)

    results = resolve_alternative_groups(
        results
    )

    experience = match_experience(
        job_profile,
        candidate_profile
    )

    summary = calculate_summary(
        results,
        experience
    )

    return {
        "job": {
            "title": job_profile.get("title"),
            "company": job_profile.get("company"),
            "location": job_profile.get("location")
        },
        "summary": summary,
        "experience": experience,
        "requirements": results
    }


if __name__ == "__main__":

    with open(
        "output/job_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        job_profile = json.load(file)

    with open(
        "profile/master_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        candidate_profile = json.load(file)

    result = match_job(
        job_profile,
        candidate_profile
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

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