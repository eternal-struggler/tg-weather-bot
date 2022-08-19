import requests
from datetime import datetime

from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


def city_to_lat_lon(city_name):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={open_weather_token}"
        )
        return r.json()[0]["lat"], r.json()[0]["lon"]

    except Exception as ex:
        print(ex)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города и я пришлю информацию о погоде")


@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_emoji = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U00002614",
        "Fog": "Туман \U00002614",
    }

    try:
        lat, lon = city_to_lat_lon(message["text"])

        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_token}"
            f"&units=metric"
        )
        data = r.json()

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
        sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

        summary = data["weather"][0]["main"]

        if summary in code_to_emoji:
            description = code_to_emoji[summary]
        else:
            description = "Я не понимаю, что за погода у тебя за окном..."

        await message.reply(f"***{datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                            f"Погода в городе {message['text']}:\n"
                            f"Температура: {temperature}℃ ({description})\n"
                            f"Влажность: {humidity}%\n "
                            f"Давление: {pressure} мм.рт.ст.\n"
                            f"Скорость ветра: {wind} м/сек\n"
                            f"Рассвет: {sunrise_timestamp}\n "
                            f"Закат: {sunset_timestamp}")

    except TypeError:
        await message.reply("\U00002620 Проверьте название города \U00002620")


if __name__ == "__main__":
    executor.start_polling(dp)
