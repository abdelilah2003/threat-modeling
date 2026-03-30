from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np


class Embedder:
    """Sentence-transformers embedder with deterministic fallback.

    The fallback keeps CI deterministic even when model download is unavailable.
    """

    def __init__(self, model_name: str, use_fallback: bool = True) -> None:
        self.model_name = model_name
        self.use_fallback = use_fallback
        self._model = None
        self._load_error = None

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
        except Exception as exc:  # pragma: no cover - environment dependent
            self._load_error = str(exc)
            if not use_fallback:
                raise RuntimeError(f"Failed to load embedding model '{model_name}': {exc}") from exc

    @property
    def using_fallback(self) -> bool:
        return self._model is None

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        texts = list(texts)
        if self._model is not None:
            vectors = self._model.encode(texts, normalize_embeddings=True)
            return np.asarray(vectors, dtype=np.float32)
        return self._hash_encode(texts)

    def _hash_encode(self, texts: List[str], dim: int = 384) -> np.ndarray:
        vectors = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            seed = int.from_bytes(digest[:8], "big", signed=False)
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(dim).astype(np.float32)
            norm = float(np.linalg.norm(vec)) or 1.0
            vectors.append(vec / norm)
        return np.stack(vectors)
