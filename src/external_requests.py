import requests


WEATHER_API_KEY = '99ba78ee79a2a24bc507362c5288a81b'


class GetWeatherRequest:

    def __init__(self):
        self.session = requests.Session()

    def get_weather(self, city):
        url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&q={}&appid={}'.format(city, WEATHER_API_KEY)
        r = self.session.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        if r is None:
            return None
        else:
            data = r.json()
            weather = data['main']['temp']
            return weather


class CheckCityExisting():

    def __init__(self):
        self.session = requests.Session()

    def check_existing(self, city):
        url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&q={}&appid={}'.format(city, WEATHER_API_KEY)
        r = self.session.get(url)
        if r.status_code == 404:
            return False
        if r.status_code == 200:
            return True
