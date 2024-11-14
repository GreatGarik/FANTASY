import requests
from bs4 import BeautifulSoup
import csv
import os
import time


header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
          'Accept': 'ext/html,application/xhtml+txml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}


# Получение URL товаров со странички
#url = input('Введите URL для опроса:    ')
url = f'https://www.espn.com/f1/results/_/id/600041156'
response = requests.get(url=url, headers=header)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.find_all(сclass_="hide-mobile"))

