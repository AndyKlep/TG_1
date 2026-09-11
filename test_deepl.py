from translator_api import (
    TranslationServiceError,
    check_deepl_connection,
    translate_ru_to_en,
)


def main():
    try:
        usage = check_deepl_connection()

        print("DeepL API доступен.")
        print(f"Использовано символов: {usage['character_count']}")
        print(f"Лимит символов: {usage['character_limit']}")

        original = "Привет! Я изучаю Python и создаю Telegram-бота."
        translation = translate_ru_to_en(original)

        print("\nОригинал:")
        print(original)

        print("\nПеревод:")
        print(translation)

    except TranslationServiceError as error:
        print("\nОшибка проверки DeepL:")
        print(error)


if __name__ == "__main__":
    main()