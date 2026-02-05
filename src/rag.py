from __future__ import annotations

from typing import List
import numpy as np
import faiss
from openai import AzureOpenAI


def row_docs(df, source: str, max_rows: int = 3000) -> List[str]:
    df = df.head(max_rows).copy()
    docs = []
    for i, r in df.iterrows():
        txt = f"SOURCE={source} ROW={i} | " + " | ".join([f"{c}={r[c]}" for c in df.columns])
        docs.append(txt)
    return docs


def embed_texts(client: AzureOpenAI, model: str, texts: List[str], batch: int = 64) -> np.ndarray:
    vecs = []
    for i in range(0, len(texts), batch):
        chunk = texts[i : i + batch]
        resp = client.embeddings.create(model=model, input=chunk)
        vecs.extend([d.embedding for d in resp.data])
    arr = np.array(vecs, dtype=np.float32)
    faiss.normalize_L2(arr)
    return arr


def build_index(client: AzureOpenAI, model: str, docs: List[str]) -> faiss.IndexFlatIP:
    emb = embed_texts(client, model, docs, batch=64)
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    return index


def rag_query(client: AzureOpenAI, model: str, index: faiss.IndexFlatIP, docs: List[str], query: str, k: int = 10):
    q = embed_texts(client, model, [query], batch=1)
    scores, idxs = index.search(q, k)
    return [docs[i] for i in idxs[0]]
