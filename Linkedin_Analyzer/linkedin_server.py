import json
from pathlib import Path

from flask import Flask, request, jsonify

from linkedin_analyzer import LinkedInAnalyzer


PROFILE_FILE = "C:/hlocal2/JobHunter/profile/master_profile.json"


with open(
    PROFILE_FILE,
    "r",
    encoding="utf-8"
) as file:

    candidate_profile = json.load(file)


app = Flask(__name__)

linkedin_analyzer = LinkedInAnalyzer(candidate_profile)


@app.post("/analyze")
def analyze():

    data = request.get_json()

    result = linkedin_analyzer.analyze({
        "description": data["description"]
    })

    return jsonify(result)


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8000
    )