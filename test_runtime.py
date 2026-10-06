from pathlib import Path

from llm.hardware import HardwareDetector
from llm.runtime import RuntimeSelector


BASE_DIR = Path(__file__).resolve().parent

detector = HardwareDetector()
selector = RuntimeSelector(BASE_DIR)

use_vulkan = detector.has_vulkan()

server = selector.get_server_path(
    use_vulkan
)

print("Vulkan disponible:", use_vulkan)
print("Runtime elegido:", server)