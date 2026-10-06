from pathlib import Path

from llm.hardware import HardwareDetector
from llm.runtime import RuntimeSelector
from llm.manager import LLMManager
from llm.client import LLMClient


BASE_DIR = Path(__file__).resolve().parent


detector = HardwareDetector()
selector = RuntimeSelector(BASE_DIR)

use_vulkan = detector.has_vulkan()

server_path = selector.get_server_path(
    use_vulkan
)

model_path = (
    BASE_DIR
    / "models"
    / "Ministral-3-8B-Instruct-2512-Q4_K_M.gguf"
)


manager = LLMManager(
    server_path=server_path,
    model_path=model_path
)


try:

    print("Iniciando LLM en segundo plano...")

    manager.start_background()

    print("El programa puede continuar mientras arranca el servidor.")

    manager.wait_until_ready()

    print("El LLM ya está listo para usarse.")

    client = LLMClient()

    response = client.generate(
        "Explica en una frase qué es Heracles."
    )

    print()
    print("RESPUESTA:")
    print(response)

finally:

    manager.stop()