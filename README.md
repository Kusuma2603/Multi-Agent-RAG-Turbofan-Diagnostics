# ✈️ Turbofan Engine Diagnostic System
### Multi-Agent RAG Framework · Powered by Ollama · Runs 100% Locally

A production-style AI system that helps aviation maintenance engineers diagnose turbofan engine faults. Engineers describe symptoms in plain language; three specialist AI agents retrieve relevant maintenance records and generate a structured diagnostic report — all running locally with no data leaving the machine.

---

## 🏗️ Architecture

```
Engineer Query
      │
      ▼
┌─────────────┐
│ Orchestrator│  ── fans out query to 3 agents in parallel (ThreadPoolExecutor)
└─────────────┘
   │        │        │
   ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│Agent1│ │Agent2│ │Agent3│
│Fault │ │Symp. │ │Maint.│
│Class.│ │Anal. │ │Advis.│
└──────┘ └──────┘ └──────┘
   │        │        │
   └────────┴────────┘
            │
            ▼ (each agent)
      ChromaDB Query          ← semantic search via nomic-embed-text
            │
            ▼
      Ollama (llama3)          ← local LLM, no API calls
            │
            ▼
    Structured Report
```

**Each agent:**
1. Receives the engineer's query
2. Retrieves the top-3 most semantically similar fault records from ChromaDB
3. Calls Ollama (llama3) with its specialist system prompt + retrieved context
4. Returns a focused, structured response

| Agent | Role |
|---|---|
| **Fault Classifier** | Identifies fault type + confidence (Low/Medium/High) |
| **Symptom Analyzer** | Interprets sensor readings, pinpoints affected engine section |
| **Maintenance Advisor** | Recommends repair steps, parts needed, downtime, safety notes |

---

## 📁 Project Structure

```
turbofan_rag/
├── data/
│   └── generate_dataset.py   # Step 1: generate 48 synthetic fault scenarios
├── ingest.py                  # Step 2: embed scenarios into ChromaDB
├── agents.py                  # Step 3: three specialist RAG agents
├── orchestrator.py            # Step 4: parallel fan-out + report assembly
├── app.py                     # Step 5: Gradio web UI
└── requirements.txt
```

---

## ⚙️ Setup

> **Python 3.11 recommended.** Not tested on 3.12+.

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull required models
```bash
ollama pull llama3              # Main LLM for agents
ollama pull nomic-embed-text    # Embedding model for ChromaDB
```

### 3. Create Python environment
```bash
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Generate the synthetic dataset
```bash
python data/generate_dataset.py
# Creates: data/turbofan_faults.json  (~48 fault scenarios)
```

### 5. Ingest into ChromaDB
```bash
python ingest.py
# Creates: chroma_db/  (embedded vector store)
```

---

## 🚀 Run

Make sure Ollama is running first:
```bash
ollama serve          # in a separate terminal (if not already running)
```

**Gradio web UI:**
```bash
python app.py
# Opens: http://localhost:7860
```

**Command-line test (no UI):**
```bash
python orchestrator.py
```

---

## 🧪 Example Queries

Try these in the UI:
- *"EGT is spiking to 810°C during climb, vibration at 5.2 mils, some smoke from exhaust."*
- *"N1 fluctuating between 88% and 95% at cruise. Fuel flow seems higher than normal."*
- *"Strong vibration in the fan section, N2 stable, but we hear a grinding noise at idle."*
- *"Oil pressure dropped from 55 psi to 38 psi over the last 3 flight hours."*
- *"Compressor stall occurred twice during acceleration. EGT jumped to 790°C briefly."*

---

## 🔧 Customization

| What to change | Where | How |
|---|---|---|
| Use a faster model | `agents.py` | Change `LLM_MODEL = "llama3"` to `"mistral"` |
| More context per query | `agents.py` | Increase `TOP_K = 3` |
| Larger knowledge base | `data/generate_dataset.py` | Increase scenarios per fault type |
| Add a new fault type | `data/generate_dataset.py` | Add a new dict to `FAULT_TEMPLATES` |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM inference | [Ollama](https://ollama.com) (llama3) — local, no API key |
| Embeddings | nomic-embed-text via Ollama |
| Vector store | [ChromaDB](https://www.trychroma.com/) |
| Web UI | [Gradio](https://www.gradio.app/) |
| Parallelism | Python `concurrent.futures.ThreadPoolExecutor` |

---

## ⚠️ Disclaimer

This system uses **synthetic data** generated for demonstration purposes. It is a **decision support tool** and should never replace qualified aviation maintenance engineers or official AMM procedures.
