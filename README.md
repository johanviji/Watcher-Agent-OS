# Agentic Shell for Linux – Agent 11: Directory Watcher Agent by Johan and Neeraj

This project is part of the **Agentic Shell for Linux** multi-agent system[cite: 1, 2]. **Agent 11 (Directory Watcher Agent)** provides persistent, event-driven file-system monitoring using the Linux `inotify` API. Rather than executing one-off terminal commands, it translates natural language requests into structured, validated watch rules that run as background daemons[cite: 2, 3, 9].

---

## System Architecture & Design

The system follows a decoupled, multi-tier agentic architecture:
1. **Interface Layer (Base Shell REPL):** Accepts plain English user input and routes intent[cite: 2].
2. **Orchestration Layer (Router & Agent):** Dispatches requests to specialized agents (e.g., Agent 11)[cite: 2].
3. **Tooling Layer (MCP Server):** Exposes validated tools (`watch_directory`, `list_watches`, `remove_watch`).
4. **Security & Guardrail Framework:** Enforces path safety (`os.path.realpath`), action whitelists (`move`, `copy`, `rename`, `compress`), destructive command blacklisting, and human-in-the-loop confirmation before saving rules[cite: 3, 5].
5. **Data Path (Watcher Daemon):** A background process utilizing Linux `inotify` via `ctypes` and `select()` multiplexing to apply rules instantly when file events occur[cite: 2, 3].

---

##  Project Directory Structure

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

Navigate to the project root directory:

Bash
cd path/to/agentic_shell_root
Install python3-pip if it is not already installed:

Bash
sudo apt update && sudo apt install python3-pip -y
Install required Python packages:

Bash
pip3 install -r requirements.txt




How to Run the Program
To run the program with persistent background event monitoring, open two separate terminal windows/tabs inside your project root directory (agentic_shell_root/):

Terminal Window 1: Start the Background Daemon
In the first terminal window, start the inotify background process:

Bash
python3 -m agents.directory_watcher.daemon
Note: On Linux/WSL, this detaches as a background worker. It reads active configurations from rules.json and monitors system events.

Terminal Window 2: Launch the Interactive Agentic Shell
In the second terminal window, start the main shell interface:

Bash
python3 main.py
This launches the interactive prompt (shell@agentic:~$) where you can type natural language instructions.









## some basic test cases:

Testing Output Scenarios
Once the shell prompt (shell@agentic:~$) is active, you can test all system capabilities:

1. Create a File Watch (Primary Use Case)
Input:

Plaintext
shell@agentic:~$ watch my downloads folder and automatically move any pdf files to my documents.
Output & Behavior:
The router matches the intent, presents a guardrail validation summary, and prompts:Confirm watch creation (y/n)?
Typing y saves the rule to rules.json, signals the daemon via SIGHUP, and outputs:

Plaintext
Success: Watch rule_1 created for /home/user/Downloads (*.pdf) -> move.
2. List Active Watches
Input:

Plaintext
shell@agentic:~$ List all active watches
Output & Behavior:
Displays all running rules managed in rules.json:

Plaintext
[rule_1] /home/user/Downloads | *.pdf -> move
3. Security Guardrail Test (Forbidden System Paths)
Input:

Plaintext
shell@agentic:~$ Watch /etc and move files to /bin
Output & Behavior:
The validator intercepts forbidden system paths and blocks execution:

Plaintext
Error: Security violation: Watching system directory '/etc' is forbidden.
4. Remove an Existing Watch
Input:

Plaintext
shell@agentic:~$ Remove rule_1
Output & Behavior:
Removes the target rule from rules.json and updates the background daemon:

Plaintext
Success: Watch rule_1 deleted.
