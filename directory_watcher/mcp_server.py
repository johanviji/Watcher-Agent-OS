import os
import json
import signal
import platform
from directory_watcher.validator import validate_rule

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")
PID_FILE = os.path.join(os.path.dirname(__file__), "watcher.pid")

def _signal_daemon():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
                if platform.system() == "Windows":
                    # Windows doesn't support SIGHUP; daemon file watcher handles reloads or we can touch rules
                    pass
                else:
                    os.kill(pid, signal.SIGHUP)
        except Exception:
            pass

def _load_all_rules():
    if not os.path.exists(RULES_FILE): 
        return []
    try:
        with open(RULES_FILE, "r") as f: 
            return json.load(f)
    except Exception: 
        return []

def _save_all_rules(rules):
    with open(RULES_FILE, "w") as f: 
        json.dump(rules, f, indent=2)

def watch_directory(path: str, pattern: str, action: str, destination: str = None, recursive: bool = False) -> str:
    rule_obj = {
        "id": f"rule_{len(_load_all_rules()) + 1}",
        "path": path, 
        "pattern": pattern, 
        "action": action,
        "destination": destination, 
        "recursive": recursive, 
        "active": True
    }
    is_valid, msg = validate_rule(rule_obj)
    if not is_valid: 
        return f"Error: {msg}"

    rules = _load_all_rules()
    if len(rules) >= 20: 
        return "Error: Limit of 20 active rules reached."
    
    rules.append(rule_obj)
    _save_all_rules(rules)
    _signal_daemon()
    return f"Success: Watch {rule_obj['id']} created for {path} ({pattern}) -> {action}."

def list_watches() -> str:
    rules = _load_all_rules()
    if not rules: 
        return "No active watches found."
    return "\n".join([f"[{r['id']}] {r['path']} | {r['pattern']} -> {r['action']}" for r in rules])

def remove_watch(watch_id: str) -> str:
    rules = _load_all_rules()
    new_rules = [r for r in rules if r["id"] != watch_id]
    if len(new_rules) == len(rules): 
        return f"Error: Watch ID not found."
    _save_all_rules(new_rules)
    _signal_daemon()
    return f"Success: Watch {watch_id} deleted."