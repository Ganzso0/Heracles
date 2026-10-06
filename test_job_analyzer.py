from pathlib import Path
import json

from llm.hardware import HardwareDetector
from llm.runtime import RuntimeSelector
from llm.manager import LLMManager
from llm.client import LLMClient

from analyzer.job_analyzer import analyze_job


BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# RUNTIME
# ==========================================

detector = HardwareDetector()
selector = RuntimeSelector(BASE_DIR)

use_vulkan = detector.has_vulkan()

server_path = selector.get_server_path(
    use_vulkan
)


# ==========================================
# MODELO
# ==========================================

model_path = (
    BASE_DIR
    / "models"
    / "Ministral-3-8B-Instruct-2512-Q4_K_M.gguf"
)


# ==========================================
# LLM MANAGER
# ==========================================

manager = LLMManager(
    server_path=server_path,
    model_path=model_path
)


try:

    print()
    print("==============================")
    print("INICIANDO LLM")
    print("==============================")

    manager.start_background()

    print("Esperando a que el modelo esté listo...")

    manager.wait_until_ready()

    print("✅ LLM listo")


    # ==========================================
    # CLIENT
    # ==========================================

    client = LLMClient()


    # ==========================================
    # OFERTA
    # ==========================================

    offer_file = BASE_DIR / "oferta.txt"

    with open(
        offer_file,
        "r",
        encoding="utf-8"
    ) as file:

        job_text = file.read()


    # ==========================================
    # ANALYZER
    # ==========================================

    print()
    print("==============================")
    print("ANALIZANDO OFERTA")
    print("==============================")

    job_profile = analyze_job(
        job_text,
        client
    )


    # ==========================================
    # RESULTADO
    # ==========================================

    print()
    print("==============================")
    print("JOB PROFILE")
    print("==============================")

    print(
        json.dumps(
            job_profile,
            indent=4,
            ensure_ascii=False
        )
    )


    # ==========================================
    # GUARDAR
    # ==========================================

    output_dir = BASE_DIR / "output"

    output_dir.mkdir(
        exist_ok=True
    )

    output_file = output_dir / "job_profile.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            job_profile,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(
        "✅ Guardado en:",
        output_file
    )


finally:

    manager.stop()