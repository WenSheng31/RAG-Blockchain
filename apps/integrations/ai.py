import logging
import os
import threading

import faiss
import numpy as np
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)

FAISS_DIR = Path(settings.BASE_DIR) / "faiss_data"
INDEX_PATH = FAISS_DIR / "gitbook_faiss.index"
IDS_PATH = FAISS_DIR / "gitbook_ids.npy"

_lock = threading.Lock()
_rag: "RAGService | None" = None


class RAGService:
    def __init__(self, index, ids, embedder, model):
        self._index = index
        self._ids = ids
        self._embedder = embedder
        self._model = model

    @classmethod
    def load(cls) -> "RAGService":
        from sentence_transformers import SentenceTransformer
        import google.generativeai as genai

        index = faiss.read_index(str(INDEX_PATH))
        ids = np.load(str(IDS_PATH))
        embedder = SentenceTransformer("BAAI/bge-m3")
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("RAGService loaded (%d vectors).", index.ntotal)
        return cls(index, ids, embedder, model)

    def retrieve(self, query: str, k: int = 5) -> list[int]:
        vec = self._embedder.encode([query], normalize_embeddings=True).astype("float32")
        k_actual = min(k, self._index.ntotal)
        _, I = self._index.search(vec, k_actual)
        return [int(self._ids[i]) for i in I[0] if i != -1]

    def generate(self, keyword: str, contexts: list[str]) -> str:
        context = "\n\n---\n\n".join(contexts)
        prompt = (
            f"請根據以下區塊鏈文章內容，用繁體中文統整並摘要說明「{keyword}」是什麼，"
            f"輸出格式為 Markdown：\n\n{context}"
        )
        try:
            import google.generativeai as genai
            resp = self._model.generate_content(prompt, request_options={"timeout": 60})
            return (resp.text or "").strip() or "AI 摘要生成失敗：回傳為空。"
        except Exception as exc:
            logger.error("Gemini failed for '%s': %s", keyword, exc)
            return f"AI 摘要生成失敗：{exc}"


def get_rag() -> RAGService:
    global _rag
    if _rag is None:
        with _lock:
            if _rag is None:
                _rag = RAGService.load()
    return _rag


def reset() -> None:
    global _rag
    with _lock:
        _rag = None
