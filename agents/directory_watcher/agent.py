import re
from agents.directory_watcher.mcp_server import watch_directory, list_watches, remove_watch

class DirectoryWatcherAgent:
    def __init__(self):
        self.name = "Directory Watcher Agent"
        self.agent_id = 11
        self.description = "Sets up persistent file-system watches using inotify for automated actions."

    def handle_request(self, user_prompt: str, home_dir: str) -> str:
        """Standardized agent interface called by the Base Shell router."""
        p_lower = user_prompt.lower()
        if "list" in p_lower: 
            return list_watches()
        if "remove" in p_lower:
            wid = next((w for w in user_prompt.split() if w.startswith("rule_")), "rule_1")
            return remove_watch(wid)

        # Dynamic parser for general watch requests (e.g., "Watch /etc and move files to /bin")
        if "watch" in p_lower:
            # Extract path after 'watch' and destination after 'to'
            path_match = re.search(r"watch\s+([^\s]+)", user_prompt, re.IGNORECASE)
            dest_match = re.search(r"to\s+([^\s]+)", user_prompt, re.IGNORECASE)
            
            path = path_match.group(1) if path_match else f"{home_dir}/Downloads"
            destination = dest_match.group(1) if dest_match else f"{home_dir}/Documents"
            
            pattern = "*.pdf" if "pdf" in p_lower else "*"
            action = "move" if "move" in p_lower else "copy"

            print(f"\n[Guardrail Summary] Action: {action} files matching '{pattern}' from {path} to {destination}.")
            confirm = input("Confirm watch creation (y/n)? ").strip().lower()
            
            if confirm == 'y':
                return watch_directory(path=path, pattern=pattern, action=action, destination=destination)
            return "Cancelled by user."

        return "Directory Watcher Agent received prompt, but requires valid parameters."