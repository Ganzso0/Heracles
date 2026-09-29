import json
import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "ministral-3:8b"


def generate_cover_letter(
    job_profile: dict,
    candidate_profile: dict,
    match_result: dict
) -> str:

    prompt = f"""
Eres un asistente especializado en redactar cartas de presentación profesionales.

Debes redactar una carta de presentación personalizada para una oferta de empleo
utilizando EXCLUSIVAMENTE la información proporcionada.

No inventes:
- experiencia profesional
- años de experiencia
- tecnologías
- responsabilidades
- proyectos
- formación
- certificaciones

Puedes destacar y relacionar información real del candidato con los requisitos
de la oferta.

La carta debe:
- estar escrita en español
- ser profesional pero natural
- tener una extensión aproximada de 250-350 palabras
- centrarse en por qué el perfil del candidato puede ser relevante para la oferta
- mencionar tecnologías o conocimientos relevantes cuando tenga sentido
- no mencionar el porcentaje de compatibilidad
- no decir que la carta ha sido generada por IA
- no utilizar listas
- no utilizar títulos como "Carta de presentación"
- devolver únicamente el texto de la carta

MUY IMPORTANTE:

Nunca confundas los requisitos de la oferta con la experiencia del candidato.

El campo "experience.minimum_years" indica LO QUE PIDE LA EMPRESA,
NO los años de experiencia que tiene el candidato.

Nunca afirmes que el candidato tiene un número de años de experiencia
que no aparezca explícitamente en candidate_profile.

Nunca conviertas una tecnología requerida por la oferta en una tecnología
que el candidato domina.

Si el candidato no cumple un requisito, NO intentes ocultarlo ni inventar
experiencia para compensarlo.

Es preferible omitir una tecnología que afirmar que el candidato la domina.

OFERTA:
{json.dumps(job_profile, ensure_ascii=False, indent=2)}

PERFIL DEL CANDIDATO:
{json.dumps(candidate_profile, ensure_ascii=False, indent=2)}

RESULTADO DE COMPATIBILIDAD:
{json.dumps(match_result, ensure_ascii=False, indent=2)}
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
            "options": {
                "num_predict": 700
            }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"].strip()