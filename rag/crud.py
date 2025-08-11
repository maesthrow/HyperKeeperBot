import hashlib
import time

from rag.chroma import collection, chunk_text, add_items


def content_hash(title: str|None, text: str|None) -> str:
    s = ((title or "") + "\n\n" + (text or "")).encode("utf-8")
    return hashlib.sha1(s).hexdigest()


def delete_item_embeddings(user_id: int, item_id: str):
    collection.delete(
        where={
            "$and": [
                {"user_id": {"$eq": int(user_id)}},
                {"item_id": {"$eq": str(item_id)}}
            ]
        }
    )


def add_or_update_item_embeddings(user_id: int, item_id: str, title: str|None, text: str|None, batch:int=128):
    # 0) короткая защита от пустых данных
    title = (title or "").strip()
    text  = (text  or "").strip()
    if not title and not text:
        delete_item_embeddings(user_id, item_id)
        return 0

    # 1) хеш и быстрая проверка «не изменилось?»
    h = content_hash(title, text)
    existing = collection.get(
        where={
            "$and": [
                {"user_id": {"$eq": int(user_id)}},
                {"item_id": {"$eq": str(item_id)}}
            ]
        },
        limit=1, include=["metadatas"]
    )
    if existing.get("metadatas"):
        old_h = existing["metadatas"][0].get("content_hash")
        if old_h == h:
            return 0  # уже актуально — ничего не делаем

    # 2) удалить старые чанки (иначе будет «мусор»)
    delete_item_embeddings(user_id, item_id)

    # 3) разрезать и залить
    chunks = chunk_text(title, text)
    now = int(time.time())
    items = []
    for i, chunk in enumerate(chunks):
        items.append({
            "item_id": item_id,
            "title": title,
            "text": chunk,
            "meta": {
                "user_id": int(user_id),
                "item_id": str(item_id),
                "chunk_idx": i,
                "content_hash": h,
                "updated_at": now,
            }
        })
    if items:
        add_items(user_id=user_id, items=items, batch=batch)
    return len(items)


def remove_user_item_embeddings(user_id: int, item_id: str):
    delete_item_embeddings(user_id, item_id)