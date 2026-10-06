from llm.client import LLMClient


client = LLMClient()

response = client.generate(
    "Explica en una frase qué es Python."
)

print()
print("RESPUESTA:")
print(response)