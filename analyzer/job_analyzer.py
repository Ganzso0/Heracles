import json
import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "ministral-3:8b"


def analyze_job(job_text: str) -> dict:

    prompt = f"""
Analiza la siguiente oferta de trabajo y conviértela EXCLUSIVAMENTE
en el JSON indicado.

Tu objetivo es identificar QUÉ PIDE REALMENTE LA EMPRESA para poder
compararlo posteriormente con el perfil profesional de un candidato.

REGLAS:

1. NO INVENTES INFORMACIÓN.

   Solo puedes extraer información que aparezca explícitamente en
   la oferta.

   Si un dato no aparece explícitamente, utiliza null o [] según
   corresponda.

2. NO INFIERAS información a partir de:

   - el título del puesto
   - el nivel de seniority
   - tecnologías relacionadas
   - conocimientos habituales del sector
   - conocimientos que normalmente acompañan a una tecnología
   - años de experiencia
   - ubicación de la empresa
   - idioma en el que está escrita la oferta

   Ejemplos:

   - "Senior .NET Developer" NO implica "Entity Framework".
   - ".NET" NO implica "C#".
   - ".NET" NO implica "ASP.NET".
   - "ASP.NET" NO implica "ASP.NET Core".
   - "AWS" NO implica "Azure".
   - "SQL" NO implica "SQL Server".
   - "Docker" NO implica "Kubernetes".
   - "Senior Developer" NO implica titulación universitaria.
   - Un puesto tecnológico NO implica conocimientos de inglés.

3. DISTINGUE entre requisitos OBLIGATORIOS y DESEABLES.

4. Si la oferta utiliza expresiones como:

   - "se requiere"
   - "imprescindible"
   - "obligatorio"
   - "must have"
   - "required"
   - "requisito"

   considéralo obligatorio.

5. Si la oferta utiliza expresiones como:

   - "valorable"
   - "se valorará"
   - "deseable"
   - "nice to have"
   - "plus"
   - "preferred"

   considéralo deseable.

6. Si una tecnología aparece EXPLÍCITAMENTE como parte del perfil
   solicitado o de los requisitos técnicos y no se indica si es
   obligatoria o deseable, considérala obligatoria.

7. EXTRACCIÓN LITERAL DE TECNOLOGÍAS.

   Si una tecnología, lenguaje, framework, biblioteca, herramienta,
   plataforma, arquitectura, metodología o concepto técnico aparece
   explícitamente como parte del perfil solicitado, debes considerar
   esa mención para "requirements".

   NO sustituyas una tecnología específica por otra más genérica.

   Ejemplos:

   - Si aparece "ASP.NET", extrae "ASP.NET".
   - Si aparece ".NET", extrae ".NET".
   - Si aparecen ".NET" y "ASP.NET", pueden aparecer ambos.
   - "ASP.NET" NO debe convertirse en ".NET".
   - "ASP.NET Core" NO debe convertirse en "ASP.NET".
   - "Entity Framework Core" NO debe convertirse en ".NET".
   - "C#" NO debe convertirse en ".NET".

8. Una tecnología solo puede aparecer en "requirements" si aparece
   explícitamente en la oferta.

   NO añadas tecnologías relacionadas o habitualmente asociadas.

   Por ejemplo, si aparece:

   ".NET"

   NO añadas automáticamente:

   - C#
   - ASP.NET
   - ASP.NET Core
   - Entity Framework
   - LINQ

   Cada tecnología debe aparecer explícitamente en la oferta.

9. No confundas una tecnología mencionada como contexto con un
   requisito.

   Por ejemplo:

   "La empresa trabaja con tecnologías Microsoft"

   NO significa automáticamente que "Microsoft" sea un requisito.

   Del mismo modo, una tecnología mencionada únicamente dentro de
   una responsabilidad no debe convertirse automáticamente en
   requisito.

   Solo inclúyela como requisito cuando el texto indique que forma
   parte de los conocimientos, tecnologías, experiencia o capacidades
   solicitadas al candidato.

10. Extrae los años de experiencia SOLAMENTE cuando estén indicados
    explícitamente.

    Ejemplo:

    "mínimo 3 años de experiencia"

    debe producir:

    "minimum_years": 3
    "required": true

11. Si se menciona experiencia pero no se especifica una cantidad
    mínima de años, utiliza:

    "minimum_years": null

12. No confundas RESPONSABILIDADES del puesto con REQUISITOS.

    Las tareas que realizará el candidato deben ir en
    "responsibilities".

13. No conviertas una responsabilidad en una skill salvo que la oferta
    indique claramente que dicha tecnología, conocimiento o competencia
    es requerida.

14. Mantén los nombres de las tecnologías reconocibles y cercanos a
    cómo aparecen en la oferta.

    Ejemplos:

    ".NET Core" → ".NET Core"
    "C sharp" → "C#"
    "C Sharp" → "C#"
    "Entity Framework Core" → "Entity Framework Core"

    Puedes normalizar diferencias evidentes de escritura, pero NO
    puedes cambiar una tecnología por otra diferente.

15. Si la oferta menciona explícitamente una arquitectura,
    metodología, herramienta, tecnología o concepto técnico como
    requisito, inclúyelo en "requirements".

16. NO asumas equivalencias entre tecnologías.

    Ejemplos:

    ".NET" NO significa automáticamente "ASP.NET Core".
    "AWS" NO significa automáticamente "Azure".
    "SQL" NO significa automáticamente "SQL Server".
    "Docker" NO significa automáticamente "Kubernetes".

17. OOP (Object-Oriented Programming) y OOD (Object-Oriented Design)
    deben clasificarse como:

    "programming_concept"

    y NO como "design_pattern".

18. Los design patterns concretos deben clasificarse como:

    "design_pattern"

19. Si varios requisitos están unidos por "o", "OR", "either...or",
    considéralo un conjunto de requisitos alternativos.

    Ejemplo:

    "Azure o AWS"

    debe producir dos elementos con:

    "match_type": "alternative"

    y el mismo valor en "group".

20. Si varios requisitos están unidos por "y", "AND", considéralos
    requisitos independientes, salvo que el contexto indique
    claramente que forman una única alternativa.

21. Para requisitos alternativos utiliza:

    "match_type": "alternative"

    y el mismo valor en "group" para todos los elementos del grupo.

22. Para requisitos independientes utiliza:

    "match_type": "individual"

    y:

    "group": null

23. EDUCATION debe contener ÚNICAMENTE titulaciones o requisitos
    educativos mencionados EXPLÍCITAMENTE en la oferta.

    No infieras una titulación porque el puesto sea senior, técnico
    o profesional.

    Si la oferta no menciona ninguna titulación:

    "education": []

24. LANGUAGES debe contener ÚNICAMENTE idiomas mencionados
    EXPLÍCITAMENTE en la oferta.

    No infieras idiomas por:

    - la ubicación
    - el idioma de la oferta
    - el tipo de puesto
    - la empresa

    Si la oferta no menciona ningún idioma:

    "languages": []

25. Si un idioma aparece pero la oferta no especifica nivel:

    "level": null

26. Si una titulación, idioma o requisito aparece como deseable:

    "required": false

27. Si una titulación, idioma o requisito aparece como obligatorio:

    "required": true

28. No incluyas habilidades genéricas como:

    - trabajo en equipo
    - comunicación
    - proactividad
    - responsabilidad
    - capacidad de aprendizaje

    salvo que sean especialmente relevantes para evaluar el perfil
    profesional y la oferta las presente como un requisito real.

29. El título, empresa y ubicación deben extraerse de la oferta cuando
    estén disponibles.

    No inventes ninguno de estos datos.

30. "seniority" debe extraerse ÚNICAMENTE cuando la oferta indique
    explícitamente un nivel como:

    - Junior
    - Mid
    - Middle
    - Senior
    - Lead
    - Principal
    - Staff
    - Architect

31. NO deduzcas seniority únicamente por los años de experiencia.

32. ANTES DE GENERAR EL JSON, realiza una comprobación final:

    - Comprueba que no has añadido ninguna tecnología que no aparezca
      explícitamente en la oferta.
    - Comprueba que no has añadido ninguna titulación que no aparezca
      explícitamente.
    - Comprueba que no has añadido ningún idioma que no aparezca
      explícitamente.
    - Comprueba que no has convertido una tecnología específica en
      otra más genérica.
    - Comprueba que no has omitido una tecnología que aparece
      explícitamente como parte del perfil solicitado.
    - Comprueba que los requisitos "o / OR / either...or" están
      correctamente agrupados como alternativas.
    - Comprueba que las responsabilidades no se han convertido
      incorrectamente en requisitos.
33. SEPARACIÓN ESTRICTA ENTRE REQUISITOS Y RESPONSABILIDADES.

    UNA TECNOLOGÍA, HERRAMIENTA, PLATAFORMA, ARQUITECTURA O CONOCIMIENTO
    NO DEBE AÑADIRSE A "requirements" ÚNICAMENTE POR APARECER EN UNA
    RESPONSABILIDAD.

    Si la tecnología aparece dentro de una frase introducida como:
    - "Funciones"
    - "Responsabilidades"
    - "Tareas"
    - "Te encargarás de..."
    - "Trabajarás en..."
    - "Participarás en..."
    - "Desarrollarás..."
    - "Realizarás..."
    - "Tus funciones serán..."
    
    entonces esa mención pertenece a "responsibilities" y NO debe
    convertirse en un requisito.

    Para añadir una tecnología a "requirements", debe existir una
    evidencia explícita de que la empresa la solicita al candidato,
    por ejemplo:
    - experiencia con X
    - conocimientos de X
    - dominio de X
    - experiencia mínima con X
    - se requiere X
    - imprescindible X
    - se valorará X
    - deseable X
    - X es requisito
    - X forma parte del perfil buscado

    EJEMPLO:

    "Buscamos un desarrollador con experiencia en ASP.NET.
     Funciones: desarrollo de soluciones basadas en tecnologías
     Microsoft."

    Resultado:

    "ASP.NET" → requirements

    "tecnologías Microsoft" → NO requirements
    "tecnologías Microsoft" → puede aparecer únicamente dentro de
    responsibilities.

    IMPORTANTE:
    El hecho de que una tecnología aparezca en una responsabilidad
    NO constituye evidencia suficiente para considerarla un requisito.

OFERTA:
{job_text}

Devuelve EXACTAMENTE esta estructura:

{{
    "title": null,
    "company": null,
    "location": null,
    "seniority": null,

    "experience": {{
        "minimum_years": null,
        "required": false
    }},

    "requirements": [
        {{
            "name": "",
            "category": "",
            "required": true,
            "match_type": "individual",
            "group": null
        }}
    ],

    "education": [
        {{
            "name": "",
            "required": true
        }}
    ],

    "languages": [
        {{
            "name": "",
            "level": null,
            "required": true
        }}
    ],

    "responsibilities": []
}}

CATEGORÍAS PERMITIDAS PARA "requirements":

- programming_language
- programming_concept
- framework
- library
- architecture
- design_pattern
- database
- cloud
- infrastructure
- messaging
- testing
- methodology
- tool
- ai_ml
- data
- other

IMPORTANTE:

- "required" debe ser true o false.
- true = requisito obligatorio.
- false = requisito deseable.
- Si una tecnología aparece explícitamente como requisito técnico
  pero no se especifica si es obligatoria o deseable, utiliza true.
- No añadas tecnologías que no aparezcan explícitamente.
- No añadas titulaciones que no aparezcan explícitamente.
- No añadas idiomas que no aparezcan explícitamente.
- No completes información basándote en conocimientos externos.
- No inventes requisitos.
- No elimines una tecnología específica porque exista otra tecnología
  relacionada o más general.
- Responde únicamente con JSON válido.
- No escribas explicaciones.
- No uses markdown.
"""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "num_predict": 1000
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    content = result["message"]["content"]

    print()
    print("==============================")
    print("RESPUESTA RAW DEL MODELO")
    print("==============================")
    print(repr(content))
    print()

    return parse_json_response(content)

def parse_json_response(content: str) -> dict:

    content = content.strip()

    # JSON puro
    if content.startswith("{") and content.endswith("}"):
        return json.loads(content)

    # JSON dentro de ```json ... ```
    if content.startswith("```"):

        lines = content.splitlines()

        # Eliminar ```json
        lines = lines[1:]

        # Eliminar ``` final
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    return json.loads(content)


if __name__ == "__main__":

    with open(
        "oferta.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_text = file.read()

    job_profile = analyze_job(job_text)

    print(
        json.dumps(
            job_profile,
            indent=4,
            ensure_ascii=False
        )
    )

    with open(
        "output/job_profile.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            job_profile,
            file,
            indent=4,
            ensure_ascii=False
        )