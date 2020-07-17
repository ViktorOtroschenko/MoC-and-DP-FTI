import requests
from pprint import pprint
import json

api_key = 'LVsZi9Eml1VChO0D0qI6tgebiifwXwDUQyT2p868'
main_link = f'https://api.nasa.gov/planetary/apod'

nasa_params = {'api_key': api_key}

response = requests.get(main_link, params=nasa_params)
data = response.json()

with open('nasa.json', 'w') as f:
    json.dump(data, f)

pprint(data)