import json

from typing import Dict, List

import ollama
from ingest import Document
from utils import timer, load_config, extract_json, token_count


@timer
def extract_entities(docs: List[Document]) -> Dict:
    """
    For each document, call the LLM with the extraction prompt and
    return a list of extracted entities.
    """
    cfg = load_config()
    DEBUG = cfg["DEBUG"] == 1
    prompt_template = cfg["extraction_prompt"]
    results = []
    total_tokens = 0

    for doc in docs:
        print(f"extracting {doc.doc_id}")
        prompt = prompt_template + f"\n\nText:\n{doc.text}"
        try:
            resp = ollama.chat(
                model=cfg["extract_model_name"],
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": cfg["temperature"],
                    "max_tokens": cfg["max_tokens"],
                },
            )            

            total_tokens += token_count(prompt) + token_count(str(resp))

            if DEBUG:
                print(f"LLM Response Content: {resp}")

            # The model should return a JSON object
            # just in case, attempty to extract json from response content
            json_string = extract_json(resp["message"]["content"])

            if DEBUG:
                print(f"json extracted : {json_string}")

            if json_string:
                entity = json.loads(json_string)
                results.append({"source": doc.doc_id, "entities": entity})
            
        except Exception as e:            
            print(f"Extraction error for {doc.doc_id}: {e}")        
    return {"result": results, "elapsed_seconds": 0, "total_tokens": total_tokens}

