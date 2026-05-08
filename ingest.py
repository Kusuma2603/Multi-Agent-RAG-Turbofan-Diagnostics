"""
Step 2: Embed dataset and store in ChromaDB.
Run after: python data/generate_dataset.py
"""

import json
import os
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# ─── Configuration ────────────────────────────────────────────────────────────
OLLAMA_URL  = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHROMA_PATH = "./chroma_db"
COLLECTION  = "turbofan_docs"

# Fixed path: data/turbofan_faults.json (was incorrectly data/data/...)
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "turbofan_faults.json")


# ─── Build Document Text ──────────────────────────────────────────────────────
def build_document_text(scenario: dict) -> str:
    sensor = scenario.get("sensor_readings", {})

    return (
        f"Fault Type: {scenario.get('fault_type', 'unknown')}\n"
        f"Symptoms: {', '.join(scenario.get('symptoms', []))}\n"
        f"Sensor Readings: "
        f"EGT={sensor.get('EGT_degC', 'NA')}°C, "
        f"N1={sensor.get('N1_percent', 'NA')}%, "
        f"N2={sensor.get('N2_percent', 'NA')}%, "
        f"Vibration={sensor.get('vibration_mils', 'NA')} mils\n"
        f"Severity: {scenario.get('severity', 'unknown')}\n"
        f"Recommended Action: {scenario.get('recommended_action', 'NA')}\n"
        f"Notes: {scenario.get('notes', '')}"
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: Dataset not found at {DATA_FILE}")
        print("Please run: python data/generate_dataset.py")
        return

    print(f"Loading dataset from: {DATA_FILE}")
    with open(DATA_FILE) as f:
        scenarios = json.load(f)

    print(f"  Found {len(scenarios)} scenarios.\n")

    print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    embedding_fn = OllamaEmbeddingFunction(
        model_name=EMBED_MODEL,
        url=f"{OLLAMA_URL}/api/embeddings",
    )

    collection = client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=embedding_fn,
    )

    ids, documents, metadatas = [], [], []

    for s in scenarios:
        try:
            doc_id = f"scenario_{s.get('id', 'unknown')}"
            ids.append(doc_id)
            documents.append(build_document_text(s))
            metadatas.append({
                "fault_type": s.get("fault_type", "unknown"),
                "severity": s.get("severity", "unknown"),
            })
        except Exception as e:
            print(f"  Skipping bad record: {e}")

    print(f"Embedding and storing {len(ids)} documents...")
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(f"✅ Done! Collection '{COLLECTION}' now has {collection.count()} documents.")


if __name__ == "__main__":
    main()
