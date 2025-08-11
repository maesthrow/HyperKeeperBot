# ---------- Извлечение items из специфичной структуры ----------
from typing import Dict, Any, Generator, List

from rag.chroma import add_items
from utils.utils_data import get_folders_collection

import logging


def _normalize_item(item_key: str, raw: Dict[str, Any]) -> Dict[str, str]:
    """
    В твоей схеме items — словарь вида {item_id: { ... поля ... }}.
    Берём то, что точно пригодится: item_id, title, text.
    """
    item_id = str(raw.get("id") or raw.get("_id") or raw.get("item_id") or item_key)
    title = (raw.get("title") or "").strip()

    # text может быть строкой или списком строк
    text = raw.get("text")
    if isinstance(text, list):
        text = "\n".join([t for t in text if t])  # склеиваем
    elif text is None:
        text = ""
    return {"item_id": item_id, "title": title or "", "text": (text or "").strip()}


def _walk_folder_dict(node: Dict[str, Any]) -> Generator[Dict[str, str], None, None]:
    """
    node ожидается вида:
    {
      "name": "Хранилище",
      "folders": { "<fid>": {...}, ... },
      "items":   { "<iid>": {...}, ... }
    }
    """
    # items текущей папки
    items_dict = node.get("items") or {}
    if isinstance(items_dict, dict):
        for key, raw in items_dict.items():
            if not isinstance(raw, dict):
                continue
            item = _normalize_item(str(key), raw)
            # отфильтруем совсем пустые
            if not (item["text"]):
                continue
            yield item

    # подпапки
    subfolders = node.get("folders") or {}
    if isinstance(subfolders, dict):
        for _, sub in subfolders.items():
            if isinstance(sub, dict):
                yield from _walk_folder_dict(sub)


def iter_user_items_from_folders_doc(user_doc: Dict[str, Any]) -> Generator[Dict[str, str], None, None]:
    """
    Поддерживает 2 входа:
    1) полный документ: {"_id": ..., "folders": {...}}
    2) сразу словарь folders: {"0": {...}, "0/1-2": {...}, ...}  ← это твой случай
    """
    # если пришёл уже корневой словарь папок (как в твоём логе)
    if "folders" not in user_doc and any(isinstance(v, dict) for v in user_doc.values()):
        roots = user_doc
    else:
        roots = user_doc.get("folders") or {}

    if not isinstance(roots, dict):
        return

    for _, root_node in roots.items():
        if isinstance(root_node, dict):
            yield from _walk_folder_dict(root_node)


# ---------- Публичные функции ----------
async def reindex_user_folders(user_id: int, batch: int = 256) -> int:
    """
    Пройдём по структуре folders конкретного пользователя и проиндексируем все items.
    Возвращаем кол-во проиндексированных items (не чанков).
    """
    user_doc = await get_folders_collection(user_id)
    if not user_doc:
        logging.warning(f"folders doc not found for user_id={user_id}")
        return 0
    else:
        logging.info(f"folders for user={user_doc}")

    # Собираем items пакетами и шлём в Chroma
    count = 0
    buf: List[Dict[str, str]] = []
    for it in iter_user_items_from_folders_doc(user_doc):
        buf.append(it)
        if len(buf) >= batch:
            add_items(user_id=user_id, items=buf, batch=batch)
            count += len(buf)
            buf.clear()
    if buf:
        add_items(user_id=user_id, items=buf, batch=batch)
        count += len(buf)

    logging.info(f"Indexed items={count} for user_id={user_id}")
    return count


async def reindex_many_users(user_ids: List[int], batch: int = 256) -> int:
    """
    Массовая индексация по списку user_id. Возвращаем суммарное количество items.
    """
    total = 0
    for uid in user_ids:
        try:
            total += await reindex_user_folders(uid, batch=batch)
        except Exception:
            logging.exception(f"Failed reindex for user_id={uid}")
    return total
