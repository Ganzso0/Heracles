from pathlib import Path

from core.heracles import Heracles

from llm.hardware import HardwareDetector
from llm.runtime import RuntimeSelector
from llm.manager import LLMManager


BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config" / "config.json"
PROFILE_FILE = BASE_DIR / "profile" / "master_profile.json"


def main():

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

    llm_manager = LLMManager(
        server_path=server_path,
        model_path=model_path
    )

    try:

        print("🤖 Preparando IA local...")

        llm_manager.start_background()

        heracles = Heracles(
            config_file=CONFIG_FILE,
            profile_file=PROFILE_FILE,
            llm_manager=llm_manager
        )

        heracles.run()

    finally:

        llm_manager.stop()


if __name__ == "__main__":
    main()