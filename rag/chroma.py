# ======= chroma_setup.py =======
import os

os.environ.setdefault("DUCKDB_THREADS", "1")  # снижает шанс падений на Win
os.environ["CHROMADB_DISABLE_HNSWLIB"] = "1"   # критично: отключаем нативный индекс
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

try:
    import torch
    torch.set_num_threads(1)
except ImportError:
    pass

import math
import json
from typing import List, Dict, Any, Optional, Iterable

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

# ---- Укажи тут свою модель эмбеддингов ----
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")


def embed(texts):
    return model.encode(texts, normalize_embeddings=True).tolist()


# --- База: путь можно менять, чтобы "чисто" пересоздать индекс ---
CHROMA_PATH = "./rag/db/chroma_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False)
)


# Имя коллекции привязываем к модели и размерности, чтобы не путать
COLLECTION_NAME = f"hk_user_items_minilm_l6_v2_d{EMBED_DIM}"


def get_collection():
    # создаст коллекцию, если её нет — без try/except и без chromadb.errors
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        #metadata={"hnsw:space": "cosine"},  # cosine/inner/ l2 — на ваш выбор
    )


collection = get_collection()


# ======= utils =======

def _json_safe(x: Any, depth: int = 0, max_depth: int = 4) -> Any:
    """Привести метаданные к JSON-безопасному виду с мягким ограничением глубины."""
    if depth > max_depth:
        return str(x)

    if x is None or isinstance(x, (bool, int, float, str)):
        return x

    # datetime, numpy, и пр.
    if hasattr(x, "isoformat"):
        try:
            return x.isoformat()
        except Exception:
            return str(x)

    if isinstance(x, dict):
        return {str(k): _json_safe(v, depth+1, max_depth) for k, v in list(x.items())[:100]}
    if isinstance(x, (list, tuple, set)):
        lst = list(x)[:200]
        return [_json_safe(v, depth+1, max_depth) for v in lst]

    # последний шанс
    return str(x)


def _has_nan_or_inf(arr: np.ndarray) -> bool:
    return (np.isnan(arr).any() or np.isinf(arr).any())

# ======= твоё разбиение на чанки (слегка дополировал) =======


def chunk_text(title: Optional[str],
               text: Optional[str],
               target_chars: int = 1000,
               overlap: int = 200) -> List[str]:
    title = (title or "").strip()
    text = (text or "").strip()

    title_prefix = (title + "\n\n") if title else ""
    min_body = 200
    chunk_size = max(target_chars - len(title_prefix), min_body)

    max_overlap = max(int(chunk_size * 0.2), 0)
    overlap = min(overlap, max_overlap)

    if not text and not title_prefix:
        return []

    if not text:
        return [title_prefix.rstrip()]

    chunks = []
    start = 0
    max_chunks = 10000

    while start < len(text) and len(chunks) < max_chunks:
        end = min(len(text), start + chunk_size)
        body = text[start:end].strip()
        if not body:
            break
        chunks.append(title_prefix + body)
        if end >= len(text):
            break
        new_start = end - overlap
        if new_start <= start:
            new_start = end
        start = new_start

    return chunks


# ======= основной апсерт =======

def add_items(user_id: int, items: List[Dict[str, Any]], batch: int = 128):
    """
    items: [{ "item_id": str|int, "title": str, "text": str, "meta": dict? }, ...]
    Идемпотентно: детерминированные id в формате f"{item_id}::{i}".
    """
    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for it in items:
        item_id = str(it["item_id"])
        chunks = chunk_text(it.get("title"), it.get("text"))

        for i, chunk in enumerate(chunks):
            # фильтрация пустых или слишком коротких кусков, чтобы не плодить мусор
            if not chunk or chunk.strip() == "":
                continue

            ids.append(f"{item_id}::{i}")
            docs.append(chunk)

            base_meta = {
                "user_id": int(user_id),
                "item_id": item_id,
                "title": (it.get("title") or "").strip(),
            }
            if it.get("meta"):
                try:
                    base_meta.update(it["meta"])
                except Exception:
                    # если meta неожиданно не dict, сохраним как строку
                    base_meta["meta_raw"] = str(it["meta"])

            metas.append(_json_safe(base_meta))

            if len(ids) >= batch:
                _flush_batch(ids, docs, metas)
                ids, docs, metas = [], [], []

    if ids:
        _flush_batch(ids, docs, metas)


def user_has_embeddings(user_id: int) -> bool:
    """
    Быстро проверяет, есть ли хотя бы один чанк у пользователя.
    Ничего «тяжёлого» не тянем: только ids.
    """
    try:
        res = collection.get(
            where={"user_id": int(user_id)},
            limit=1
        )
        return bool(res and res.get("ids"))
    except Exception:
        return False


def user_embeddings_count(user_id: int) -> int:
    """
    Возвращает количество чанков у пользователя (если поддерживается фильтр в count()).
    Падает обратно на дешёвый get() без эмбеддингов, если count(where=...) недоступен.
    """
    try:
        # в новых версиях chroma есть count(where=...)
        return collection.count(where={"user_id": int(user_id)})  # type: ignore[arg-type]
    except TypeError:
        # fallback для старых версий: берём только ids, пагинацию можно добавить при желании
        res = collection.get(where={"user_id": int(user_id)})
        return len(res.get("ids", []))


