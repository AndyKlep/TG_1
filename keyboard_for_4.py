from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib3.util import url

start_keys = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Привет!"),
        KeyboardButton(text="Пока!"),
        ],
    ],
    resize_keyboard=True,
)


inline_arkham_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Правила",
                url="https://ru.arkhamdb.com/rules",
            )
        ],
        [
            InlineKeyboardButton(
                text='Колоды',
                url='https://ru.arkhamdb.com/decklists',
            )
        ],
        [
            InlineKeyboardButton(
                text='FAQ',
                url='https://ru.arkhamdb.com/faqs',
            )
        ]

    ]
)

inline_first_call = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Показать больше',
                callback_data="show_more",
            )
        ]
    ]
)

inline_second_call = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Опция 1',
                callback_data="option_1"

            )
        ],
[
            InlineKeyboardButton(
                text='Опция 2',
                callback_data="option_2"
            )
        ]
    ]
)