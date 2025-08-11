import re
from typing import Tuple, Dict, Any

MDV2_SPECIALS = r'[_*[\]()~`>#+\-=|{}.!]'

PATTERNS = {
    "pre":     re.compile(r"```([\s\S]*?)```"),
    "code":    re.compile(r"`([^`\n]+?)`"),
    "link":    re.compile(r"\[([^\]\n]+?)\]\(([^)\n]+?)\)"),
    "bold2":   re.compile(r"\*\*(.+?)\*\*"),
    "bold":    re.compile(r"\*(?!\s)(.+?)(?<!\s)\*"),
    "uline2":  re.compile(r"__(.+?)__"),
    "uline":   re.compile(r"_(?!\s)(.+?)(?<!\s)_"),
    "strike":  re.compile(r"~~(.+?)~~"),
    "spoiler": re.compile(r"\|\|(.+?)\|\|"),
}


def _escape_plain(text: str) -> str:
    text = text.replace("\\", "\\\\")
    return re.sub(f"({MDV2_SPECIALS})", r"\\\1", text)


def _escape_content(text: str) -> str:
    """Экранируем спецсимволы в содержимом форматирующих сущностей."""
    return _escape_plain(text)


def _escape_url(url: str) -> str:
    """Минимально безопасное экранирование внутри (url) для MarkdownV2."""
    url = url.replace("\\", "\\\\")
    url = url.replace("(", "\\(").replace(")", "\\)")
    return url


def _protect(text: str) -> Tuple[str, Dict[str, Any]]:
    """Заменяем валидные конструкции плейсхолдерами и сохраняем структуру."""
    stash: Dict[str, Any] = {}
    i = 0

    for name in ["pre", "code", "link", "bold2", "bold", "uline2", "uline", "strike", "spoiler"]:
        pat = PATTERNS[name]

        def repl(m):
            nonlocal i
            key = f"PH{name}{i}X"
            if name == "pre":
                stash[key] = ("pre", m.group(1))
            elif name == "code":
                stash[key] = ("code", m.group(1))
            elif name == "link":
                stash[key] = ("link", m.group(1), m.group(2))
            elif name == "bold2":
                stash[key] = ("bold", m.group(1))      # **..** → *..*
            elif name == "uline2":
                stash[key] = ("uline", m.group(1))     # __..__ → _.._
            elif name in ("bold", "uline", "strike", "spoiler"):
                stash[key] = (name, m.group(1))
            else:
                stash[key] = ("raw", m.group(0))
            i += 1
            return key

        text = pat.sub(repl, text)
    return text, stash


def _restore(text: str, stash: Dict[str, Any]) -> str:
    """Возвращаем плейсхолдеры с корректным экранированием содержимого."""
    # Важно: никакой regex — прямые replace по ключам, чтобы не зацепить экранирование
    for key, val in stash.items():
        kind = val[0]
        if kind == "pre":
            rep = f"```{val[1]}```"                  # в pre ничего не экранируем
        elif kind == "code":
            rep = f"`{val[1]}`"                      # в inline code тоже
        elif kind == "link":
            text_part = _escape_content(val[1])
            url_part = _escape_url(val[2])
            rep = f"[{text_part}]({url_part})"
        elif kind == "bold":
            rep = f"*{_escape_content(val[1])}*"
        elif kind == "uline":
            rep = f"_{_escape_content(val[1])}_"
        elif kind == "strike":
            rep = f"~~{_escape_content(val[1])}~~"
        elif kind == "spoiler":
            rep = f"||{_escape_content(val[1])}||"
        else:
            rep = _escape_plain(val[1] if len(val) > 1 else "")
        text = text.replace(key, rep)
    return text


def _escape_dangerous_hyphens(text: str) -> str:
    """Экранируем любую «гребёнку» дефисов в начале строки: -, --, ---, …"""
    def repl(m: re.Match) -> str:
        lead = m.group("lead") or ""
        run  = m.group("run")
        return lead + "".join("\\-" for _ in run)
    return re.sub(r"(?m)^(?P<lead>\s*)(?P<run>-+)", repl, text)


def escape_md_preserving_formatting(s: str) -> str:
    """
    Сохраняет разметку, конвертирует **→*, __→_, экранирует спецсимволы:
    - снаружи форматирующих блоков,
    - и внутри содержимого bold/italic/underline/strike/spoiler,
    - URL обрабатывает отдельно,
    - дефисы в начале строк экранирует.
    """
    safe, stash = _protect(s)
    safe = _escape_plain(safe)          # экранируем «голый» текст
    safe = _restore(safe, stash)        # возвращаем разметку с экранированным содержимым
    safe = _escape_dangerous_hyphens(safe)
    return safe
