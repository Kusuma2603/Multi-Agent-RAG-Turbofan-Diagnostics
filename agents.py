"""
Step 3: Three specialist agents, each with a focused system prompt and RAG retrieval.
Each agent retrieves relevant context from ChromaDB, then calls Ollama to answer.
"""

import chromadb
import ollama
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# ─── Configuration ────────────────────────────────────────────────────────────
LLM_MODEL    = "llama3"
EMBED_MODEL  = "nomic-embed-text"
OLLAMA_URL   = "http://localhost:11434"
CHROMA_PATH  = "./chroma_db"
COLLECTION   = "turbofan_docs"
TOP_K        = 3   # Number of similar docs to retrieve


# ─── Shared ChromaDB connection ───────────────────────────────────────────────
_chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
_embedding_fn = OllamaEmbeddingFunction(
    model_name=EMBED_MODEL,
    url=f"{OLLAMA_URL}/api/embeddings",
)
_collection = _chroma_client.get_or_create_collection(
    name=COLLECTION,
    embedding_function=_embedding_fn,
)


def retrieve_context(query: str) -> str:
    """Retrieve the top-K most relevant documents from ChromaDB."""
    count = _collection.count()
    if count == 0:
        return "No maintenance records found. Please run ingest.py first."

    results = _collection.query(
        query_texts=[query],
        n_results=min(TOP_K, count),
    )
    docs = results.get("documents", [[]])[0]
    if not docs:
        return "No relevant maintenance records found."
    return "\n\n---\n\n".join(docs)


def call_ollama(system_prompt: str, user_message: str) -> str:
    """Send a message to Ollama and return the response text."""
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_message},
            ],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "ConnectError" in error_msg:
            return (
                "ERROR: Cannot connect to Ollama. "
                "Please start it with: ollama serve"
            )
        return f"ERROR: Ollama call failed — {error_msg}"


# ─── Agent 1: Fault Classifier ────────────────────────────────────────────────
FAULT_CLASSIFIER_PROMPT = """You are a turbofan engine fault classification expert.
Your ONLY job is to identify the most likely fault type based on the engineer's description
and the retrieved maintenance records provided.

Be concise. State the fault type, confidence level (Low/Medium/High), and one sentence of reasoning.
Format your answer as:
Fault Type: <name>
Confidence: <Low|Medium|High>
Reasoning: <one sentence>"""


def fault_classifier_agent(query: str) -> str:
    context = retrieve_context(query)
    user_msg = f"Engineer's description:\n{query}\n\nRelevant maintenance records:\n{context}"
    return call_ollama(FAULT_CLASSIFIER_PROMPT, user_msg)


# ─── Agent 2: Symptom Analyzer ────────────────────────────────────────────────
SYMPTOM_ANALYZER_PROMPT = """You are a turbofan engine symptom analysis expert.
Your ONLY job is to interpret the sensor readings and observable symptoms described by the engineer.
Compare them against the retrieved maintenance records.

Identify which readings are anomalous, what they indicate, and which engine section is affected.
Be concise and use bullet points."""


def symptom_analyzer_agent(query: str) -> str:
    context = retrieve_context(query)
    user_msg = f"Engineer's description:\n{query}\n\nRelevant maintenance records:\n{context}"
    return call_ollama(SYMPTOM_ANALYZER_PROMPT, user_msg)


# ─── Agent 3: Maintenance Advisor ─────────────────────────────────────────────
MAINTENANCE_ADVISOR_PROMPT = """You are a turbofan engine maintenance advisor.
Your ONLY job is to recommend the next maintenance action based on the fault description
and retrieved maintenance records.

Provide: immediate action, parts likely needed, estimated downtime, and safety precautions.
Be specific and practical. Use numbered steps."""


def maintenance_advisor_agent(query: str) -> str:
    context = retrieve_context(query)
    user_msg = f"Engineer's description:\n{query}\n\nRelevant maintenance records:\n{context}"
    return call_ollama(MAINTENANCE_ADVISOR_PROMPT, user_msg)
