import requests
import json
import pandas as pd

from requests import api

'''
Function returns a DataFrame of 5 day weather forecast
of the city provided in argument
@param: cityName
'''
def fetchWeather(cityName):
    api_key = '411d19dc84c08c5a4c9d6e3ca8dc6951'
    url = 'https://api.openweathermap.org/data/2.5/forecast?q=%s&appid=%s' % (cityName, api_key) 
    print(url + '\n\n')
    response = requests.get(url).text

    response_json = json.loads(response)

    weather_list = []
    columns = ['Date', 'Temperature', 'Feels Like', 'Min Temperature', 'Max Temperature', 'Description', 'Weather']
    for day in response_json['list']:
        weather_list.append([day['dt_txt'], day['main']['temp'], day['main']['feels_like'], day['main']['temp_min'], day['main']['temp_max'], day['weather'][0]['description'], day['weather'][0]['main']])
    
    temps = ['Temperature', 'Feels Like', 'Min Temperature', 'Max Temperature']
    weather_df = pd.DataFrame(data = weather_list, columns=columns)
    for col in temps:
        weather_df[col] = 1.8*(weather_df[col] - 273) + 32
    print(weather_df)
    return weather_df