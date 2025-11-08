import hashlib
import random
import string


def generate_ekn_code(work_center_name: str, length: int = 8) -> str:
    """
    Генерирует уникальный код для рабочего центра (ekn_code) на основе имени.
    length - длина случайной части кода
    """
    # Хешируем имя рабочего центра
    name_hash = hashlib.sha1(work_center_name.encode("utf-8")).hexdigest()[:4].upper()

    # Генерируем случайную последовательность букв и цифр
    random_part = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )

    return f"{name_hash}-{random_part}"
