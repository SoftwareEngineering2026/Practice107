import os
import time
from collections import Counter

while True:

    if os.path.exists("/data/task.txt"):

        with open(
            "/data/task.txt",
            "r",
            encoding="utf-8"
        ) as f:
            text = f.read()

        time.sleep(5)

        words = text.split()

        word_count = len(words)

        char_count = len(text)

        if words:
            common_word = Counter(words).most_common(1)[0][0]
        else:
            common_word = "нет"

        result = f"""
Количество слов: {word_count}
Количество символов: {char_count}
Самое частое слово: {common_word}
"""

        with open(
            "/data/result.txt",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(result)

        os.remove("/data/task.txt")

    time.sleep(1)