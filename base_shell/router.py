import os
from agents.directory_watcher.agent import DirectoryWatcherAgent

class AgentRouter:
    def __init__(self):
        # Registers available specialized agents in the shell ecosystem
        self.agents = {
            11: DirectoryWatcherAgent(),
            # Additional agents (1 to 35) can be registered here independently
        }

    def route_and_execute(self, user_prompt: str) -> str:
        """Routes natural language instructions to the appropriate specialized agent."""
        prompt_lower = user_prompt.lower()
        home_dir = os.path.expanduser("~")

        # Intent matching routing logic for Agent 11
        if any(keyword in prompt_lower for keyword in ["watch", "downloads", "pdf", "file watch", "folder"]):
            selected_agent = self.agents[11]
            print(f"[Router LLM] Intent matched -> Routing to Agent {selected_agent.agent_id}: {selected_agent.name}")
            return selected_agent.handle_request(user_prompt, home_dir)
            
        elif any(keyword in prompt_lower for keyword in ["kill", "cpu", "process", "memory"]):
            return "[Router LLM] Routed to Process Hunter Agent (Agent 1 - Independent Module)."
            
        return "[Router LLM] Error: Could not match prompt to any of the 35 specialized agents."