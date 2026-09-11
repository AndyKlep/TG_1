import deepl

from config import DEEPL_API_KEY


class TranslationServiceError(Exception):
    """Ошибка при обращении к сервису DeepL."""


def get_translator() -> deepl.Translator:
    """
    Создаёт объект клиента DeepL.

    Если ключ относится к DeepL API Free и оканчивается на ':fx',
    задаётся endpoint бесплатного API.
    """

    if not DEEPL_API_KEY:
        raise TranslationServiceError(
            "В файле config.py не задан DEEPL_API_KEY."
        )

    server_url = None

    if DEEPL_API_KEY.endswith(":fx"):
        server_url = "https://api-free.deepl.com"

    return deepl.Translator(
        auth_key=DEEPL_API_KEY,
        server_url=server_url,
    )


def check_deepl_connection() -> dict:
    """
    Проверяет соединение с DeepL, корректность ключа и остаток квоты.

    Возвращает словарь:
    {
        "character_count": число уже переведённых символов,
        "character_limit": месячный лимит символов
    }
    """

    try:
        translator = get_translator()
        usage = translator.get_usage()

        return {
            "character_count": usage.character.count,
            "character_limit": usage.character.limit,
        }

    except deepl.AuthorizationException as error:
        raise TranslationServiceError(
            "DeepL отклонил API-ключ. Проверьте DEEPL_API_KEY "
            "в config.py и статус API-подписки."
        ) from error

    except deepl.QuotaExceededException as error:
        raise TranslationServiceError(
            "Лимит символов DeepL API исчерпан."
        ) from error

    except deepl.ConnectionException as error:
        raise TranslationServiceError(
            f"Не удалось подключиться к DeepL: {error}"
        ) from error

    except deepl.DeepLException as error:
        raise TranslationServiceError(
            f"Ошибка DeepL API: {type(error).__name__}: {error}"
        ) from error


def translate_ru_to_en(text: str) -> str:
    """
    Переводит русский текст на английский через DeepL API.

    Возвращает строку с переводом или возбуждает TranslationServiceError.
    """

    text = text.strip()

    if not text:
        raise TranslationServiceError(
            "Получен пустой текст для перевода."
        )

    try:
        translator = get_translator()

        result = translator.translate_text(
            text=text,
            source_lang="RU",
            target_lang="EN-US",
        )

        return result.text

    except deepl.AuthorizationException as error:
        raise TranslationServiceError(
            "DeepL отклонил API-ключ. Проверьте DEEPL_API_KEY "
            "в config.py."
        ) from error

    except deepl.QuotaExceededException as error:
        raise TranslationServiceError(
            "Лимит символов DeepL API исчерпан."
        ) from error

    except deepl.ConnectionException as error:
        raise TranslationServiceError(
            f"Не удалось подключиться к DeepL: {error}"
        ) from error

    except deepl.DeepLException as error:
        raise TranslationServiceError(
            f"Ошибка DeepL API: {type(error).__name__}: {error}"
        ) from error