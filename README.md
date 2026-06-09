<!-- Steps to crate project -->
uv init
uv venv
source .venv/bin/activate

uv add strands-agents
uv add bedrock-agentcore-starter-toolkit    


<!-- Step to launch runtime -->
source .venv/bin/activate
agentcore configure -e main.py  
agentcore launch
agentcore invoke '{"prompt": "Hello"}
# strands-ai-agent
