"""
Long-term Memory with ChromaDB + Strands Agent
================================================
Flow:
  1. User sends message
  2. Agent fetches relevant memories from ChromaDB
  3. Injects memories into system prompt (context)
  4. LLM answers with past knowledge
  5. Agent extracts and saves new facts to ChromaDB
"""

import uuid
import chromadb
from strands import Agent


# ─────────────────────────────────────────────
# STEP 1: Setup ChromaDB (Vector Database)
# ─────────────────────────────────────────────

# PersistentClient = saves to disk (remembers across runs)
# If you use Client() instead → saves to RAM only (lost on exit)
chroma_client = chromadb.PersistentClient(path="./long_term_memory")

# Collection = like a "table" in normal DB
# get_or_create_collection → loads existing or creates new
memory_collection = chroma_client.get_or_create_collection(
    name="agent_memory",

    # How similarity is measured when searching
    # cosine = compares meaning/direction of vectors (best for text)
    metadata={"hnsw:space": "cosine"}
)


# ─────────────────────────────────────────────
# STEP 2: Save Memory Function
# ─────────────────────────────────────────────

def save_memory(fact: str):
    """
    Save a fact to long-term memory (ChromaDB).

    ChromaDB automatically converts text → vector internally.
    Each memory needs a unique ID.
    """
    memory_collection.add(
        documents=[fact],           # the actual text fact
        ids=[str(uuid.uuid4())]     # unique ID for each memory
    )
    print(f"\n💾 Memory saved: {fact}")


# ─────────────────────────────────────────────
# STEP 3: Fetch Relevant Memory Function
# ─────────────────────────────────────────────

def fetch_memories(query: str, n_results: int = 3) -> str:
    """
    Search long-term memory for facts relevant to the query.

    ChromaDB converts query → vector, then finds
    closest matching vectors (most similar meanings).

    Returns them as a string to inject into context.
    """

    # Check if any memories exist first
    if memory_collection.count() == 0:
        return ""

    # Query = search by meaning, not exact text
    results = memory_collection.query(
        query_texts=[query],
        n_results=min(n_results, memory_collection.count())
    )

    memories = results["documents"][0]  # list of matching facts

    if not memories:
        return ""

    # Format memories as a string
    memory_str = "\n".join(f"- {m}" for m in memories)
    print(f"\n🔍 Relevant memories found:\n{memory_str}")
    return memory_str


# ─────────────────────────────────────────────
# STEP 4: Build System Prompt with Memories
# ─────────────────────────────────────────────

def build_system_prompt(user_query: str) -> str:
    """
    Fetch relevant memories and inject into system prompt.
    This is how long-term memory enters the context.
    """
    memories = fetch_memories(user_query)

    if memories:
        return f"""You are a helpful assistant with memory.

You remember these facts about the user from past conversations:
{memories}

Use this information naturally when relevant. Do not mention
that you are recalling from memory unless asked.
"""
    else:
        return "You are a helpful assistant."


# ─────────────────────────────────────────────
# STEP 5: Extract Facts from Conversation
# ─────────────────────────────────────────────

def extract_and_save_facts(user_message: str):
    """
    Simple fact extraction — in production you'd use
    an LLM to extract facts. Here we use keywords for simplicity.

    Real production approach:
      → send message to LLM
      → ask "what facts should I remember from this?"
      → save those facts
    """
    keywords = [
        "my name is", "i am from", "i live in",
        "i work at", "i prefer", "i like", "i hate",
        "i have", "my issue is", "my problem is",
        "i use", "i am a", "my email"
    ]

    msg_lower = user_message.lower()
    for keyword in keywords:
        if keyword in msg_lower:
            # Save the full sentence as a memory
            save_memory(user_message)
            break  # save once per message


# ─────────────────────────────────────────────
# STEP 6: Main Conversation Loop
# ─────────────────────────────────────────────

print("=== Agent with Long-term Memory ===")
print("Type 'exit' to quit")
print("Type 'show memories' to see all saved memories")
print("=" * 40)

while True:
    user_input = input("\nYou: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    # Show all saved memories
    if user_input.lower() == "show memories":
        all_memories = memory_collection.get()
        if all_memories["documents"]:
            print("\n📚 All saved memories:")
            for i, doc in enumerate(all_memories["documents"], 1):
                print(f"  {i}. {doc}")
        else:
            print("\n📭 No memories saved yet.")
        continue

    # ── Core Flow ──

    # 1. Extract and save any facts from user message
    extract_and_save_facts(user_input)

    # 2. Build system prompt with relevant memories injected
    system_prompt = build_system_prompt(user_input)

    # 3. Create agent with memory-aware system prompt
    #    Note: New agent each turn so system prompt updates with fresh memories
    agent = Agent(system_prompt=system_prompt)

    # 4. Send message to agent
    response = agent(user_input)

    print(f"\nAgent: {response}")