import ssl

import aiohttp
import certifi


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: "☀️ Ясно",
    1: "🌤 Преимущественно ясно",
    2: "⛅ Переменная облачность",
    3: "☁️ Пасмурно",
    45: "🌫 Туман",
    48: "🌫 Изморозевый туман",
    51: "🌦 Слабая морось",
    53: "🌦 Морось",
    55: "🌧 Сильная морось",
    56: "🌧 Слабая ледяная морось",
    57: "🌧 Сильная ледяная морось",
    61: "🌦 Небольшой дождь",
    63: "🌧 Дождь",
    65: "🌧 Сильный дождь",
    66: "🌧 Слабый ледяной дождь",
    67: "🌧 Сильный ледяной дождь",
    71: "🌨 Небольшой снег",
    73: "🌨 Снег",
    75: "❄️ Сильный снег",
    77: "❄️ Снежные зёрна",
    80: "🌦 Небольшой ливень",
    81: "🌧 Ливень",
    82: "⛈ Сильный ливень",
    85: "🌨 Слабый снежный заряд",
    86: "❄️ Сильный снежный заряд",
    95: "⛈ Гроза",
    96: "⛈ Гроза с небольшим градом",
    99: "⛈ Гроза с сильным градом",
}


def create_ssl_context() -> ssl.SSLContext:
    """
    Создаёт SSL-контекст с набором доверенных CA-сертификатов certifi.

    Нужен для исправления ошибки:
    SSL: CERTIFICATE_VERIFY_FAILED
    """

    return ssl.create_default_context(
        cafile=certifi.where()
    )


async def get_coordinates(
    session: aiohttp.ClientSession,
    city: str,
) -> dict | None:
    """
    Ищет город через Geocoding API Open-Meteo.

    Возвращает первую найденную локацию в виде словаря
    либо None, если город не найден.
    """

    params = {
        "name": city,
        "count": 1,
        "language": "ru",
        "format": "json",
    }

    async with session.get(
        GEOCODING_URL,
        params=params,
    ) as response:
        print("Геокодирование URL:", response.url)
        print("Геокодирование HTTP-статус:", response.status)

        response.raise_for_status()

        data = await response.json()

    results = data.get("results")

    if not results:
        return None

    return results[0]


async def get_current_weather(city: str) -> dict | None:
    """
    Получает текущую погоду по названию города.

    Возвращает:
    - словарь с готовыми данными о погоде;
    - None, если город не найден.

    Может возбуждать:
    - aiohttp.ClientError при сетевой или HTTP-ошибке;
    - asyncio.TimeoutError при превышении времени ожидания.
    """

    timeout = aiohttp.ClientTimeout(total=15)

    ssl_context = create_ssl_context()

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
    ) as session:
        location = await get_coordinates(
            session=session,
            city=city,
        )

        if location is None:
            return None

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto",
        }

        async with session.get(
            FORECAST_URL,
            params=params,
        ) as response:
            print("Прогноз URL:", response.url)
            print("Прогноз HTTP-статус:", response.status)

            response.raise_for_status()

            data = await response.json()

    current = data["current"]

    return {
        "city": location["name"],
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": data.get(
            "timezone",
            location.get("timezone", ""),
        ),
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
        "description": WEATHER_CODES.get(
            current["weather_code"],
            "Неизвестное состояние погоды",
        ),
    }