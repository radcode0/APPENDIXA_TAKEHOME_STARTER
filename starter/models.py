from __future__ import annotations
import time
from dataclasses import dataclass

def estimate_tokens(text: str) -> int:
    # simple heuristic
    return max(1, int(len(text) / 4))

@dataclass
class CostTracker:
    total_tokens: int = 0
    total_latency: float = 0.0

    def record(self, prompt: str, response: str, latency: float):
        self.total_tokens += estimate_tokens(prompt) + estimate_tokens(response)
        self.total_latency += latency

class MockLLM:
    """Replace with your model of choice. This mock just echoes prompts."""
    def __init__(self, tracker: CostTracker | None = None):
        self.tracker = tracker or CostTracker()

    def generate(self, prompt: str) -> str:
        t0 = time.time()
        # Echo-based response for scaffolding
        response = f"[MOCK RESPONSE]\n{prompt[:400]}"
        latency = time.time() - t0
        self.tracker.record(prompt, response, latency)
        return response
