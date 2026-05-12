import subprocess
import json
import os
from pathlib import Path

# Load whitelist from config/permissions.json
PERM_PATH = Path(__file__).parents[2] / "config" / "permissions.json"
with open(PERM_PATH, "r", encoding="utf-8") as f:
    WHITELIST = json.load(f)

def _is_allowed(action: str, target: str) -> bool:
    allowed = WHITELIST.get(action, [])
    # allow exact match or prefix for scripts (e.g., "C:\\Scripts\\")
    for entry in allowed:
        if target.lower().startswith(entry.lower()):
            return True
    return False

def execute_intent(uid: str, intent: dict):
    """Execute a structured intent.

    Expected intent format:
    {
        "action": "open_app" | "run_script",
        "target": "executable or script path",
        "args": ["arg1", "arg2", ...]
    }
    Returns (success: bool, log_entry: dict).
    """
    action = intent.get("action")
    target = intent.get("target")
    args = intent.get("args", [])

    if not action or not target:
        return False, {"error": "malformed intent"}

    if not _is_allowed(action, target):
        return False, {"error": f"action {action} on {target} not whitelisted"}

    try:
        if action == "open_app":
            # Ensure the executable is found; rely on PATH if just name
            cmd = [target] + args
            subprocess.run(cmd, check=True, shell=False)
        elif action == "run_script":
            # For scripts we run via PowerShell (Windows) or bash (Linux)
            script_path = Path(target)
            if not script_path.is_file():
                raise FileNotFoundError(f"Script {target} not found")
            # Use PowerShell to execute .ps1 or .bat, otherwise default shell
            if script_path.suffix.lower() in {".ps1", ".bat", ".cmd"}:
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)], check=True, shell=False)
            else:
                subprocess.run([str(script_path)] + args, check=True, shell=False)
        else:
            return False, {"error": f"unsupported action {action}"}
    except Exception as e:
        return False, {"exception": str(e)}

    return True, {"action": action, "target": target, "args": args}
