"""
Multi-Agent System — Agents as Tools
======================================
Pattern: One main agent (orchestrator) uses
         specialist agents as tools.

Two ways to use agents as tools in Strands:
  1. Pass agent directly in tools list (simplest)
  2. Use .as_tool() with name and description

System: Content Creation Pipeline
  ├── Researcher Agent  → researches the topic
  ├── Writer Agent      → writes the content
  └── Reviewer Agent    → reviews and improves
"""

from strands import Agent


# ─────────────────────────────────────────────
# SPECIALIST AGENT 1: Researcher
# name        = tool name main agent uses
# description = main agent reads this to decide when to call
# ─────────────────────────────────────────────

researcher_agent = Agent(
    name="research_topic",
    description="Research a topic and return key facts, trends and statistics. Always use this first before writing anything.",
    system_prompt="""You are an expert researcher.
Your ONLY job is to research a given topic and return:
- 3 to 5 key facts
- Current trends
- Important statistics if any

Be factual, concise, and well structured.
Do NOT write articles. Just research points."""
)


# ─────────────────────────────────────────────
# SPECIALIST AGENT 2: Writer
# ─────────────────────────────────────────────

writer_agent = Agent(
    name="write_article",
    description="Write a short article based on research points. Use this after researching the topic.",
    system_prompt="""You are an expert content writer.
Your ONLY job is to take research points and write
a clean, engaging short article (200-300 words).

- Use simple language
- Clear structure with intro, body, conclusion
- Make it interesting to read"""
)


# ─────────────────────────────────────────────
# SPECIALIST AGENT 3: Reviewer
# ─────────────────────────────────────────────

reviewer_agent = Agent(
    name="review_article",
    description="Review and improve a written article. Give quality score and return final improved version. Use this after writing.",
    system_prompt="""You are an expert content reviewer.
Your ONLY job is to review an article and:
- Fix grammar and clarity issues
- Improve weak sentences
- Give a quality score out of 10
- Return the improved final version

Format your response as:
SCORE: X/10
FEEDBACK: (what you improved)
FINAL ARTICLE: (improved version)"""
)


# ─────────────────────────────────────────────
# MAIN AGENT (Orchestrator)
# Pass specialist agents directly in tools list
# Strands automatically converts them to tools
# ─────────────────────────────────────────────

main_agent = Agent(
    system_prompt="""You are a content creation orchestrator.
When user gives you a topic, follow these steps IN ORDER:

Step 1: Use research_topic   → get research on the topic
Step 2: Use write_article    → write article using that research
Step 3: Use review_article   → review and improve the article

Then present the final result clearly to the user.
Always follow all 3 steps. Never skip any step.""",

    tools=[
        researcher_agent,   # agent passed directly as tool ✅
        writer_agent,
        reviewer_agent,
    ]
)


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────m

print("=== Multi-Agent Content Creator ===")
print("Give me any topic → I will research, write and review it!")
print("Type 'exit' to quit")
print("=" * 40)

while True:
    user_input = input("\nYou: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    print("\n⚙️  Working... (research → write → review)\n")
    response = main_agent(user_input)
    print(f"\nFinal Result:\n{response}")