# Agentic Shell for Linux – Agent 11: Directory Watcher Agent

This project is part of the **Agentic Shell for Linux** multi-agent system[cite: 1, 2]. **Agent 11 (Directory Watcher Agent)** provides persistent, event-driven file-system monitoring using the Linux `inotify` API. Rather than executing one-off terminal commands, it translates natural language requests into structured, validated watch rules that run as background daemons[cite: 2, 3, 9].

---

## 🏗️ System Architecture & Design

The system follows a decoupled, multi-tier agentic architecture:
1. **Interface Layer (Base Shell REPL):** Accepts plain English user input and routes intent[cite: 2].
2. **Orchestration Layer (Router & Agent):** Dispatches requests to specialized agents (e.g., Agent 11)[cite: 2].
3. **Tooling Layer (MCP Server):** Exposes validated tools (`watch_directory`, `list_watches`, `remove_watch`).
4. **Security & Guardrail Framework:** Enforces path safety (`os.path.realpath`), action whitelists (`move`, `copy`, `rename`, `compress`), destructive command blacklisting, and human-in-the-loop confirmation before saving rules[cite: 3, 5].
5. **Data Path (Watcher Daemon):** A background process utilizing Linux `inotify` via `ctypes` and `select()` multiplexing to apply rules instantly when file events occur[cite: 2, 3].

---

## 📁 Project Directory Structure

```text
agentic_shell_root/
│
├── base_shell/
│   ├── __init__.py
│   └── router.py          # Central Router LLM dispatching requests to agents
│
├── agents/
│   ├── __init__.py
│   └── directory_watcher/ # Agent 11 Module
│       ├── __init__.py
│       ├── validator.py   # Security guardrails & path safety checks
│       ├── daemon.py      # Background inotify daemon
│       ├── mcp_server.py  # MCP tools and rule store management[cite: 2, 3]
│       └── agent.py       # Domain-specific agent logic & request handler
│
├── main.py                # Global entry point / Interface Layer (REPL)[cite: 2]
└── requirements.txt       # Project dependencies[cite: 6]
