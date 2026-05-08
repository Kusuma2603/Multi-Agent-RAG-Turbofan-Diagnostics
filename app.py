import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
import json
from orchestrator import run_diagnostic, format_report

EXAMPLES = [
    "EGT is spiking to 810°C during climb, vibration at 5.2 mils, some smoke from exhaust.",
    "N1 fluctuating between 88% and 95% at cruise. Fuel flow seems higher than normal.",
    "Strong vibration in the fan section, N2 stable, but we hear a grinding noise at idle.",
    "Oil pressure dropped from 55 psi to 38 psi over the last 3 flight hours.",
    "Compressor stall occurred twice during acceleration. EGT jumped to 790°C briefly.",
]


def diagnose(query: str):
    if not query.strip():
        return "Please enter a description of the fault or symptoms."
    try:
        report = run_diagnostic(query)
        formatted = format_report(report)
        if isinstance(formatted, dict):
            return json.dumps(formatted, indent=2)
        return str(formatted)
    except Exception as e:
        return (
            f"Error running diagnostic:\n{str(e)}\n\n"
            "Make sure Ollama is running:\n> ollama serve"
        )


with gr.Blocks(title="Turbofan Engine Diagnostic System") as demo:

    gr.Markdown(
        """
# ✈️ Turbofan Engine Diagnostic Decision Support
### Multi-Agent RAG System powered by Ollama (100% local)

Describe the fault symptoms, sensor readings, or anomaly you are observing.
The system will consult three specialist AI agents to produce a diagnostic report.
"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            query_box = gr.Textbox(
                label="Describe the fault / symptoms",
                placeholder="e.g. EGT is 820°C at cruise, vibration 5.8 mils...",
                lines=5,
            )
            submit_btn = gr.Button("Run Diagnostic", variant="primary")
            gr.Markdown("**Example queries:**")
            gr.Examples(examples=EXAMPLES, inputs=query_box)

        with gr.Column(scale=2):
            output_box = gr.Textbox(
                label="Diagnostic Report",
                lines=30,
                interactive=False,
            )

    submit_btn.click(fn=diagnose, inputs=query_box, outputs=output_box)

    gr.Markdown(
        """
---
**How it works:**  
Your query is processed by three specialist agents running in parallel:
- **Fault Classifier** — identifies the fault type and confidence level  
- **Symptom Analyzer** — interprets sensor readings and pinpoints affected sections  
- **Maintenance Advisor** — recommends repair steps, parts, downtime, and safety notes  

Each agent retrieves context from ChromaDB using semantic search.  
All inference runs locally via Ollama — no data leaves your machine.
"""
    )


if __name__ == "__main__":
    demo.launch(share=True)