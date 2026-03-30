from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import yaml

# ✅ Clean import (no try/except here)
from app.embeddings import Embedder


class RagPipeline:
    def __init__(
        self,
        docs_path: str = "rag/knowledge_base/docs.json",
        retrieval_config_path: str = "rag/retrieval_config.yaml",
    ) -> None:
        self.docs_path = Path(docs_path)
        self.retrieval_config_path = Path(retrieval_config_path)

        # 📄 Load config
        with self.retrieval_config_path.open("r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # 📄 Load docs
        with self.docs_path.open("r", encoding="utf-8") as f:
            self.docs: List[Dict[str, str]] = json.load(f)

        # 🤖 Embedder
        self.embedder = Embedder(
            model_name=self.config.get(
                "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            use_fallback=bool(self.config.get("fallback_to_hash_embeddings", False)),
        )

        self.top_k = int(self.config.get("top_k", 2))
        self.use_faiss = bool(self.config.get("use_faiss", True))

        # 🔢 Build vectors
        self.doc_vectors = self.embedder.encode(
            [doc["content"] for doc in self.docs]
        )

        self.index = self._build_index(self.doc_vectors)

    def _build_index(self, vectors: np.ndarray):
        if self.use_faiss:
            try:
                import faiss

                index = faiss.IndexFlatIP(vectors.shape[1])
                index.add(vectors)
                return ("faiss", index)
            except Exception:
                pass
        return ("numpy", vectors)

    def retrieve(self, question: str, top_k: int | None = None) -> List[Dict[str, str]]:
        query_vec = self.embedder.encode([question])
        k = top_k or self.top_k

        mode, idx = self.index

        if mode == "faiss":
            scores, ids = idx.search(query_vec, k)
            ranked = [(int(i), float(s)) for i, s in zip(ids[0], scores[0])]
        else:
            scores = np.dot(idx, query_vec[0])
            order = np.argsort(scores)[::-1][:k]
            ranked = [(int(i), float(scores[i])) for i in order]

        results = []
        for i, score in ranked:
            doc = dict(self.docs[i])
            doc["score"] = round(score, 4)
            results.append(doc)

        return results

    def generate_answer(self, question: str, docs: List[Dict[str, str]]) -> str:
        if not docs:
            return "I could not find relevant information in the knowledge base."

        context = " ".join(doc["content"] for doc in docs)
        return f"Based on policy documents: {context}"

    # 🔐 Security layer
    def _is_malicious_or_injection(self, question: str) -> bool:
        q = question.lower()

        blocked = [
            "ignore previous instructions",
            "reveal secret",
            "environment variable",
            "credentials",
            "admin credentials",
            "drop table",
            "rm -rf",
        ]

        return any(term in q for term in blocked)

    def ask(self, question: str) -> Dict[str, object]:
        if self._is_malicious_or_injection(question):
            return {
                "answer": "Request blocked due to security policy.",
                "retrieved_documents": [],
                "embedding_fallback": self.embedder.using_fallback,
            }

        docs = self.retrieve(question)
        answer = self.generate_answer(question, docs)

        return {
            "answer": answer,
            "retrieved_documents": docs,
            "embedding_fallback": self.embedder.using_fallback,
        }