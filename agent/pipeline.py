#!/usr/bin/env python
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

from evaluator import evaluate
from extraction import extract_entities
from generator import generate_brief
from ingest import build_corpus
from indexer import build_index
from utils import load_config, write_json, get_client_name

# ------------------------------------------------------------------
# Pipeline driver
# ------------------------------------------------------------------
def run_pipeline() -> None:
    attempts = []
    brief_attempt = 1
    cfg = load_config()
    threshold = cfg.get("similarity_threshold", 0.75)
    total_seconds = 0
    total_tokens = 0

    work_folder = cfg.get("work_folder", "work")
    data_folder = cfg.get("data_folder", "data")    
    outputs_dir = cfg.get("output_folder", "outputs")    

    Path(outputs_dir).mkdir(exist_ok=True)
    Path(work_folder).mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Ingest
    # ------------------------------------------------------------------
    texts = build_corpus(Path(data_folder))

    # ------------------------------------------------------------------
    # 2. Extraction
    # ------------------------------------------------------------------
    extracted = extract_entities(texts)
    total_seconds += extracted.get("elapsed_seconds", 0)
    total_tokens += extracted.get("total_tokens", 0)
    client_name = get_client_name(extracted)

    # ------------------------------------------------------------------
    # 3. Indexing
    # ------------------------------------------------------------------
    index = build_index(extracted["result"])
    total_seconds += index.get("elapsed_seconds", 0)
    index_file = f"{work_folder}/{cfg["index_file"].format(client_name=client_name)}"
    write_json(index_file, index, indent=2)

    # ------------------------------------------------------------------
    # 4. Generation
    # ------------------------------------------------------------------
    brief = generate_brief(index)
    total_seconds += brief.get("elapsed_seconds", 0)
    total_tokens += int(brief.get("total_tokens", 0))
    brief_file = f"{work_folder}/{cfg["brief_file"].format(client_name=f"{client_name}_v{brief_attempt}")}"    
    write_json(brief_file, brief["result"], indent=2)

    # ------------------------------------------------------------------
    # 5. Evaluation
    # ------------------------------------------------------------------
    print(f"evaluating brief (attempt {brief_attempt})")

    eval_result = evaluate(brief["result"], texts)
    total_seconds += eval_result.get("elapsed_seconds", 0)
    total_tokens += eval_result.get("total_tokens", 0)
    similarity = eval_result["similarity"]

    metrics = {
        "extraction_time": extracted["elapsed_seconds"],
        "evaluation_time": eval_result["elapsed_seconds"],
        f"attempt_{brief_attempt}_similarity": similarity,
        f"attempt_{brief_attempt}_generation_time": brief["elapsed_seconds"],
    }

    attempts.append({
        "attempt": brief_attempt,
        "brief_file": str(brief_file),
        "score": similarity
    })

    print(f"brief attempt {brief_attempt} score {similarity})")
    
    # ------------------------------------------------------------------
    # 6. Loop if needed
    # ------------------------------------------------------------------
    while similarity < threshold and brief_attempt < 3:
        brief_attempt += 1
        print(f"Similarity {similarity:.3f} below {threshold}. Re‑running extraction/generation (attempt {brief_attempt})")        
        brief = generate_brief(index, brief_attempt)        
        total_seconds += brief.get("elapsed_seconds", 0)
        total_tokens += int(brief.get("total_tokens", 0))
        brief_file = f"{work_folder}/{cfg["brief_file"].format(client_name=f"{client_name}_v{brief_attempt}")}"    
        write_json(brief_file, brief, indent=2)
        print(f"evaluating brief (attempt {brief_attempt})")
        eval_result = evaluate(brief["result"], texts)
        total_seconds += eval_result.get("elapsed_seconds", 0)
        total_tokens += eval_result.get("total_tokens", 0)
        similarity = eval_result["similarity"]

        metrics.update({
            f"attempt_{brief_attempt}_similarity": similarity,
            f"attempt_{brief_attempt}_generation_time": brief["elapsed_seconds"],
        })
        
        attempts.append({
            "attempt": brief_attempt,
            "brief_file": str(brief_file),
            "score": similarity
        })

        print(f"brief attempt {brief_attempt} score {similarity})")

    # ------------------------------------------------------------------
    # 7. Save final output
    # ------------------------------------------------------------------  
    best_score = 0      
    if attempts:
        best_attempt = max(attempts, key=lambda x: x["score"])
        # recall the brief for final output
        best_brief_path = best_attempt["brief_file"]
        with open(best_brief_path, "r") as f:
            best_brief = json.load(f)
        brief = best_brief 

        # Update metrics with the best attempt
        metrics.update({
            "best_attempt_number": best_attempt["attempt"],
            "best_attempt_file": best_attempt["brief_file"],
            "best_attempt_score": best_attempt["score"],
        })

        best_score = best_attempt["score"]
                                          
    brief_file = f"{outputs_dir}/{cfg["brief_file"].format(client_name=client_name)}"
    metrics_file = f"{outputs_dir}/{cfg["metrics_file"]}"

    write_json(brief_file, brief, indent=2)

    cost_estimate_usd = total_tokens / 1000 * cfg.get("estimate_model_cost_1k", 0)

    # metrics are combined into a single JSON
    all_metrics = {
        "latency_seconds": total_seconds,
        "cost_estimate_usd": f"{cost_estimate_usd:.2f}",
        "total_tokens": total_tokens,
        "work_metrics": metrics,
    }
    write_json(metrics_file, all_metrics, indent=2)

    print(f"Pipeline finished. Final similarity: {best_score:.3f}")
    print(f"Final result written to: {outputs_dir}")


def main():
    run_pipeline()

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()