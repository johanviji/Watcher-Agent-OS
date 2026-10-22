import os
from base_shell.router import AgentRouter

def main():
    router = AgentRouter()
    print("==================================================")
    print(" Agentic Shell for Linux - Multi-Agent System    ")
    print(" Loaded Independent Specialized Agents            ")
    print("==================================================")

    while True:
        try:
            user_input = input("\nshell@agentic:~$ ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting Agentic Shell. Goodbye!")
                break

            response = router.route_and_execute(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()