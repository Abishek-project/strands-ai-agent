from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@gongrzhe/server-gmail-autoauth-mcp"]
)

mcp_client = MCPClient(lambda: stdio_client(server_params))

with mcp_client:
    tools = mcp_client.list_tools_sync()

    print("=== Gmail Agent ===")
    print(f"✅ Connected to Gmail MCP Server")
    print(f"📦 Tools: {[t.tool_name for t in tools]}")
    print("=" * 40)

    agent = Agent(
        system_prompt="""You are a helpful Gmail assistant.
You can read, search, and send emails.
Always summarize emails clearly and concisely.""",
        tools=tools
    )

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break
        response = agent(user_input)
        print(f"\nAgent: {response}")