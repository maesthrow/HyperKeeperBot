from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from load_all import bot
from rag.answer import build_rag_chain
from rag.chroma import iter_user_fragments
from utils.utils_button_manager import get_after_rag_search_item_markup
from utils.utils_markdown_new import escape_md_preserving_formatting
from utils.utils_parse_mode_converter import escape_markdown


async def rag_search_handler(message: Message, state: FSMContext):
    for frag in iter_user_fragments(message.from_user.id, batch=128):
        print(frag["id"], frag["item_id"], frag["title"][:30])

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    answer = build_rag_chain()

    text = message.text[4:]
    query = text.strip()

    print(f'RAG Search: {query}')

    text, used_chunks = answer(query=query, user_id=message.from_user.id, top_k=8, top_n=2)

    print("=== Answer ===")
    print(text)

    def truncate(s: str, n: int = 200) -> str:
        s = (s or "").replace("\n", " ").strip()
        return s if len(s) <= n else s[:n] + "…"

    print("=== Used chunks (reranked) ===")
    for d in used_chunks:
        print(
            f"score={d.score:.4f} | title={d.metadata.get('title')} | item_id={d.metadata.get('item_id')}\n"
            f"text: {truncate(d.text, 300)}\n---"
        )

    text = escape_md_preserving_formatting(text)

    inline_markup = await get_after_rag_search_item_markup(
        user_id=message.from_user.id,
        item_id=used_chunks[0].metadata.get('item_id')
    )

    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inline_markup
    )
