# Take-Home Starter – Agentic Pipeline

This starter kit aligns with *Appendix A – Take‑Home Exercise*.

## Goal
Build a prototype **agent pipeline** that converts unstructured implementation data into a structured project brief and proves quality with **automated evaluation**.

## Provided Structure
```
.
├── data/
│   ├── transcript_01.txt ... transcript_05.txt
│   ├── requirements_modules.csv
│   ├── requirements_timeline.csv
│   └── salesforce_export.json
├── gold/
│   └── customerX.yaml
├── outputs/                # Your agent should write files here
│   └── (empty)
└── starter/
    ├── ingest.py
    ├── models.py
    └── eval.py
```

## Required Outputs
Your agent should create the following in `outputs/`:
- `customerX_brief.json` (must include keys: `modules`, `config_yaml`, `risks`, `next_steps`)
- `metrics.json` containing `total_tokens`, `cost_estimate_usd`, `latency_seconds`

## How to Run
1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r starter/requirements.txt
   ```
2. Implement your agent (you may create additional files; just keep `starter/` intact).
3. Produce the required outputs in `outputs/`.
4. Run the evaluation harness:
   ```bash
   python starter/eval.py
   ```

## Notes
- Keep credentials out of this repo; you may mock LLMs or use local inference.
- Focus on clear design, observability, and evaluation. UI is not graded.

— Starter generated on 2025-08-08 16:39:02Z
