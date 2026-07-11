from pathlib import Path

import numpy as np
import faiss
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from apps.integrations.ai import FAISS_DIR, INDEX_PATH, IDS_PATH
from apps.knowledge.models import Article

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


def chunk_text(tokenizer, text: str) -> list[str]:
    """Split text into overlapping windows of at most CHUNK_SIZE tokens."""
    offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    if len(offsets) <= CHUNK_SIZE:
        return [text]

    stride = CHUNK_SIZE - CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(offsets):
        end = min(start + CHUNK_SIZE, len(offsets))
        char_start, char_end = offsets[start][0], offsets[end - 1][1]
        chunks.append(text[char_start:char_end])
        if end == len(offsets):
            break
        start += stride
    return chunks


class Command(BaseCommand):
    help = "Build FAISS index from all Article content (chunked with overlap)"

    def handle(self, *args, **options):
        pages = list(Article.objects.only("id", "title", "content"))
        if not pages:
            self.stdout.write(self.style.WARNING("資料庫中沒有文章，索引未建立。"))
            return

        self.stdout.write(f"共 {len(pages)} 篇文章，開始切塊與向量化…")

        embedder = SentenceTransformer("BAAI/bge-m3")
        embedder.max_seq_length = 8192

        texts = []
        ids_list = []
        for p in pages:
            full_text = f"{p.title}\n{p.content or ''}"
            for piece in chunk_text(embedder.tokenizer, full_text):
                texts.append(piece)
                ids_list.append(p.id)
        ids = np.array(ids_list)

        self.stdout.write(
            f"切分為 {len(texts)} 個區塊（平均每篇 {len(texts) / len(pages):.1f} 塊，"
            f"chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}）。"
        )

        vectors = embedder.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype("float32")

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)

        FAISS_DIR.mkdir(exist_ok=True)

        tmp_index = INDEX_PATH.with_suffix(".tmp")
        tmp_ids = FAISS_DIR / "gitbook_ids.tmp.npy"
        faiss.write_index(index, str(tmp_index))
        np.save(str(tmp_ids), ids)
        tmp_index.replace(INDEX_PATH)
        tmp_ids.replace(IDS_PATH)

        self.stdout.write(self.style.SUCCESS(
            f"索引建立完成，共 {len(pages)} 篇文章、{len(texts)} 個向量。"
        ))
