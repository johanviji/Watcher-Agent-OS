import os
from directory_watcher.agent import DirectoryWatcherAgent

def main():
    agent = DirectoryWatcherAgent()
    home_dir = os.path.expanduser("~")
    print("==================================================")
    print(" Agentic Shell for Linux - Directory Watcher Agent")
    print(" Type your natural language command or 'exit' to quit.")
    print("==================================================")

    while True:
        try:
            cmd = input("\nshell@agentic:~$ ").strip()
            if not cmd: 
                continue
            if cmd.lower() in {"exit", "quit"}: 
                print("Exiting shell.")
                break
            response = agent.process_request(cmd, home_dir)
            print(response)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()