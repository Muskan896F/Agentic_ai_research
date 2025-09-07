# memory/long_term.py
"""
Long-Term Memory
- Stores embeddings + metadata across runs
- Default: FAISS index (local vector DB)
- Allows: upsert, query, and persistence
"""

import os
import numpy as np
from typing import List, Dict
from loguru import logger

# Try FAISS import
try:
    import faiss
except ImportError:
    faiss = None
    logger.warning("⚠️ FAISS not installed. Run `pip install faiss-cpu` for local vector memory.")


class LongTermMemory:
    def __init__(self, dim: int = 1536, index_path: str = "memory/long_term.faiss"):
        self.dim = dim
        self.index_path = index_path
        self.index = None
        self.id_to_meta: Dict[int, Dict] = {}

        if faiss is not None:
            self._init_index()

    def _init_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            logger.info(f"✅ Loaded FAISS index from {self.index_path}")
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            logger.info("✅ Created new FAISS index")

    def upsert(self, embedding: List[float], meta: Dict):
        """Insert one vector + metadata"""
        if faiss is None:
            logger.error("❌ FAISS not available. Cannot upsert vectors.")
            return
        arr = np.array([embedding]).astype("float32")
        self.index.add(arr)
        idx = self.index.ntotal - 1
        self.id_to_meta[idx] = meta
        logger.debug(f"Inserted vector {idx} with meta: {meta}")

    def query(self, embedding: List[float], k: int = 5) -> List[Dict]:
        """Find top-k nearest neighbors"""
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
        """Persist index to disk"""
        if faiss is None:
            return
        faiss.write_index(self.index, self.index_path)
        logger.info(f"💾 Saved FAISS index to {self.index_path}")


# Quick test
if __name__ == "__main__":
    lt = LongTermMemory(dim=8, index_path="memory/test_long.faiss")

    # dummy vector
    import numpy as np
    v1 = np.random.rand(8).astype("float32").tolist()
    lt.upsert(v1, {"topic": "React Native 2025", "url": "https://example.com"})
    lt.save()

    # query with random vector
    qv = np.random.rand(8).astype("float32").tolist()
    print("Query results:", lt.query(qv, k=1))
