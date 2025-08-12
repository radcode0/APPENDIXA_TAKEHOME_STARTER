import json
from typing import Dict, List

from ingest import Document
from utils import timer, write_json


@timer
def build_index(extracted: List[Document]) -> Dict:
    print("indexing")
    """
    Builds a JSON index of the form:
        {
          "documents": [
            { "source": "...", "entities": { ... } },
            ...
          ]
        }
    """
    if not extracted:
        raise ValueError("No data was extracted")
    index = {"documents": extracted}
    return index