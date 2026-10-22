from directory_watcher.mcp_server import watch_directory, list_watches, remove_watch

class DirectoryWatcherAgent:
    def process_request(self, user_prompt: str, home_dir: str) -> str:
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
        return "Unable to parse request."