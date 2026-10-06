import copy
import json



def adapt_cv(
    job_profile: dict,
    candidate_profile: dict,
    llm_client
) -> dict:
    # ==========================================================
    # INFORMACIÓN ORIGINAL
    # ==========================================================

    original_experience = candidate_profile.get(
        "experience",
        []
    )

    original_projects = candidate_profile.get(
        "projects",
        []
    )

    original_education = candidate_profile.get(
        "education",
        []
    )

    original_languages = candidate_profile.get(
        "languages",
        []
    )

    original_skills = candidate_profile.get(
        "skills",
        {}
    )

    # ==========================================================
    # ELEMENTOS VÁLIDOS
    # ==========================================================

    experience_names = [
        experience.get("company")
        for experience in original_experience
    ]

    project_names = [
        project.get("name")
        for project in original_projects
    ]

    education_titles = [
        education.get("title")
        for education in original_education
    ]

    language_names = [
        language.get("name")
        for language in original_languages
    ]

    # ==========================================================
    # INFORMACIÓN DEL CANDIDATO PARA EL LLM
    # ==========================================================

    candidate_information = {
        "skills": original_skills,

        "experience": [
            {
                "company": experience.get("company"),
                "role": experience.get("role"),
                "duration": experience.get("duration"),
                "period": experience.get("period"),
                "technologies": experience.get(
                    "technologies",
                    []
                ),
                "achievements": experience.get(
                    "achievements",
                    []
                )
            }
            for experience in original_experience
        ],

        "projects": [
            {
                "name": project.get("name"),
                "type": project.get("type"),
                "status": project.get("status"),
                "technologies": project.get(
                    "technologies",
                    []
                ),
                "description": project.get(
                    "description"
                )
            }
            for project in original_projects
        ],

        "education": original_education,

        "languages": original_languages
    }

    # ==========================================================
    # PROMPT
    # ==========================================================

    prompt = f"""
Adapta el CV a la oferta.

Tu trabajo es determinar qué información del perfil es más
relevante para esta oferta y devolverla como PRIORIDADES.

IMPORTANTE:

- El perfil es la fuente de verdad.
- Solo puedes seleccionar información que ya exista en el perfil.
- No inventes información.
- No modifiques información.
- No elimines información.
- Python conservará automáticamente todo lo que no priorices.
- "ats_keywords" puede contener términos profesionales relevantes para
  la oferta, aunque no aparezcan literalmente en el perfil.

==================================================
OFERTA
==================================================

{json.dumps(job_profile, ensure_ascii=False, indent=2)}

==================================================
PERFIL
==================================================

{json.dumps(candidate_information, ensure_ascii=False, indent=2)}

==================================================
ELEMENTOS VÁLIDOS
==================================================

EXPERIENCIAS:
{json.dumps(experience_names, ensure_ascii=False)}

PROYECTOS:
{json.dumps(project_names, ensure_ascii=False)}

FORMACIÓN:
{json.dumps(education_titles, ensure_ascii=False)}

IDIOMAS:
{json.dumps(language_names, ensure_ascii=False)}

CATEGORÍAS DE SKILLS:
{json.dumps(list(original_skills.keys()), ensure_ascii=False)}

SKILLS:
{json.dumps(original_skills, ensure_ascii=False)}

==================================================
REGLAS
==================================================

1. COPIA LITERAL

Los elementos seleccionados deben copiarse EXACTAMENTE
como aparecen en las listas anteriores.

No cambies nombres.
No traduzcas.
No abrevies.
No crees variantes.
No combines elementos.

Ejemplo:

"Microsoft Azure" → "Microsoft Azure"

NO → "Azure"

"ASP.NET Core" → "ASP.NET Core"

NO → "ASP.NET"

"Minsait" → "Minsait"

NO → "Desarrollador Full Stack en Minsait"


2. EXPERIENCIA

Selecciona las experiencias profesionales más relevantes
para la oferta.

Ordénalas de mayor a menor relevancia.

Utiliza únicamente los nombres de la lista EXPERIENCIAS.


3. PROYECTOS

Selecciona los proyectos más relevantes.

Ordénalos de mayor a menor relevancia.

Utiliza únicamente los nombres de la lista PROYECTOS.


4. FORMACIÓN

Selecciona la formación más relevante.

Ordénala de mayor a menor relevancia.

Utiliza únicamente los títulos de la lista FORMACIÓN.


5. IDIOMAS

Selecciona los idiomas relevantes.

Utiliza únicamente los nombres de la lista IDIOMAS.


6. SKILLS

Para cada categoría, selecciona las skills más relevantes.

Ordénalas de mayor a menor relevancia.

Utiliza únicamente categorías y skills que existan
en el perfil.

No muevas skills entre categorías.


7. RELEVANCIA

Prioriza:

- requisitos explícitos;
- tecnologías explícitamente requeridas;
- tecnologías deseables;
- experiencia relacionada;
- proyectos relacionados;
- formación relacionada.

No inventes equivalencias.

Si la oferta pide una tecnología que no existe en el perfil,
no la sustituyas por otra.




8. TARGET POSITION

Indica el puesto al que corresponde la oferta.

No inventes un puesto diferente.

==================================================
SALIDA
==================================================

Devuelve SOLO JSON válido:

{{
    "target_position": "",
    "summary": "",
    "experience_priority": [],
    "project_priority": [],
    "education_priority": [],
    "language_priority": [],
    "skills_priority": {{}},
    "ats_keywords": []
}}


ATS KEYWORDS:

Genera entre 5 y 15 keywords o expresiones relevantes para la oferta.

Prioriza términos que aparezcan explícitamente en la oferta.

Las keywords deben ser naturales y profesionales.

No repitas literalmente todas las skills del perfil.

No utilices ats_keywords para inventar tecnologías o experiencia.

Ejemplo:

[
    "Agile",
    "Scrum",
    "Trabajo en equipo",
    "Resolución de problemas",
    "Comunicación técnica",
    "Buenas prácticas de desarrollo",
    "Desarrollo de APIs"
]

Las listas de prioridad pueden contener solo algunos
elementos.

Ejemplo:

Si existen:

["A", "B", "C", "D"]

puedes devolver:

["C", "A"]

Python colocará después B y D.

==================================================
COMPROBACIÓN
==================================================

Antes de responder comprueba:

- Cada experiencia existe literalmente en EXPERIENCIAS.
- Cada proyecto existe literalmente en PROYECTOS.
- Cada formación existe literalmente en FORMACIÓN.
- Cada idioma existe literalmente en IDIOMAS.
- Cada categoría de skills existe literalmente en CATEGORÍAS.
- Cada skill existe literalmente dentro de su categoría.
- No hay elementos inventados.
- No has cambiado ningún nombre.

Si tienes dudas sobre un elemento, no lo incluyas.

Devuelve únicamente el JSON.
"""

    # ==========================================================
    # OLLAMA
    # ==========================================================

    content = llm_client.generate(
        prompt,
        temperature=0.2,
        max_tokens=3000
    )

    print("\n========== RESPUESTA RAW ==========")
    print(content)
    print("===================================")
    print("Longitud:", len(content))
    print("===================================\n")

    adaptation = parse_json_response(content)

    # ==========================================================
    # VALIDAR RESPUESTA DEL LLM
    # ==========================================================

    validate_adaptation(
        adaptation,
        candidate_profile
    )

    # ==========================================================
    # CONSTRUIR CV COMPLETO
    # ==========================================================

    adapted_profile = build_complete_profile(
        adaptation,
        candidate_profile,
        job_profile
    )

    # ==========================================================
    # VALIDACIÓN FINAL
    # ==========================================================

    validate_adapted_profile(
        adapted_profile,
        candidate_profile
    )

    return adapted_profile


