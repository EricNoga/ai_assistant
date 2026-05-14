import chromadb
from chromadb.config import Settings
from uuid import uuid4

# -----------------------------------
# CHROMADB CLIENT
# -----------------------------------

client = chromadb.Client(
    Settings(
        persist_directory="backend/memory_db"
    )
)

collection = client.get_or_create_collection(
    name="agent_memory"
)

# -----------------------------------
# ADD MEMORY
# -----------------------------------
def add_memory(
    text: str,
    metadata: dict = None
):
    """
    Store memory into vector DB
    """

    collection.add(
        documents=[text],
        metadatas=[metadata or {}],
        ids=[str(uuid4())]
    )


# -----------------------------------
# SEARCH MEMORY
# -----------------------------------
def search_memory(
    query: str,
    n_results: int = 3
):
    """
    Retrieve relevant memories
    """

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    if not results["documents"]:
        return []

    return results["documents"][0]


# -----------------------------------
# GET ALL MEMORIES
# -----------------------------------
def get_all_memories():

    return collection.get()


# -----------------------------------
# SIMPLE IMPORTANCE FILTER
# -----------------------------------
def is_important(text: str):
    """
    Basic heuristic for memory importance
    """

    important_keywords = [
        "error",
        "solution",
        "completed",
        "successful",
        "failed",
        "project",
        "task",
        "agent",
        "memory"
    ]

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in important_keywords
    )


# -----------------------------------
# MEMORY SUMMARIZATION
# -----------------------------------
def summarize_memory(memories: list):
    """
    Compress multiple memories
    into smaller chunks
    """

    if not memories:
        return ""

    summary = "\n".join(memories[:5])

    if len(summary) > 1000:
        summary = summary[:1000]

    return summary