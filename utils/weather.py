import requests
from datetime import datetime
import pytz

def get_weather(city, today, api_key):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "lang": "ja",
        "units": "metric"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # 日本時間に変換
    jst = pytz.timezone("Asia/Tokyo")

    # 結果格納リスト
    today_forecast = []

    for entry in data["list"]:
        # 予報時間（UTC）をJSTに変換
        dt_utc = datetime.utcfromtimestamp(entry["dt"])
        dt_jst = dt_utc.replace(tzinfo=pytz.utc).astimezone(jst)

        if dt_jst.date() == today:
            forecast = {
                "time": dt_jst.strftime("%H:%M"),
                "weather": entry["weather"][0]["description"],
                "temp": entry["main"]["temp"],
                "humidity": entry["main"]["humidity"],
                "wind_speed": entry["wind"]["speed"],
                "rain_mm": entry.get("rain", {}).get("3h", 0.0)
            }
            today_forecast.append(forecast)

    return today_forecast