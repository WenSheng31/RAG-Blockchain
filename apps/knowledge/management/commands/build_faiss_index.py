from pathlib import Path

import numpy as np
import faiss
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from apps.integrations.ai import FAISS_DIR, INDEX_PATH, IDS_PATH
from apps.knowledge.models import Article


class Command(BaseCommand):
    help = "Build FAISS index from all Article content"

    def handle(self, *args, **options):
        pages = list(Article.objects.only("id", "title", "content"))
        if not pages:
            self.stdout.write(self.style.WARNING("資料庫中沒有文章，索引未建立。"))
            return

        self.stdout.write(f"共 {len(pages)} 篇文章，開始向量化…")

        embedder = SentenceTransformer("BAAI/bge-m3")
        embedder.max_seq_length = 512
        texts = [f"{p.title}\n{p.content or ''}" for p in pages]
        ids = np.array([p.id for p in pages])

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

        self.stdout.write(self.style.SUCCESS(f"索引建立完成，共 {len(pages)} 筆向量。"))
