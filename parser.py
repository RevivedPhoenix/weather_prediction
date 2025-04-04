import os
import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import configparser
from dateutil import parser
from datetime import datetime

dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, "config.ini"))

FILE_NAME = eval(config["File_name"]["FILE_NAME"])
MONTHS = eval(config["Months"]["MONTHS"])
OTHER_MONTHS = eval(config["Months"]["OTHER_MONTHS"])
API_KEY = eval(config["Api_key"]["API_KEY"])
months_translate = {'января': 'January', 'февраля': 'February', 'марта': 'March',
     'апреля': 'April', 'мая': 'May', 'июня': 'June', 'июля': 'July', 
     'августа': 'August', 'сентября': 'September', 'октября': 'October',
     'ноября': 'November', 'декабря': 'December'}

today = datetime.today().date()

#response = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Minsk/2015-01-01/2015-01-31?unitGroup=metric&key={API_KEY}')

def parser_dates(r):
    l = []
    soup = bs(r.text, "html.parser")
    date_array = soup.find_all('div', class_='heading heading_minor heading_line')
    for date in date_array:
        new_date = " ".join([date.text.split()[0], months_translate[date.text.split()[1]]]) + ' ' + date.text.split()[2]
        parse_date = parser.parse(new_date)
        format_date = datetime.strftime(parse_date,"%Y-%m-%d")
        if format_date <= str(today):
            l.append(format_date)
    return l

def parser_temperature(r):
    l_temp = []
    soup = bs(r.text, "html.parser")
    temperature_array = soup.find_all('div', class_='day__temperature')
    for temperature in temperature_array:
        res_temp = temperature.text.split('\n')[0].split('°')
        l_temp.append(res_temp[0])
    l_day_temp = l_temp[2::4]
    l_evening_temp = l_temp[3::4]
    l_night_temp = l_temp[0::4]
    l_morning = l_temp[1::4]
    return l_day_temp, l_evening_temp, l_night_temp, l_morning

def parse_part1():
    df = pd.DataFrame(columns=['Date', 'Morning temperature', 'Daily temperature', 'Evening temperature', 'Night temperature']) 
    for elem in MONTHS:
        for i in range(1,32):
            URL = f"https://pogoda.mail.ru/prognoz/minsk/{i}-{elem}/"
            r = requests.get(URL, timeout=10000)
            l = []
            l = parser_dates(r)
            l_day_temp, l_evening_temp, l_night_temp, l_morning = [], [], [], []
            l_day_temp, l_evening_temp, l_night_temp, l_morning = parser_temperature(r)
                
            d = {'Date': l, 'Morning temperature': l_morning, 'Daily temperature': l_day_temp, 'Evening temperature': l_evening_temp, 'Night temperature': l_night_temp} 
            if len(d['Date']) != len(d['Daily temperature']):
                d['Morning temperature'].pop(0)
                d['Daily temperature'].pop(0)
                d['Evening temperature'].pop(0)
                d['Night temperature'].pop(0)
            df = pd.concat([df, pd.DataFrame(d)], ignore_index=True)
    return df

def parse_part2():
    df = pd.DataFrame()
    for elem in OTHER_MONTHS:
        for i in range(1,32):
            URL = f"https://pogoda.mail.ru/prognoz/minsk/{i}-{elem}/"
            r = requests.get(URL, timeout=10000)
            l = []
            l = parser_dates(r)
            l_day_temp, l_evening_temp, l_night_temp, l_morning = [], [], [], []
            l_day_temp, l_evening_temp, l_night_temp, l_morning = parser_temperature(r)
            if len(d['Date']) != len(d['Daily temperature']):
                d['Morning temperature'].pop(0)
                d['Daily temperature'].pop(0)
                d['Evening temperature'].pop(0)
                d['Night temperature'].pop(0)
            d = {'Date': l, 'Morning temperature': l_morning, 'Day temperature': l_day_temp, 'Evening temperature': l_evening_temp, 'Night temperature': l_night_temp}
            
            df = pd.concat([df, pd.DataFrame(d)], ignore_index=True)
    return df

df = parse_part1()
df2 = parse_part2()
df_temperature = pd.concat([df, df2], ignore_index=True)

df_temperature.to_csv(FILE_NAME)