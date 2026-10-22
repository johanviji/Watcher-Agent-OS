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

        if "download" in p_lower and ("pdf" in p_lower or "move" in p_lower):
            dl, doc = f"{home_dir}/Downloads", f"{home_dir}/Documents"
            print(f"\n[Guardrail Summary] Move every *.pdf in {dl} to {doc}.")
            if input("Confirm watch creation (y/n)? ").strip().lower() == 'y':
                return watch_directory(path=dl, pattern="*.pdf", action="move", destination=doc)
            return "Cancelled by user."
        return "Directory Watcher Agent received prompt, but requires valid parameters."