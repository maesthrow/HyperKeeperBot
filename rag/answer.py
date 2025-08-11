import os
from typing import Tuple, List, Optional

from langchain_community.chat_models import GigaChat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag.chroma import rag_search
from rag.reranker import CrossEncoderReranker, RerankedDoc

_DEFAULT_SYSTEM = (
    "Ты — интеллектуальный ассистент мужского пола, который отвечает строго на основании предоставленного контекста,"
    " которым является персональная информация пользователя, с которым ты общаешься."
    " У тебя нет других источников знаний, кроме этого контекста."
    " Используй только факты, приведённые в контексте/"
    " Если вопрос предполагает конкретный ответ (число, ID, дата, имя, ссылка и т.п.),"
    " и эти данные есть в контексте — приведи их напрямую."
    " Если ответ можно сформировать частично — дай максимально точный ответ из доступных фрагментов,"
    " обязательно передавай найденные по контексту ссылки, значения и т.п."
    " Отвечай уверенно, но не выдумывай факты, которых нет в контексте."
    #" В крайнем случае, если в контексте нет достаточной информации для ответа — явно укажи, что данных недостаточно."
)

_DEFAULT_USER = (
    "Вопрос пользователя:\n{question}\n\n"
    "Контекст (фрагменты персональных данных пользователя):\n{context}\n\n"
    "Сформируй ответ, используя только информацию из контекста."
    " Если информации достаточно — ответь полностью, по существу, без лишних комментариев."
    " Если в контексте есть хотя бы частичный или приближенный ответ и какие либо данные:"
    " число, ID, дата, имя, ссылка — обязательно укажи найденные данные, "
    "но только те, которые требуются по запросу пользовтеля."
)


def _format_context(chunks: List[RerankedDoc]) -> str:
    parts = []
    for i, d in enumerate(chunks, 1):
        title = d.metadata.get("title") or ""
        # item_id = d.metadata.get("item_id") or ""
        head = f"[{i}] {title}".strip()
        parts.append(f"{head}\n{d.text}\n---")
    return "\n".join(parts)


def build_rag_chain(
    llm: Optional[GigaChat] = None,
    system_prompt: str = _DEFAULT_SYSTEM,
    user_prompt: str = _DEFAULT_USER,
):
    """
    Возвращает функцию answer(query, user_id, top_k, top_n), которая:
      1) делает первичный векторный поиск (top_k),
      2) rerank cross-encoder'ом до top_n,
      3) скармливает 2+ лучших чанка в LLM через LangChain.
    """
    if llm is None:
        # Создаём LLM клиента GigaChat
        llm = GigaChat(
            model=os.getenv("GIGACHAT_MODEL", "GigaChat"),
            temperature=0.1,
            credentials=os.getenv("GIGA_AUTH_DATA"),
            verify_ssl_certs=False  # у Сбера иногда бывают проблемы с цепочкой SSL
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt),
    ])
    output_parser = StrOutputParser()

    # Соберём “цепочку” для финального шага
    chain = prompt | llm | output_parser

    # Внедрим pre-steps (retrieval + rerank) в удобную функцию
    reranker = CrossEncoderReranker(
        model_name=os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    )

    def answer(query: str, user_id: int, top_k: int = 8, top_n: int = 2) -> Tuple[str, List[RerankedDoc]]:
        # 1) первичный recall
        candidates = rag_search(user_id=user_id, query=query, k=top_k)
        # 2) rerank
        top_chunks = reranker.rerank(query=query, docs=candidates, top_n=top_n)
        # 3) LLM
        ctx = _format_context(top_chunks)
        print(f'ctx={ctx}')
        response = chain.invoke({"question": query, "context": ctx})
        return response, top_chunks

    return answer
