"""
RAG — Retrieval Augmented Generation
======================================
What it does:
  Loads YOUR document → splits into chunks → stores in ChromaDB
  When user asks → finds relevant chunks → agent answers from them

Steps:
  1. INDEXING  → load doc, chunk it, embed, store in ChromaDB
  2. RETRIEVAL → user asks, find relevant chunks
  3. GENERATION → inject chunks into context, agent answers

Run this file:
  First run  → indexes the document, then starts chat
  Later runs → document already indexed, just starts chat
"""

import chromadb
from strands import Agent


# ─────────────────────────────────────────────
# STEP 1: SETUP CHROMADB
# ─────────────────────────────────────────────

chroma_client = chromadb.PersistentClient(path="./rag_storage")

# Separate collection for RAG (different from long-term memory)
collection = chroma_client.get_or_create_collection(
    name="company_docs",
    metadata={"hnsw:space": "cosine"}
)


# ─────────────────────────────────────────────
# STEP 2: CHUNKING FUNCTION
# ─────────────────────────────────────────────

def chunk_document(text: str, chunk_size: int = 200) -> list[str]:
    """
    Split document into small chunks.

    Why chunk?
      - Can't fit entire document in context window
      - Smaller chunks = more precise retrieval
      - Only relevant chunks sent to LLM

    chunk_size = number of words per chunk
    """
    # Split by words
    words = text.split()
    chunks = []

    # Slide through words in chunk_size steps
    # overlap = 50 words → chunks share some words
    # Why overlap? So context isn't lost at chunk boundaries
    overlap = 50

    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]       # take chunk_size words
        chunks.append(" ".join(chunk))           # join back to string
        i += chunk_size - overlap                # move forward with overlap

    return chunks


# ─────────────────────────────────────────────
# STEP 3: INDEXING FUNCTION
# ─────────────────────────────────────────────

def index_document(file_path: str):
    """
    Load document → chunk → store in ChromaDB.

    This is done ONCE. Next time you run,
    document is already indexed — skips this step.
    """

    # Check if already indexed
    if collection.count() > 0:
        print(f"✅ Document already indexed ({collection.count()} chunks). Skipping.\n")
        return

    print(f"📄 Indexing document: {file_path}")

    # Load the document
    with open(file_path, "r") as f:
        text = f.read()

    # Split into chunks
    chunks = chunk_document(text)
    print(f"✂️  Split into {len(chunks)} chunks")

    # Store each chunk in ChromaDB
    # ChromaDB auto-converts text → vector (embedding)
    collection.add(
        documents=chunks,                              # list of chunk texts
        ids=[f"chunk_{i}" for i in range(len(chunks))]  # unique IDs
    )

    print(f"💾 Stored {len(chunks)} chunks in ChromaDB\n")


# ─────────────────────────────────────────────
# STEP 4: RETRIEVAL FUNCTION
# ─────────────────────────────────────────────

def retrieve_relevant_chunks(query: str, n_chunks: int = 3) -> str:
    """
    Find chunks most relevant to the user's question.

    How it works:
      1. ChromaDB converts query to vector
      2. Compares with all stored chunk vectors
      3. Returns top n_chunks most similar ones
    """
    results = collection.query(
        query_texts=[query],
        n_results=min(n_chunks, collection.count())
    )

    chunks = results["documents"][0]  # list of relevant chunks

    if not chunks:
        return "No relevant information found."

    # Join chunks into one string
    context = "\n\n---\n\n".join(chunks)

    print(f"\n🔍 Retrieved {len(chunks)} relevant chunks from document")
    return context


# ─────────────────────────────────────────────
# STEP 5: RAG AGENT
# ─────────────────────────────────────────────

def ask(question: str) -> str:
    """
    Full RAG pipeline for one question:
      1. Retrieve relevant chunks
      2. Build system prompt with chunks injected
      3. Create agent with that context
      4. Get answer
    """

    # Retrieve relevant chunks from ChromaDB
    relevant_context = retrieve_relevant_chunks(question)

    # Inject chunks into system prompt
    # This is how document knowledge enters the LLM context
    system_prompt = f"""You are a helpful assistant that answers questions
based ONLY on the provided document context below.

If the answer is not in the context, say "I don't have that information
in the document."

Do NOT use your general knowledge. Only use what's in the context.

DOCUMENT CONTEXT:
{relevant_context}
"""

    # Create fresh agent with document context
    agent = Agent(system_prompt=system_prompt)

    # Get answer
    return agent(question)


# ─────────────────────────────────────────────
# MAIN — Index document then start chat
# ─────────────────────────────────────────────

# Index the document (skips if already done)
index_document("company_policy.txt")

print("=== RAG — Company Policy Assistant ===")
print("Ask any question about company policy!")
print("Type 'exit' to quit")
print("=" * 40)

while True:
    user_input = input("\nYou: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    response = ask(user_input)
    print(f"\nAgent: {response}")