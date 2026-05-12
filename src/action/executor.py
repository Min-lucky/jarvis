import subprocess
import json
import os
import platform
import psutil
from pathlib import Path

# Load whitelist from config/permissions.json
PERM_PATH = Path(__file__).parents[2] / "config" / "permissions.json"
with open(PERM_PATH, "r", encoding="utf-8") as f:
    WHITELIST = json.load(f)

def _is_allowed(action: str, target: str) -> bool:
    if action == "get_system_info":
        return True # Safe read-only action
    allowed = WHITELIST.get(action, [])
    for entry in allowed:
        if target.lower().startswith(entry.lower()):
            return True
    return False

def execute_intent(uid: str, intent: dict):
    """Execute a structured intent.
    Supported actions: open_app, run_script, get_system_info, list_apps
    """
    action = intent.get("action")
    target = intent.get("target", "")
    args = intent.get("args", [])

    if not action:
        return False, {"error": "no action specified"}

    if not _is_allowed(action, target):
        return False, {"error": f"action {action} on {target} not whitelisted"}

    try:
        if action == "open_app":
            cmd = [target] + args
            subprocess.Popen(cmd, shell=False) # Use Popen so it doesn't block
            return True, {"message": f"Opening {target}"}
            
        elif action == "get_system_info":
            info = {
                "os": platform.system(),
                "version": platform.version(),
                "cpu_usage": f"{psutil.cpu_percent()}%",
                "memory_usage": f"{psutil.virtual_memory().percent}%",
                "disk_usage": f"{psutil.disk_usage('/').percent}%"
            }
            return True, info

        elif action == "run_script":
            script_path = Path(target)
            if not script_path.is_file():
                raise FileNotFoundError(f"Script {target} not found")
            if script_path.suffix.lower() in {".ps1", ".bat", ".cmd"}:
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)], check=True)
            else:
                subprocess.run([str(script_path)] + args, check=True)
            return True, {"message": f"Executed script {target}"}
            
        else:
            return False, {"error": f"unsupported action {action}"}
    except Exception as e:
        return False, {"exception": str(e)}
