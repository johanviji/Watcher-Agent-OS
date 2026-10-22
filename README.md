Agentic Shell for Linux - Directory Watcher Agent (Agent 11)

An autonomous, multi-agent terminal framework for Linux. This repository implements an intelligent base shell router and a decoupled, domain-specific Directory Watcher Agent (Agent 11) capable of monitoring Linux file-system events in real-time via inotify system calls and performing automated file operations safely.

Architecture Overview

The system is designed around a modular, extensible multi-agent architecture capable of scaling to multiple specialized agents (e.g., Process Hunter, Zombie Reaper, CPU Affinity Managers).

agentic_shell_root/
├── base_shell/
│   ├── __init__.py
│   └── router.py          # Central Router LLM dispatching requests to agents
│
├── agents/
│   ├── __init__.py
│   └── directory_watcher/ # Agent 11 (Modular Domain Agent)
│       ├── __init__.py
│       ├── validator.py   # Security guardrails & path safety checks
│       ├── daemon.py      # Background inotify worker process
│       ├── mcp_server.py  # MCP tools and rule store management
│       └── agent.py       # Domain-specific agent logic & request handler
│
├── main.py                # Global REPL Shell entry point
└── requirements.txt       # Dependencies


Core Components

Base Shell & Router (base_shell/router.py): Intercepts natural language inputs, identifies intent, and dynamically routes tasks to the responsible specialized agent.

MCP Tooling Layer (agents/directory_watcher/mcp_server.py): Exposes structured capabilities (watch_directory, list_watches, remove_watch) and persists rule configurations.

Real-time Linux Daemon (agents/directory_watcher/daemon.py): A low-level C-library wrapper (libc.so.6) invoking inotify_init1 and inotify_add_watch to monitor file-system events (IN_CLOSE_WRITE, IN_MOVED_TO) with zero poll latency.

Security & Guardrail Validator (agents/directory_watcher/validator.py): Enforces path safety (blocks monitoring/writing to root directories like /etc, /bin, /proc), validates action whitelists, prevents loop conditions, and inspects inputs for destructive shell commands.

Key Features

Natural Language Parsing: Accepts conversational Linux tasks (e.g., "Watch my downloads folder and automatically move any PDF files to my Documents").

Safety Guardrails: Human-in-the-loop confirmation prompts and automated path validation before rule registration.

Low-Overhead Event Monitoring: Utilizes native Linux inotify syscalls rather than CPU-intensive loop polling.

Dynamic Rule Reloading: Inter-process communication (IPC) via SIGHUP signals allowing the background daemon to update rules seamlessly without restarting.

System Requirements

OS: Linux or WSL (Windows Subsystem for Linux - Ubuntu).

Python: Version 3.8+

Linux C Library: libc.so.6 (standard on Debian/Ubuntu environments).

Setup & Installation

1. Install System Dependencies (WSL / Ubuntu)

Ensure python3-pip and Python build tools are installed:

sudo apt update && sudo apt install python3-pip -y


2. Install Project Dependencies

Navigate to your project root directory and run:

pip3 install -r requirements.txt


How to Run

Running the agent system requires two terminal windows (or two tabs inside WSL):

Terminal 1: Start the Inotify Background Daemon

The daemon runs as a persistent background worker listening for file system events and SIGHUP signals:

python3 -m agents.directory_watcher.daemon


Terminal 2: Start the Interactive Base Shell

Launch the main user interface:

python3 main.py


Sample Usage & Test Scenarios

Run these commands inside the shell@agentic:~$ interactive prompt:

Scenario 1: Create a Persistent File Watch

shell@agentic:~$ watch my downloads folder and automatically move any pdf files to my documents.


Behavior:

The Router identifies the intent and delegates to Agent 11.

The Guardrail validator checks path safety and prints a summary.

Enter y when prompted to confirm.

The rule is written to rules.json and a SIGHUP signal refreshes the daemon.

Scenario 2: List Active Watches

shell@agentic:~$ List all active watches


Behavior: Displays all registered file watches, their paths, matching patterns, and corresponding actions.

Scenario 3: Test Security Guardrails (Forbidden System Directory)

shell@agentic:~$ Watch /etc and move files to /bin


Behavior: The request is routed to Agent 11, but the security guardrail halts execution and returns:
Error: Security violation: Watching system directory '/etc' is forbidden.

Scenario 4: Remove a Watch Rule

shell@agentic:~$ Remove rule_1


Behavior: Deletes rule_1 from the active configurations and updates the background daemon immediately.