def _flush_batch(ids: List[str], docs: List[str], metas: List[Dict[str, Any]]):
    # эмбеддинг
    vecs = embed(docs)
    if not isinstance(vecs, np.ndarray):
        vecs = np.asarray(vecs, dtype=np.float32)
    if vecs.dtype != np.float32:
        vecs = vecs.astype(np.float32, copy=False)

    # проверка формы и NaN/Inf
    if vecs.ndim != 2 or vecs.shape[1] != EMBED_DIM:
        raise ValueError(f"Bad embedding shape: {vecs.shape}, expected (?, {EMBED_DIM})")
    if _has_nan_or_inf(vecs):
        # выкидываем плохие документы
        good_idx = np.where(~(np.isnan(vecs).any(axis=1) | np.isinf(vecs).any(axis=1)))[0]
        if len(good_idx) == 0:
            return
        ids[:]  = [ids[i]  for i in good_idx]
        docs[:] = [docs[i] for i in good_idx]
        metas[:] = [metas[i] for i in good_idx]
        vecs = vecs[good_idx]

    # upsert порциями поменьше — снижает шанс падения native-кода
    SLICE = 16
    for s in range(0, len(ids), SLICE):
        sl = slice(s, s+SLICE)
        collection.upsert(
            ids=list(map(str, ids[sl])),
            documents=docs[sl],
            metadatas=metas[sl],
            embeddings=vecs[sl].tolist(),  # отдаём чистый python-list
        )


# ======= поиск =======

def rag_search(user_id: int, query: str, k: int = 5):
    qv = embed([query])
    if not isinstance(qv, np.ndarray):
        qv = np.asarray(qv, dtype=np.float32)
    if qv.dtype != np.float32:
        qv = qv.astype(np.float32, copy=False)
    if qv.ndim != 2 or qv.shape[1] != EMBED_DIM:
        raise ValueError(f"Bad query embedding shape: {qv.shape}, expected (?, {EMBED_DIM})")
    if _has_nan_or_inf(qv):
        raise ValueError("Query embedding has NaN/Inf")

    res = collection.query(
        query_embeddings=qv.tolist(),
        n_results=k,
        where={"user_id": int(user_id)}
    )
    return [
        {"text": t, **m}
        for t, m in zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0])
    ]


# ======= утилита: снести коллекцию (если снова поменяешь модель) =======
def drop_collection():
    client.delete_collection(COLLECTION_NAME)


# ======= чтение всех фрагментов пользователя (фикс include) =======

def _collect_ids_for_user(user_id: int, page_size: int = 1000) -> list[str]:
    """
    Возвращает все ids для пользователя с пагинацией.
    ids всегда приходят, их НЕ нужно указывать в include.
    """
    user_id = int(user_id)
    ids: list[str] = []
    offset = 0

    while True:
        try:
            # дешёвый запрос: просим НИЧЕГО, кроме обязательных полей (ids вернутся всё равно)
            resp = collection.get(
                where={"user_id": user_id},
                limit=page_size,
                offset=offset,
                include=[]  # важно: НЕ ["ids"]
            )
        except TypeError:
            # кросс-версийный fallback (у старых версий может не быть include=[])
            resp = collection.get(
                where={"user_id": user_id},
                limit=page_size,
                offset=offset,
            )

        batch_ids = list(map(str, resp.get("ids", [])))
        if not batch_ids:
            break
        ids.extend(batch_ids)
        if len(batch_ids) < page_size:
            break
        offset += page_size

    return ids


def get_user_fragments(user_id: int, batch: int = 256) -> list[dict]:
    """
    Возвращает ВСЕ фрагменты (чанки) пользователя.
    Формат: [{ "id": str, "text": str, **metadata }, ...]
    """
    ids = _collect_ids_for_user(user_id)
    if not ids:
        return []

    out: list[dict] = []
    for i in range(0, len(ids), batch):
        chunk_ids = ids[i:i + batch]
        resp = collection.get(
            ids=chunk_ids,
            include=["documents", "metadatas"]  # ids вернутся автоматически
        )
        got_ids = list(map(str, resp.get("ids", [])))
        docs = resp.get("documents", [])
        metas = resp.get("metadatas", [])

        for _id, doc, meta in zip(got_ids, docs, metas):
            item = {"id": _id, "text": doc or ""}
            if isinstance(meta, dict):
                item.update(meta)
            out.append(item)

    return out


def iter_user_fragments(user_id: int, batch: int = 256):
    """
    Генератор по чанкам пользователя (экономит память).
    yield dict как в get_user_fragments().
    """
    ids = _collect_ids_for_user(user_id)
    for i in range(0, len(ids), batch):
        chunk_ids = ids[i:i + batch]
        resp = collection.get(
            ids=chunk_ids,
            include=["documents", "metadatas"]
        )
        for _id, doc, meta in zip(resp.get("ids", []),
                                  resp.get("documents", []),
                                  resp.get("metadatas", [])):
            item = {"id": str(_id), "text": doc or ""}
            if isinstance(meta, dict):
                item.update(meta)
            yield item
