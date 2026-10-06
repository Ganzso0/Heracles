from pathlib import Path


class RuntimeSelector:

    def __init__(self, base_dir: Path):

        self.base_dir = base_dir

    def get_server_path(self, use_vulkan: bool):

        if use_vulkan:

            return (
                self.base_dir
                / "runtime"
                / "vulkan"
                / "llama-server.exe"
            )

        return (
            self.base_dir
            / "runtime"
            / "cpu"
            / "llama-server.exe"
        )