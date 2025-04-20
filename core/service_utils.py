# --------------------------------------------------------------------
# ⚙️ SERVICE UTILS: Helpers to control the systemd service
# --------------------------------------------------------------------
# This module provides a unified function to:
# - Start, stop, or restart the systemd service via a privileged script
# - Use `pkexec` to trigger a helper script with root access
# --------------------------------------------------------------------

import subprocess
import os


def run_service_command(command: str) -> str:
    """
    Run a systemd command (start, stop, restart) through a privileged helper script.

    This function delegates service control to a Python helper script
    (scripts/control_service_helper.py) and uses `pkexec` to request
    elevated privileges.

    Args:
        command (str): One of "start", "stop", or "restart".

    Returns:
        str: The stdout message returned by the helper script.

    Raises:
        ValueError: If the command is not supported.
        RuntimeError: If the helper script fails or is missing.
    """
    if command not in ["start", "stop", "restart"]:
        raise ValueError(f"Unsupported command: {command}")

    # Compute absolute path to the helper script
    helper_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "control_service_helper.py"
    )

    if not os.path.exists(helper_path):
        raise RuntimeError(f"Missing helper script: {helper_path}")

    try:
        result = subprocess.run(
            ["pkexec", "python3", helper_path, command],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Service control failed: {e.stderr.strip()}")
