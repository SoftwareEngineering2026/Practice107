import os
import re
import time
from functools import lru_cache

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MODEL_NAME = os.getenv("MODEL_NAME", "cointegrated/rut5-small")


@lru_cache(maxsize=1)
def load_model():
    """
    Модель загружается один раз при первом выполнении задачи.
    Это важно, чтобы не загружать её заново для каждого текста.
    """

    print(f"Loading NLP model: {MODEL_NAME}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    print("NLP model loaded")

    return tokenizer, model


def process_text_task(text: str, mode: str) -> str:
    """
    Долгая задача обработки текста.

    Эта функция выполняется в отдельном worker-сервисе.
    Здесь используется небольшая NLP-модель ruT5.
    """

    time.sleep(1)

    text = normalize_text(text)

    if not text:
        return "Пустой текст."

    prompt = build_prompt(text, mode)

    try:
        generated = generate_text(prompt)

        if generated and len(generated.strip()) > 3:
            return format_result(generated, mode)

        return fallback_processing(text, mode)

    except Exception as error:
        print(f"Model error: {error}")
        return fallback_processing(text, mode)


def build_prompt(text: str, mode: str) -> str:
    if mode == "improve":
        return f"улучши текст: {text}"

    if mode == "formal":
        return f"перепиши текст официальным стилем: {text}"

    if mode == "friendly":
        return f"перепиши текст дружелюбным стилем: {text}"

    if mode == "shorten":
        return f"сократи текст: {text}"

    if mode == "fix":
        return f"исправь ошибки в тексте: {text}"

    return f"улучши текст: {text}"


def generate_text(prompt: str) -> str:
    tokenizer, model = load_model()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    outputs = model.generate(
        **inputs,
        max_length=256,
        num_beams=4,
        do_sample=False,
        early_stopping=True
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result.strip()


def format_result(text: str, mode: str) -> str:
    text = normalize_text(text)

    if mode == "improve":
        title = "Улучшенный вариант"

    elif mode == "formal":
        title = "Официальная версия"

    elif mode == "friendly":
        title = "Дружелюбная версия"

    elif mode == "shorten":
        title = "Краткая версия"

    elif mode == "fix":
        title = "Исправленный текст"

    else:
        title = "Результат"

    return f"{title}:\n{text}"


def fallback_processing(text: str, mode: str) -> str:
    """
    Запасной вариант, если модель не смогла сгенерировать нормальный ответ.
    Проект всё равно остаётся работоспособным.
    """

    prepared = normalize_text(text)

    replacements = {
        "привет": "Здравствуйте",
        "очень хорошой": "очень хороший",
        "кажды": "каждый",
        "друзями": "друзьями",
        "жы": "жи",
        "шы": "ши",
    }

    for old, new in replacements.items():
        prepared = prepared.replace(old, new)

    if mode == "shorten":
        words = prepared.split()
        if len(words) > 14:
            prepared = " ".join(words[:14]) + "..."

    if mode == "formal":
        prepared = prepared.replace("я хочу", "Я хотел бы")

    if mode == "friendly":
        prepared = prepared + " Спасибо за внимание!"

    return format_result(prepared, mode)


def normalize_text(text: str) -> str:
    prepared = " ".join(text.strip().split())

    prepared = re.sub(r"\s+([,.!?])", r"\1", prepared)

    if not prepared:
        return ""

    prepared = prepared[0].upper() + prepared[1:]

    if not prepared.endswith((".", "!", "?")):
        prepared += "."

    return prepared