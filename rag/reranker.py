from dataclasses import dataclass
from typing import Dict, Any, Optional, List

import numpy as np
from sentence_transformers import CrossEncoder


@dataclass
class RerankedDoc:
    text: str
    score: float
    metadata: Dict[str, Any]


class CrossEncoderReranker:
    """
    Точный reranker (relevance) по схеме query-document с CrossEncoder.
    Подходящие лёгкие модели:
      - 'cross-encoder/ms-marco-MiniLM-L-6-v2' (быстрый, точность хорошая)
      - 'BAAI/bge-reranker-base' (чуть медленнее, очень качественный)
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: Optional[str] = None):
        self.model = CrossEncoder(model_name, device=device)

    def rerank(self, query: str, docs: List[Dict[str, Any]], top_n: int = 2) -> List[RerankedDoc]:
        if not docs:
            return []
        pairs = [(query, d["text"]) for d in docs]
        scores = self.model.predict(pairs)  # np.ndarray [N]
        # отсортируем по убыванию
        order = np.argsort(-scores)
        top = []
        for idx in order[:top_n]:
            d = docs[idx]
            top.append(RerankedDoc(text=d["text"], score=float(scores[idx]), metadata={k: v for k, v in d.items() if k != "text"}))
        return top
