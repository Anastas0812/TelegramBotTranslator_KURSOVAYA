import requests
import bs4
from bs4 import BeautifulSoup as BS
import lxml.etree
import csv
import pandas as pd
import io
import pprint


URL = 'http://wordsteps.com/vocabulary/words/136958/8000+%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D1%8B%D1%85+%D0%B0%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D1%85+%D1%81%D0%BB%D0%BE%D0%B2'

"""download the web page code"""
source = requests.get(URL).text
# print(source)

"""convert text to BS object"""
soup = bs4.BeautifulSoup(source, 'lxml')
# print(soup)

"""select a table"""
table = soup.select_one('#DictWordsList')
# print(table)

"""Creation pandas data frame"""
dict_eng_rus = pd.read_html(io.StringIO(str(table)))
dict_eng_rus = dict_eng_rus[1]
pprint.pprint(dict_eng_rus)
dict_eng_rus.to_csv('1table_income.csv', encoding='utf-8')
"""parsing is complete, make changes to the table"""


#ПОЛОЖИТЬ ТАБЛИЦУ В РЕПОЗИТОРИЙ