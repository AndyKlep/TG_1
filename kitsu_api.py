import random
import ssl

import aiohttp
import certifi


KITSU_API_URL = "https://kitsu.io/api/edge"

HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json",
}

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)


class KitsuAPIError(Exception):
    """Ошибка при запросе к Kitsu API."""


def create_ssl_context() -> ssl.SSLContext:
    """
    Создаёт SSL-контекст с актуальным набором корневых
    сертификатов из certifi.
    """

    return ssl.create_default_context(
        cafile=certifi.where()
    )


async def _get_anime(params: dict) -> list[dict]:
    """
    Выполняет GET /anime и возвращает поле data
    из JSON:API-ответа Kitsu.
    """

    url = f"{KITSU_API_URL}/anime"

    ssl_context = create_ssl_context()

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    try:
        async with aiohttp.ClientSession(
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            connector=connector,
        ) as session:
            async with session.get(
                url,
                params=params,
            ) as response:
                response.raise_for_status()
                response_data = await response.json()

    except aiohttp.ClientError as error:
        raise KitsuAPIError(
            f"Не удалось получить данные Kitsu API: {error}"
        ) from error

    return response_data.get("data", [])


def _extract_anime(anime: dict) -> dict:
    """
    Преобразует объект Kitsu JSON:API в словарь,
    удобный для дальнейшего вывода в Telegram.
    """

    attributes = anime.get("attributes", {})

    titles = attributes.get("titles") or {}

    title = (
        titles.get("ru_jp")
        or titles.get("en_jp")
        or titles.get("en")
        or attributes.get("canonicalTitle")
        or "Название не указано"
    )

    start_date = attributes.get("startDate")

    year = start_date[:4] if start_date else "Не указан"

    description = (
        attributes.get("synopsis")
        or "Описание отсутствует."
    )

    poster_image = attributes.get("posterImage") or {}

    image_url = (
        poster_image.get("original")
        or poster_image.get("large")
        or poster_image.get("medium")
        or poster_image.get("small")
    )

    return {
        "id": anime.get("id"),
        "title": title,
        "year": year,
        "description": description,
        "image_url": image_url,
        "popularity_rank": attributes.get("popularityRank"),
    }


async def get_random_anime() -> dict | None:
    """
    Возвращает случайное аниме из случайной страницы выдачи.
    """

    params = {
        "page[limit]": 20,
        "page[offset]": random.randint(0, 10000),
        "sort": "popularityRank",
    }

    anime_list = await _get_anime(params)

    if not anime_list:
        return None

    return _extract_anime(random.choice(anime_list))


async def get_top_anime(position: int) -> dict | None:
    """
    Возвращает аниме с указанной позицией по популярности.
    """

    if position < 1:
        return None

    params = {
        "page[limit]": 1,
        "page[offset]": position - 1,
        "sort": "popularityRank",
    }

    anime_list = await _get_anime(params)

    if not anime_list:
        return None

    return _extract_anime(anime_list[0])


async def get_top_anime_by_year(
    position: int,
    year: int,
) -> dict | None:
    """
    Возвращает аниме с указанной позицией по популярности
    среди аниме указанного года.
    """

    if position < 1:
        return None

    params = {
        "filter[seasonYear]": year,
        "page[limit]": 1,
        "page[offset]": position - 1,
        "sort": "popularityRank",
    }

    anime_list = await _get_anime(params)

    if not anime_list:
        return None

    return _extract_anime(anime_list[0])