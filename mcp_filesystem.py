"""
MCP — Connect to Filesystem MCP Server
========================================
What this does:
  → connects to filesystem MCP server
  → server runs locally on your computer
  → agent can list, read, write files
  → all through MCP protocol

How it works:
  Your Agent (MCP Client)
        ↓ connects via stdio
  Filesystem MCP Server (runs locally)
        ↓
  Your actual files on disk
"""

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


# ─────────────────────────────────────────────
# WHAT IS stdio?
# ─────────────────────────────────────────────
# stdio = Standard Input/Output
# It's how your agent talks to local MCP server
#
# Like two people passing text notes:
#   Agent writes note → MCP Server reads it
#   MCP Server writes reply → Agent reads it
#
# This happens through command line pipes
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
# STEP 1: Define MCP Server Parameters
# ─────────────────────────────────────────────

# StdioServerParameters = how to START the MCP server
# command = what program to run
# args    = arguments to pass to it
#           first arg = path agent can access

import os

# Agent will have access to current directory
current_dir = os.getcwd()

server_params = StdioServerParameters(
    command="npx",                                          # use npx to run
    args=[
        "-y",                                               # auto confirm install
        "@modelcontextprotocol/server-filesystem",          # filesystem MCP server
        current_dir                                         # folder agent can access
    ]
)


# ─────────────────────────────────────────────
# STEP 2: Create MCP Client
# ─────────────────────────────────────────────

# MCPClient = your agent's connection to MCP server
# lambda    = function that creates the connection
# stdio_client(server_params) = connect via stdio

mcp_client = MCPClient(lambda: stdio_client(server_params))


# ─────────────────────────────────────────────
# STEP 3: Connect and Use
# ─────────────────────────────────────────────

# "with mcp_client:" = connect to server
# When block ends   = disconnect cleanly

with mcp_client:

    # Get all tools MCP server provides
    tools = mcp_client.list_tools_sync()

    print("=== MCP Filesystem Agent ===")
    print(f"✅ Connected to Filesystem MCP Server")
    print(f"📦 Available tools: {[t.tool_name for t in tools]}")
    print(f"📁 Agent has access to: {current_dir}")
    print("=" * 40)

    # Create agent with MCP tools
    agent = Agent(
        system_prompt=f"""You are a helpful file assistant.
You have access to the filesystem at: {current_dir}
You can list, read, and write files there.
Always show file contents clearly when reading.""",
        tools=tools
    )

    # Conversation loop
    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break

        response = agent(user_input)
        print(f"\nAgent: {response}")