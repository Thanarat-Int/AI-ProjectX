import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH", "storage/index.jsonl")


def read_file(path: Path) -> str:
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return ""


def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    safe_overlap = min(max(overlap, 0), max(size - 1, 0))
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - safe_overlap, 0)
    return [c for c in chunks if c]


def collect_documents(data_dir: Path, size: int, overlap: int) -> List[Tuple[str, str]]:
    docs = []
    for path in data_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue
        content = read_file(path)
        if not content.strip():
            continue
        for idx, chunk in enumerate(chunk_text(content, size, overlap)):
            source = f"{path.name}#chunk-{idx}"
            docs.append((source, chunk))
    return docs


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into local index")
    parser.add_argument("--data-dir", default="data", help="Directory with documents")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data dir not found: {data_dir}")

    docs = collect_documents(data_dir, args.chunk_size, args.chunk_overlap)
    if not docs:
        print("No documents found to ingest.")
        return

    Path(INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        for source, text in docs:
            f.write(json.dumps({"source": source, "text": text}, ensure_ascii=False))
            f.write("\n")

    print(f"Ingested {len(docs)} chunks into {INDEX_PATH}")


if __name__ == "__main__":
    main()
