import requests


class LLMClient:

    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        prompt,
        temperature=0.2,
        max_tokens=6000
    ):

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]