from strands import Agent

agent = Agent()  # one session, stays alive

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break
        print(f"Agent: {agent(user_input)}")