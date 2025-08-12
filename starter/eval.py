from __future__ import annotations
import json
from pathlib import Path
import sys
import time
import yaml

REQUIRED_KEYS = ["modules", "config_yaml", "risks", "next_steps"]

def load_json(p: Path):
    return json.loads(p.read_text())

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))

def main():
    root = Path(__file__).resolve().parents[1]
    outputs = root / "outputs"
    gold = root / "gold" / "customerX.yaml"

    brief_path = outputs / "customerX_brief.json"
    metrics_path = outputs / "metrics.json"

    results = {
        "field_completeness": 0.0,
        "module_accuracy": 0.0,
        "hallucination_rate": 1.0,
        "latency_seconds": None,
        "cost_estimate_usd": None,
        "total_tokens": None,
        "status": "FAIL",
    }

    if not brief_path.exists():
        print("No outputs found. Expected `outputs/customerX_brief.json`. Please generate your agent outputs and rerun.")
        sys.exit(2)

    brief = load_json(brief_path)
    # Field completeness
    present = sum(1 for k in REQUIRED_KEYS if k in brief)
    results["field_completeness"] = present / len(REQUIRED_KEYS)

    # Module accuracy vs gold
    gold_data = yaml.safe_load(gold.read_text())
    gold_modules = set(m.strip().lower() for m in gold_data.get("modules", []))
    pred_modules = set(m.strip().lower() for m in brief.get("modules", []))
    results["module_accuracy"] = jaccard(pred_modules, gold_modules)
    hallucinations = pred_modules - gold_modules
    results["hallucination_rate"] = 0.0 if not pred_modules else len(hallucinations) / len(pred_modules)

    # Metrics (optional)
    if metrics_path.exists():
        m = load_json(metrics_path)
        results["latency_seconds"] = m.get("latency_seconds")
        results["cost_estimate_usd"] = m.get("cost_estimate_usd")
        results["total_tokens"] = m.get("total_tokens")

    # Simple pass/fail suggestion (you may adjust thresholds)
    if results["field_completeness"] == 1.0 and results["module_accuracy"] >= 0.67:
        results["status"] = "PASS"

    print(json.dumps(results, indent=2))
    # exit code 0 so CI doesn't block reading metrics; rubric can judge numerically
    sys.exit(0)

if __name__ == "__main__":
    main()
