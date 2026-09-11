from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тестовая кнопка 1")],
        [
            KeyboardButton(text="Тестовая кнопка 2"),
            KeyboardButton(text="Тестовая кнопка 3"),
        ],
    ],
    resize_keyboard=True,
)


inline_keyboard_test = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Видео",
                url="https://www.youtube.com/watch?v=HfaIcB4Ogxk",
            )
        ]
    ]
)


def test_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    buttons = [
        "Кнопка 1",
        "Кнопка 2",
        "Кнопка 3",
        "Кнопка 4",
    ]

    for index, button_text in enumerate(buttons, start=1):
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"test_button:{index}",
                url='https://www.youtube.com/watch?v=HfaIcB4Ogxk'
            )
        )

    keyboard.adjust(2)

    return keyboard.as_markup()

inline_keyboard_test = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Каталог", callback_data='catalog')],
   [InlineKeyboardButton(text="Новости", callback_data='news')],
   [InlineKeyboardButton(text="Профиль", callback_data='person')]
])