import argparse, os, json, hashlib
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.neighbors import NearestNeighbors

# ---- Config & helpers --------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
OUT_DIR = ROOT / "outputs"
INDEX_EMB = ROOT / "day6.embeddings.npz"   # vectors + metadata
K = 3  # top-k neighbors

def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

# ---- Embeddings --------------------------------------------------------------
def get_client():
    load_dotenv(ENV, override=True)
    key = os.getenv("OPENAI_API_KEY")
    project = os.getenv("OPENAI_PROJECT")

    if not key:
        raise RuntimeError("Missing OPENAI_API_KEY in .env")

    if key.startswith("sk-proj-"):
        if not project:
            raise RuntimeError(
                "You are using a project key (sk-proj-...), but OPENAI_PROJECT is missing in .env"
            )
        return OpenAI(api_key=key, project=project)

    # fallback for classic sk- keys
    return OpenAI(api_key=key)

def embed_texts(client: OpenAI, texts: list[str]) -> np.ndarray:
    # Batch safely (OpenAI supports batching; keep simple here)
    embs = []
    B = 64
    for i in range(0, len(texts), B):
        chunk = texts[i:i+B]
        resp = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        embs.extend([d.embedding for d in resp.data])
    return np.array(embs, dtype="float32")

# ---- Chunker -----------------------------------------------------------------
def chunk_text(text, max_chars=1000):
    import re
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_chars:
            current += s + " "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = s + " "
    if current.strip():
        chunks.append(current.strip())
    return chunks


# ---- Ingest ------------------------------------------------------------------
def ingest(docs_path: str):
    client = get_client()
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs folder not found: {docs_dir}")

    texts, sources, ids = [], [], []
    for p in sorted(docs_dir.glob("*.txt")):
        full = p.read_text(errors="ignore")
        if not full.strip():
            continue
        pieces = chunk_text(full, max_chars=1000)  # chapter-sized chunks
        for i, piece in enumerate(pieces):
            if not piece.strip():
                continue
            texts.append(piece)
            sources.append(f"{p.name}#chunk{i}")          # file + chunk tag
            ids.append(_hash(f"{p}:{i}"))

    if not texts:
        print("No .txt files found to ingest.")
        return

    X = embed_texts(client, texts)
    nn = NearestNeighbors(metric="cosine", algorithm="brute")
    nn.fit(X)

    OUT_DIR.mkdir(exist_ok=True)
    np.savez_compressed(
        INDEX_EMB,
        X=X,
        sources=np.array(sources, dtype=object),
        ids=np.array(ids, dtype=object),
        chunks=np.array(texts, dtype=object),   # persist chunk text
    )
    (ROOT / "day6.nn.json").write_text(json.dumps({"metric": "cosine", "algo": "brute"}))
    print(f"Ingested {len(texts)} chunks from {docs_dir}. Saved vectors to {INDEX_EMB.name}")


# ---- Ask ---------------------------------------------------------------------
def ask(question: str, top_k: int = K):
    client = get_client()
    if not INDEX_EMB.exists():
        raise FileNotFoundError("Vector file missing. Run --ingest first.")

    data = np.load(INDEX_EMB, allow_pickle=True)
    X = data["X"]
    sources = list(map(str, data["sources"]))
    chunks = list(map(str, data["chunks"]))

    nn = NearestNeighbors(metric="cosine", algorithm="brute")
    nn.fit(X)

    q_emb = embed_texts(client, [question])
    _, idx = nn.kneighbors(q_emb, n_neighbors=min(top_k, len(sources)))
    chosen_idx = idx[0].tolist()

    picked_sources = [sources[i] for i in chosen_idx]
    picked_chunks  = [chunks[i]  for i in chosen_idx]
    context = "\n\n---\n\n".join(picked_chunks)

    messages = [
        {
            "role": "system",
            "content": "Answer using only the provided context. Add inline [citations] using the provided source tags (e.g., file.txt#chunk3)."
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nContext:\n{context}"
        },
    ]

    reply = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=messages,
    ).choices[0].message.content

    OUT_DIR.mkdir(exist_ok=True)
    out = {
        "question": question,
        "answer": reply,
        "sources": picked_sources,
    }
    out_file = OUT_DIR / f"qa_{len(list(OUT_DIR.glob('qa_*.json')))}.json"
    out_file.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("Answer saved to", out_file)


# ---- CLI ---------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", help="path to docs folder (txt files)")
    ap.add_argument("--ask", help='question string, e.g., --ask "What is X?"')
    args = ap.parse_args()

    ROOT.mkdir(exist_ok=True)
    if args.ingest:
        ingest(args.ingest)
    elif args.ask:
        ask(args.ask)
    else:
        ap.print_help()
