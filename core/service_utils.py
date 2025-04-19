# --------------------------------------------------------------------
# ⚙️ SERVICE UTILS: Helpers to control the systemd service
# --------------------------------------------------------------------

import subprocess


def run_service_command(command: str, service_name: str = "inactivity-monitor") -> str:
    """
    Run a systemctl command (start, stop, restart) for the given service.

    Args:
        command (str): One of "start", "stop", or "restart".
        service_name (str): Name of the systemd service. Default: "inactivity-monitor".

    Returns:
        str: Command output (stdout or error message)

    Raises:
        ValueError: If the command is not supported.
        RuntimeError: If the systemctl command fails.
    """
    command_dict = {
        "start": f"sudo systemctl start {service_name}",
        "stop": f"sudo systemctl stop {service_name}",
        "restart": f"sudo systemctl restart {service_name}",
    }

    cmd = command_dict.get(command)
    if not cmd:
        raise ValueError(f"Unsupported command: {command}")

    try:
        result = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr.strip()}")
