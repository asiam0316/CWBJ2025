import requests

def get_weather(city, subscription_key):
    
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "query": city
    }
    res = requests.get(url, params=params).json()
    
    if not res.get("results"):
        return {"condition": "不明", "temperature": "不明"}

    position = res["results"][0]["position"]
    lat, lon = position["lat"], position["lon"]

    weather_url = f"https://atlas.microsoft.com/weather/currentConditions/json"
    weather_params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "query": f"{lat},{lon}",
    #    "unit": "metric",
        "language": "ja-jp"
    }
    weather_res = requests.get(weather_url, params=weather_params).json()

    try:
        condition = weather_res["results"][0]["phrases"]["phrase32char"]
        temperature = f"{weather_res['results'][0]['temperature']['value']}℃"
    except Exception:
        condition = "取得失敗"
        temperature = "不明"

    return {
        "city": city,
        "condition": condition,
        "temperature": temperature
    }