# ==============================================================
# CONSTRUIR CV COMPLETO
# ==============================================================

def build_complete_profile(
    adaptation: dict,
    candidate_profile: dict,
    job_profile: dict
) -> dict:

    # El perfil original es la fuente de verdad.
    adapted_profile = copy.deepcopy(candidate_profile)

    # ==========================================================
    # TARGET POSITION
    # ==========================================================

    target_position = adaptation.get(
        "target_position",
        ""
    ).strip()

    if not target_position:

        target_position = (
            job_profile.get("title")
            or job_profile.get("position")
            or job_profile.get("role")
            or ""
        )

    adapted_profile["target_position"] = target_position

    # ==========================================================
    # SUMMARY
    # ==========================================================

    adapted_profile["summary"] = ""

    # ==========================================================
    # EXPERIENCE
    # ==============================================================

    adapted_profile["experience"] = reorder_items(
        original_items=candidate_profile.get(
            "experience",
            []
        ),
        priority_names=adaptation.get(
            "experience_priority",
            []
        ),
        key="company"
    )

    # ==========================================================
    # PROJECTS
    # ==============================================================

    adapted_profile["projects"] = reorder_items(
        original_items=candidate_profile.get(
            "projects",
            []
        ),
        priority_names=adaptation.get(
            "project_priority",
            []
        ),
        key="name"
    )

    # ==========================================================
    # EDUCATION
    # ==============================================================

    adapted_profile["education"] = reorder_items(
        original_items=candidate_profile.get(
            "education",
            []
        ),
        priority_names=adaptation.get(
            "education_priority",
            []
        ),
        key="title"
    )

    # ==========================================================
    # LANGUAGES
    # ==============================================================

    adapted_profile["languages"] = reorder_items(
        original_items=candidate_profile.get(
            "languages",
            []
        ),
        priority_names=adaptation.get(
            "language_priority",
            []
        ),
        key="name"
    )

    # ==========================================================
    # SKILLS
    # ==============================================================

    original_skills = candidate_profile.get(
        "skills",
        {}
    )

    skills_priority = adaptation.get(
        "skills_priority",
        {}
    )

    ordered_skills = {}

    for category, original_values in original_skills.items():

        priority_values = skills_priority.get(
            category,
            []
        )

        ordered_values = []

        # Primero las skills relevantes.
        for skill in priority_values:

            if skill in original_values:

                if skill not in ordered_values:

                    ordered_values.append(skill)

        # Después TODO lo demás.
        for skill in original_values:

            if skill not in ordered_values:

                ordered_values.append(skill)

        ordered_skills[category] = ordered_values

    adapted_profile["skills"] = ordered_skills

    return adapted_profile


