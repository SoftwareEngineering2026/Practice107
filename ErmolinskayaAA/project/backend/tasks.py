import time


def process_text_task(text: str, mode: str) -> str:
    """
    Функция долгой обработки текста.

    Сейчас здесь простая имитация AI-обработки.
    Позже мы заменим эту логику на вызов небольшой NLP-модели.
    """

    time.sleep(3)

    if mode == "improve":
        return improve_text(text)

    if mode == "formal":
        return make_formal(text)

    if mode == "friendly":
        return make_friendly(text)

    if mode == "shorten":
        return shorten_text(text)

    if mode == "fix":
        return fix_text(text)

    return text


def improve_text(text: str) -> str:
    return (
        "Улучшенный вариант текста: "
        + text[0].upper()
        + text[1:]
        + ". Текст стал более понятным и аккуратным."
    )


def make_formal(text: str) -> str:
    return (
        "Официальная версия: "
        + text[0].upper()
        + text[1:]
        + ". Данный текст был адаптирован в более деловом стиле."
    )


def make_friendly(text: str) -> str:
    return (
        "Дружелюбная версия: "
        + text[0].upper()
        + text[1:]
        + ". Теперь текст звучит мягче и приятнее."
    )


def shorten_text(text: str) -> str:
    words = text.split()

    if len(words) <= 10:
        return "Краткая версия: " + text

    short_text = " ".join(words[:10])
    return "Краткая версия: " + short_text + "..."


def fix_text(text: str) -> str:
    fixed = text.strip()

    if fixed:
        fixed = fixed[0].upper() + fixed[1:]

    if not fixed.endswith((".", "!", "?")):
        fixed += "."

    return "Исправленный текст: " + fixed