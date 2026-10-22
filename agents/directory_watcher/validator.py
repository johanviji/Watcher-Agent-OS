import os
import re

ALLOWED_ACTIONS = {"move", "copy", "rename", "compress"}
FORBIDDEN_PATHS = {"/", "/etc", "/proc", "/sys", "/dev", "/boot", "/usr", "/bin"}
DESTRUCTIVE_PATTERNS = [
    re.compile(r"rm\s+-rf", re.IGNORECASE),
    re.compile(r"mkfs", re.IGNORECASE),
    re.compile(r"dd\s+if", re.IGNORECASE),
    re.compile(r":\s*&?\s*\{.*\}", re.IGNORECASE)
]

def validate_rule(rule: dict) -> tuple[bool, str]:
    """Validates schema, action whitelists, and path safety guardrails[cite: 5]."""
    path = rule.get("path")
    destination = rule.get("destination")
    action = rule.get("action")
    pattern = rule.get("pattern", "*")

    if not path or not action:
        return False, "Missing required 'path' or 'action' fields."

    if action not in ALLOWED_ACTIONS:
        return False, f"Action '{action}' is not allowed. Whitelist: {ALLOWED_ACTIONS}"

    try:
        real_path = os.path.realpath(os.path.expanduser(path))
        home_dir = os.path.realpath(os.path.expanduser("~"))
    except Exception as e:
        return False, f"Invalid path resolution: {e}"

    if real_path in FORBIDDEN_PATHS:
        return False, f"Security violation: Watching system directory '{real_path}' is forbidden."

    if not real_path.startswith(home_dir):
        return False, f"Security violation: Path must reside within the user home directory ({home_dir})."

    if destination:
        real_dest = os.path.realpath(os.path.expanduser(destination))
        if real_dest in FORBIDDEN_PATHS:
            return False, f"Security violation: Destination '{real_dest}' is forbidden."
        if real_dest.startswith(real_path + os.sep) or real_dest == real_path:
            return False, "Loop protection error: Destination cannot be inside the watched directory."

    combined_text = f"{path} {destination} {pattern}"
    for pat in DESTRUCTIVE_PATTERNS:
        if pat.search(combined_text):
            return False, "Security violation: Destructive shell command pattern detected."

    return True, "Validation successful."