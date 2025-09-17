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
INDEX_EMB = ROOT / "day5.embeddings.npz"   # vectors + metadata
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

# ---- Ingest ------------------------------------------------------------------
def ingest(docs_path: str):
    client = get_client()
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs folder not found: {docs_dir}")

    # Read only .txt for now (simple & predictable)
    texts, sources, ids = [], [], []
    for p in sorted(docs_dir.glob("*.txt")):
        txt = p.read_text(errors="ignore")
        if not txt.strip():
            continue
        texts.append(txt)
        sources.append(str(p))
        ids.append(_hash(str(p)))

    if not texts:
        print("No .txt files found to ingest.")
        return

    X = embed_texts(client, texts)
    # Use cosine distance via brute-force KNN (CPU-friendly for small libs)
    nn = NearestNeighbors(metric="cosine", algorithm="brute")
    nn.fit(X)

    # Save everything compactly
    OUT_DIR.mkdir(exist_ok=True)
    np.savez_compressed(
        INDEX_EMB,
        X=X,
        sources=np.array(sources, dtype=object),
        ids=np.array(ids, dtype=object)
    )
    (ROOT / "day5.nn.json").write_text(json.dumps({"metric": "cosine", "algo": "brute"}))
    print(f"Ingested {len(texts)} docs. Saved vectors to {INDEX_EMB.name}")

# ---- Ask ---------------------------------------------------------------------
def ask(question: str):
    client = get_client()
    if not INDEX_EMB.exists():
        raise FileNotFoundError("Vector file missing. Run --ingest first.")

    data = np.load(INDEX_EMB, allow_pickle=True)
    X = data["X"]
    sources = list(map(str, data["sources"]))
    # ids = list(map(str, data["ids"]))  # reserved if needed later

    # Build a fresh neighbor model (fast for small X)
    nn = NearestNeighbors(metric="cosine", algorithm="brute")
    nn.fit(X)

    q_emb = embed_texts(client, [question])
    dist, idx = nn.kneighbors(q_emb, n_neighbors=min(K, len(sources)))
    chosen_idx = idx[0].tolist()

    picked_paths = [sources[i] for i in chosen_idx]
    context = "\n\n---\n\n".join(Path(p).read_text(errors="ignore") for p in picked_paths)

    # Compose the answer with citations
    msg = [
        {"role": "system", "content": "Answer using only the provided context. Add inline [citations] using file basenames."},
        {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"}
    ]
    reply = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=msg
    ).choices[0].message.content

    OUT_DIR.mkdir(exist_ok=True)
    out = {
        "question": question,
        "answer": reply,
        "sources": picked_paths
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
