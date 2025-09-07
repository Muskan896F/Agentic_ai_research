# tools/vector_store.py
"""
Vector Store
- Provides long-term memory using FAISS (default).
- Stores embeddings + metadata for retrieval.
- Optionally supports Pinecone (uncomment if needed).
"""

import os
from typing import List, Dict, Optional
import numpy as np
from loguru import logger

# Try importing FAISS
try:
    import faiss
except ImportError:
    faiss = None
    logger.warning("⚠️ FAISS not installed. Run `pip install faiss-cpu` for local vector storage.")


class VectorStore:
    def __init__(self, dim: int = 1536, index_path: str = "memory/index.faiss"):
        self.dim = dim
        self.index_path = index_path
        self.index = None
        self.id_to_meta = {}

        if faiss is not None:
            self._init_index()

    def _init_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            logger.info("✅ Loaded FAISS index from disk.")
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            logger.info("✅ Created new FAISS index.")

    def upsert(self, embedding: List[float], meta: Dict):
        """Insert an embedding with metadata into the index."""
        if faiss is None:
            logger.error("❌ FAISS not available. Cannot store vectors.")
            return

        arr = np.array([embedding]).astype("float32")
        self.index.add(arr)
        idx = self.index.ntotal - 1
        self.id_to_meta[idx] = meta

    def query(self, embedding: List[float], k: int = 5) -> List[Dict]:
        """Search for top-k similar vectors."""
        if faiss is None:
            return []

        q = np.array([embedding]).astype("float32")
        D, I = self.index.search(q, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            meta = self.id_to_meta.get(int(idx), {})
            results.append({"score": float(dist), "meta": meta})
        return results

    def save(self):
        """Persist index to disk."""
        if faiss is None:
            return
        faiss.write_index(self.index, self.index_path)
        logger.info("💾 Saved FAISS index to disk.")


# Quick test
if __name__ == "__main__":
    import numpy as np
    vs = VectorStore(dim=8, index_path="memory/test.faiss")

    # add dummy vector
    v1 = np.random.rand(8).astype("float32").tolist()
    vs.upsert(v1, {"topic": "test topic", "url": "https://example.com"})
    vs.save()

    # query
    qv = np.random.rand(8).astype("float32").tolist()
    results = vs.query(qv, k=1)
    print(results)