# ==============================================================
# REORDENAR SIN PERDER INFORMACIÓN
# ==============================================================

def reorder_items(
    original_items: list,
    priority_names: list,
    key: str
) -> list:

    items_by_name = {
        item.get(key): item
        for item in original_items
    }

    ordered_items = []

    # Primero los elementos priorizados por el LLM.
    for name in priority_names:

        item = items_by_name.get(name)

        if item is not None:

            ordered_items.append(
                copy.deepcopy(item)
            )

    # Después TODOS los elementos que no fueron priorizados.
    for item in original_items:

        name = item.get(key)

        if name not in priority_names:

            ordered_items.append(
                copy.deepcopy(item)
            )

    return ordered_items


# ==============================================================
# VALIDAR ADAPTACIÓN DEL LLM
# ==============================================================

def validate_adaptation(
    adaptation: dict,
    candidate_profile: dict
):

    required_fields = [
        "target_position",
        "summary",
        "experience_priority",
        "project_priority",
        "education_priority",
        "language_priority",
        "skills_priority",
        "ats_keywords"
    ]

    if not isinstance(adaptation["ats_keywords"], list):
        raise ValueError(
            "CV Adapter inválido: "
            "'ats_keywords' debe ser una lista."
        )

    for field in required_fields:

        if field not in adaptation:

            raise ValueError(
                "CV Adapter inválido: "
                f"falta el campo '{field}'."
            )

    # ==========================================================
    # EXPERIENCE
    # ==========================================================

    original_companies = [
        experience.get("company")
        for experience in candidate_profile.get(
            "experience",
            []
        )
    ]

    validate_priority_subset(
        original_companies,
        adaptation["experience_priority"],
        "experience_priority"
    )

    # ==========================================================
    # PROJECTS
    # ==========================================================

    original_projects = [
        project.get("name")
        for project in candidate_profile.get(
            "projects",
            []
        )
    ]

    validate_priority_subset(
        original_projects,
        adaptation["project_priority"],
        "project_priority"
    )

    # ==========================================================
    # EDUCATION
    # ==========================================================

    original_education = [
        education.get("title")
        for education in candidate_profile.get(
            "education",
            []
        )
    ]

    validate_priority_subset(
        original_education,
        adaptation["education_priority"],
        "education_priority"
    )

    # ==========================================================
    # LANGUAGES
    # ==========================================================

    original_languages = [
        language.get("name")
        for language in candidate_profile.get(
            "languages",
            []
        )
    ]

    validate_priority_subset(
        original_languages,
        adaptation["language_priority"],
        "language_priority"
    )

    # ==========================================================
    # SKILLS
    # ==========================================================

    original_skills = candidate_profile.get(
        "skills",
        {}
    )

    adapted_skills = adaptation[
        "skills_priority"
    ]

    if not isinstance(adapted_skills, dict):

        raise ValueError(
            "CV Adapter inválido: "
            "'skills_priority' debe ser un objeto."
        )

    # El LLM puede omitir categorías completas si
    # no considera ninguna skill relevante.
    for category, priority_values in adapted_skills.items():

        if category not in original_skills:

            raise ValueError(
                "CV Adapter inválido: "
                f"categoría de skills inexistente: "
                f"'{category}'."
            )

        validate_priority_subset(
            original_skills[category],
            priority_values,
            f"skills_priority['{category}']"
        )

    print("✅ Validación de prioridades correcta")


# ==============================================================
# VALIDAR SUBCONJUNTO DE PRIORIDADES
# ==============================================================

