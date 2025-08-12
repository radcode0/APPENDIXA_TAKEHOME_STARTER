import json
import os
import ollama
from pathlib import Path
from typing import Dict, List
from ingest import Document

import numpy as np
from utils import cosine_similarity, timer, load_config, token_count

@timer
def evaluate(brief: Dict, fact_check: List[Document]) -> Dict:
    total_tokens = 0
    cfg = load_config()
    DEBUG = cfg["DEBUG"] == 1
    # Flatten the two dicts into strings for embedding
    def flatten(d):
        return " ".join([f"{k}: {v}" for k, v in d.items() if isinstance(v, str)])

    brief_str = flatten(brief)    
    brief_emb = get_embeddings(brief_str)
    total_tokens += brief_emb.get("total_tokens", 1)

    if DEBUG:
        print("DEBUG")
        print(f"brief_emb: {brief_emb}")
        print(f"total_tokens={total_tokens}")

    if not brief_emb["result"]:
        return {"similarity": -1} # return no embeddings

    sim_scores = []
    for doc in fact_check:
        doc_emb = get_embeddings(doc.text)
        total_tokens += doc_emb.get("total_tokens", 1)
        sim_scores.append(cosine_similarity(brief_emb["result"], doc_emb["result"]))

    # Guard against an empty list
    avg_sim = sum(sim_scores) / len(sim_scores) if sim_scores else 0.0
    return {"similarity": avg_sim}


def get_embeddings(text):
    total_tokens = 0
    cfg = load_config()
    DEBUG = cfg["DEBUG"] == 1
    embeddings_model_name = cfg["embeddings_model_name"]
    response = ollama.embed(model=embeddings_model_name, input=text)

    total_tokens += token_count(text) + token_count(str(response))

    if DEBUG:
        print("DEBUG")
        print(f"text={text}")
        print(f"response={response}")
        print(f"embeddings_model_name={embeddings_model_name}")
        print(f"total_tokens={total_tokens}")
    
    return {"result": response["embeddings"], "elapsed_seconds": 0, "total_tokens": total_tokens}

