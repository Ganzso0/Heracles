import subprocess


class HardwareDetector:

    @staticmethod
    def has_vulkan():

        try:
            result = subprocess.run(
                ["vulkaninfo", "--summary"],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0

        except (
            FileNotFoundError,
            subprocess.SubprocessError
        ):
            return False