def validate_priority_subset(
    original,
    received,
    field_name
):

    if not isinstance(received, list):

        raise ValueError(
            "CV Adapter inválido: "
            f"'{field_name}' debe ser una lista."
        )

    if len(set(received)) != len(received):

        raise ValueError(
            "CV Adapter inválido: "
            f"'{field_name}' contiene elementos duplicados.\n"
            f"Recibidos: {received}"
        )

    invalid = [
        value
        for value in received
        if value not in original
    ]

    if invalid:

        raise ValueError(
            "CV Adapter inválido: "
            f"'{field_name}' contiene elementos "
            f"que no existen en el perfil.\n"
            f"Inválidos: {invalid}"
        )


# ==============================================================
# VALIDACIÓN DEL CV FINAL
# ==============================================================

def validate_adapted_profile(
    adapted_profile: dict,
    candidate_profile: dict
):

    # ==========================================================
    # EXPERIENCE
    # ==========================================================

    original_experience = candidate_profile.get(
        "experience",
        []
    )

    adapted_experience = adapted_profile.get(
        "experience",
        []
    )

    if len(original_experience) != len(
        adapted_experience
    ):

        raise ValueError(
            "CV final inválido: "
            "se ha perdido alguna experiencia."
        )

    original_by_company = {
        experience.get("company"): experience
        for experience in original_experience
    }

    adapted_by_company = {
        experience.get("company"): experience
        for experience in adapted_experience
    }

    if set(original_by_company) != set(
        adapted_by_company
    ):

        raise ValueError(
            "CV final inválido: "
            "las empresas no coinciden."
        )

    for company, original in original_by_company.items():

        adapted = adapted_by_company[company]

        if adapted != original:

            raise ValueError(
                "CV final inválido: "
                f"se ha modificado información "
                f"de '{company}'."
            )

    # ==========================================================
    # PROJECTS
    # ==========================================================

    original_projects = candidate_profile.get(
        "projects",
        []
    )

    adapted_projects = adapted_profile.get(
        "projects",
        []
    )

    original_by_name = {
        project.get("name"): project
        for project in original_projects
    }

    adapted_by_name = {
        project.get("name"): project
        for project in adapted_projects
    }

    if original_by_name != adapted_by_name:

        raise ValueError(
            "CV final inválido: "
            "se ha modificado información de proyectos."
        )

    # ==========================================================
    # EDUCATION
    # ==========================================================

    original_education = candidate_profile.get(
        "education",
        []
    )

    adapted_education = adapted_profile.get(
        "education",
        []
    )

    original_by_title = {
        education.get("title"): education
        for education in original_education
    }

    adapted_by_title = {
        education.get("title"): education
        for education in adapted_education
    }

    if original_by_title != adapted_by_title:

        raise ValueError(
            "CV final inválido: "
            "se ha modificado información de educación."
        )

    # ==========================================================
    # LANGUAGES
    # ==========================================================

    original_languages = candidate_profile.get(
        "languages",
        []
    )

    adapted_languages = adapted_profile.get(
        "languages",
        []
    )

    original_language_map = {
        language.get("name"): language.get("level")
        for language in original_languages
    }

    adapted_language_map = {
        language.get("name"): language.get("level")
        for language in adapted_languages
    }

    if original_language_map != adapted_language_map:

        raise ValueError(
            "CV final inválido: "
            "se han modificado los idiomas."
        )

    # ==========================================================
    # SKILLS
    # ==========================================================

    original_skills = candidate_profile.get(
        "skills",
        {}
    )

    adapted_skills = adapted_profile.get(
        "skills",
        {}
    )

    if set(original_skills) != set(adapted_skills):

        raise ValueError(
            "CV final inválido: "
            "han desaparecido categorías de skills."
        )

    for category, original_values in original_skills.items():

        adapted_values = adapted_skills.get(
            category,
            []
        )

        if len(original_values) != len(
            adapted_values
        ):

            raise ValueError(
                "CV final inválido: "
                f"han desaparecido skills de "
                f"'{category}'."
            )

        if set(original_values) != set(
            adapted_values
        ):

            raise ValueError(
                "CV final inválido: "
                f"han desaparecido o aparecido "
                f"skills en '{category}'."
            )

    print("✅ Validación CV completo correcta")


# ==============================================================
# PARSE JSON
# ==============================================================

def parse_json_response(content: str) -> dict:

    content = content.strip()

    if content.startswith("```"):

        lines = content.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    return json.loads(content)


# ==============================================================
# PRUEBA DIRECTA
# ==============================================================

if __name__ == "__main__":

    with open(
        "profile/master_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        candidate_profile = json.load(file)

    with open(
        "output/job_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        job_profile = json.load(file)

    adapted_profile = adapt_cv(
        job_profile,
        candidate_profile
    )

    print(
        json.dumps(
            adapted_profile,
            indent=4,
            ensure_ascii=False
        )
    )

    with open(
        "output/adapted_profile.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            adapted_profile,
            file,
            indent=4,
            ensure_ascii=False
        )