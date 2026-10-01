import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.job_analyzer import analyze_job
from matcher.match_engine import match_job


class LinkedInAnalyzer:

    def __init__(self, candidate_profile):
        self.candidate_profile = candidate_profile

    def analyze(self, job):
        job_text =job["description"]


        job_profile = analyze_job(job_text)

        match_result = match_job(
            job_profile,
            self.candidate_profile
        )

        summary = match_result["summary"]

        match_percentage = summary["match_percentage"]

        return {
            "match_percentage": match_percentage
        }