import json

from cover_letter import generate_cover_letter


with open("profile/master_profile.json", "r", encoding="utf-8") as file:
    candidate_profile = json.load(file)


job_profile = {
    "title": "Senior Full Stack & AI Engineer",
    "company": "HiveMQ",
    "location": "Madrid",
    "seniority": None,
    "experience": {
        "minimum_years": 5,
        "required": True
    },
    "requirements": [
        {"name": "TypeScript", "required": True},
        {"name": "Node.js", "required": True},
        {"name": "React", "required": True},
        {"name": "AWS", "required": True},
        {"name": "AWS Lambda", "required": True},
        {"name": "DynamoDB", "required": True}
    ],
    "education": [],
    "languages": [],
    "responsibilities": [
        "Building infrastructure",
        "Evaluating AI coding agents",
        "Collaborating with engineering teams"
    ]
}

match_result = {
    "summary": {
        "match_percentage": 80
    }
}


letter = generate_cover_letter(
    job_profile=job_profile,
    candidate_profile=candidate_profile,
    match_result=match_result
)

print("\n==============================")
print("CARTA GENERADA")
print("==============================\n")
print(letter)