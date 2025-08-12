from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import csv

@dataclass
class Document:
    doc_id: str
    text: str

def load_transcripts(data_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for p in sorted(data_dir.glob("transcript_*.txt")):
        print(f"reading {p.name}")
        docs.append(Document(doc_id=p.name, text=p.read_text()))
    return docs

def load_spreadsheets(data_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for p in data_dir.glob("*.csv"):
        print(f"reading {p.name}")
        rows = []
        with p.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
        # naive flatten
        text = "\n".join([", ".join(f"{k}={v}" for k, v in r.items()) for r in rows])
        docs.append(Document(doc_id=p.name, text=text))
    return docs

def load_salesforce_export(data_dir: Path) -> dict:
    p = data_dir / "salesforce_export.json"
    print(f"reading {p.name}")
    return json.loads(p.read_text()) if p.exists() else {}

def build_corpus(data_dir: Path) -> list[Document]:
    docs = []
    docs.extend(load_transcripts(data_dir))
    docs.extend(load_spreadsheets(data_dir))
    sf = load_salesforce_export(data_dir)
    if sf:
        docs.append(Document(doc_id="salesforce_export.json", text=json.dumps(sf)))
    return docs
