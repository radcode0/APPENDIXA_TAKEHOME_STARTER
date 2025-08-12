import json
from typing import Dict

import ollama
from utils import timer, load_config, extract_json, token_count


@timer
def generate_brief(index: Dict, brief_attempt=1) -> Dict:
    total_tokens = 0

    """
    Uses the brief prompt to turn the index into a structured brief.
    """
    print(f"(attempt {brief_attempt})")
    print(f"generating brief")
    cfg = load_config()
    DEBUG = cfg["DEBUG"] == 1
    prompt = cfg["brief_prompt"] + f"\n\nIndex:\n{json.dumps(index, indent=2)}"
    try:
        models = cfg.get("brief_model_names", "").split(",")
        model_index = max(0, min(brief_attempt - 1, len(models) - 1))
        model_name = models[model_index]
        resp = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": cfg["temperature"],
                    "max_tokens": cfg["max_tokens"],
                },
        )
        
        total_tokens += token_count(prompt) + token_count(str(resp))

        if DEBUG:
            print(resp)

        # The model should return a JSON object
        # just in case, attempty to extract json from response content
        json_string = extract_json(resp["message"]["content"])

        if DEBUG:
            print(f"json extracted : {json_string}")

        if json_string:
            brief = json.loads(json_string)
        else:
            raise ValueError("no json found in LLM response")

    except Exception as e:
        brief = {
            "summary": "",
            "objectives": "",
            "timeline": "",
            "deliverables": "",
            "risks": "",
            "next_steps": "",
        }
        print(f"Brief generation error: {e}")

    return {"result": brief, "elapsed_seconds": 0, "total_tokens": total_tokens}