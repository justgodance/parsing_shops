#!/usr/bin/env python
# coding: utf-8

# In[2]:


import time
import requests
import re
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import os
import urllib.request
import re
import pandas as pd
from openpyxl import load_workbook
from pathlib import Path
from openpyxl import Workbook
import datetime
#ПОДКЛЮЧАЕМ SQL
conn = sqlite3.connect('database3')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS gloria (Наименование text, Цена number, Цена_со_скидкой number, Коллекция text, Цвет_на_бирке text, Состав text, Рисунок text, Артикул text, Описание text, Товарная_группа1 text, Товарная_группа2 text, Товарная_группа3 text, Товарная_группа4 text, Размер text, Ссылка text, Ссылка_картинка text, Дата text)')
conn.commit()
cursor = conn.execute("SELECT Ссылка, Цена, Цена_со_скидкой from gloria")
ultradata = [[] for i in range(3)]
for row in cursor:
    ultradata[0].append(row[0])
    ultradata[1].append(row[1])
    ultradata[2].append(row[2])
conn.commit()
def parser(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://www.gloria-jeans.ru/c/kids?q=%3Apriority&page=" + str(n+1) +"&sort=priority"
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ПОЛУЧАЕМ ССЫЛКИ
    links_mas=[]
    links = soup.find_all('a',{'class':"listing-item__img-content js-listing-product-images js-transition-product"})
    for item in links:
        links_mas.append(item['href'])
#ПОЛУЧАЕМ ЦЕНЫ
    price = soup.find_all('div',{'class':"listing-item__info-price"})
    price_mas = []
    for item in price:
        price_mas.append(item.text.strip().replace("\n\n","|"))
    i=0
#ИДЕМ ПО ССЫЛКАМ
    for item in links_mas:
        dictionary = {}
        size_mas=""
        left_mas=[]
        right_mas=[]
        link = "https://www.gloria-jeans.ru" + item
        dictionary['Ссылка'] = link #ССЫЛКА
        dictionary['Дата']=now.strftime("%d-%m-%Y")
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
#КАРТИНКА
        images = soup.find_all('img',{'class':"wrapper-color__item-img"})[:1]
        for item in images:
            dictionary['Ссылка_картинка'] = item['src']
#КАТЕГОРИЯ
        cat = soup.find_all('span',{'itemprop':"name"})
        cat_mas = []
        for item in cat:
            cat_mas.append(item.text.strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#НАИМЕНОВАНИЕ
        name = soup.find_all('h1',{'class':"caption basic-info__caption caption-23 js-name-product"})
        for item in name:
            dictionary["Наименование"] = item.text
#ЦЕНЫ
        if "|" in price_mas[i]:
            dictionary["Цена"] = price_mas[i][price_mas[i].index("|")+1:]
            dictionary["Цена_со_скидкой"] = price_mas[i][:price_mas[i].index("|")]
        else:
            dictionary["Цена"] = price_mas[i]
            dictionary["Цена_со_скидкой"]="-"
#РАЗМЕРЫ
        size = soup.find_all('div',{'class':"block-size__item js-size-item"})
        for item in size:
            size_mas+=item.text.strip()+" "
        dictionary["Размер"] = size_mas
#ДЕТАЛИ
        left = soup.find_all('p',{'class':"cell-left"})
        right = soup.find_all('p',{'class':"cell-right"})
        for item in left:
            left_mas.append(item.text.strip().replace(":",""))
        for item in right:
            right_mas.append(item.text.strip())
        if "Коллекция" in left_mas:
            dictionary["Коллекция"] = right_mas[left_mas.index("Коллекция")]
        else:
            dictionary["Коллекция"] = "-"
        if "Состав" in left_mas:
            dictionary["Состав"] = right_mas[left_mas.index("Состав")]
        else:
            dictionary["Состав"] = "-"
        if "Рисунок" in left_mas:
            dictionary["Рисунок"] = right_mas[left_mas.index("Рисунок")]
        else:
            dictionary["Рисунок"] = "-"
        if "Артикул" in left_mas:
            dictionary["Артикул"] = right_mas[left_mas.index("Артикул")]
        else:
            dictionary["Артикул"] = "-"
        if "Цвет на бирке" in left_mas:
            dictionary["Цвет_на_бирке"] = right_mas[left_mas.index("Цвет на бирке")]
        else:
            dictionary["Цвет_на_бирке"] = "-"
#ОПИСАНИЕ
        description = soup.find_all('div',{'class':"product-information__item--text js-description-product-card"})
        for item in description:
              dictionary["Описание"] = item.text.strip()
#ЗАГРУЖАЕМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Коллекция','Цвет_на_бирке','Состав','Рисунок','Артикул', 'Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gloria', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Коллекция','Цвет_на_бирке','Состав','Рисунок','Артикул', 'Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gloria', conn, if_exists='append', index = False)
        i+=1


# In[3]:


def parser2(n):
    print(n)
    dictionary = {}
    now = datetime.datetime.now()
    link = "https://www.gloria-jeans.ru/c/teenagers?q=%3Apriority&page=" + str(n+1) +"&sort=priority"
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links_mas=[]
    links = soup.find_all('a',{'class':"listing-item__img-content js-listing-product-images js-transition-product"})
    for item in links:
        links_mas.append(item['href'])
#ЦЕНЫ
    price = soup.find_all('div',{'class':"listing-item__info-price"})
    price_mas = []
    for item in price:
        price_mas.append(item.text.strip().replace("\n\n","|"))
    i=0
#ИДЕМ ПО ССЫЛКАМ
    for item in links_mas:
        size_mas=""
        left_mas=[]
        right_mas=[]
        link = "https://www.gloria-jeans.ru" + item
        dictionary['Ссылка'] = link #ССЫЛКА
        dictionary['Дата']=now.strftime("%d-%m-%Y")
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
#КАРТИНКА
        images = soup.find_all('img',{'class':"wrapper-color__item-img"})[:1]
        for item in images:
            dictionary['Ссылка_картинка'] = item['src']
#КАТЕГОРИЯ
        cat = soup.find_all('span',{'itemprop':"name"})
        cat_mas = []
        for item in cat:
            cat_mas.append(item.text.strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#НАЗВАНИЕ
        name = soup.find_all('h1',{'class':"caption basic-info__caption caption-23 js-name-product"})
        for item in name:
            dictionary["Наименование"] = item.text
#ЦЕНЫ
        if "|" in price_mas[i]:
            dictionary["Цена"] = price_mas[i][price_mas[i].index("|")+1:]
            dictionary["Цена_со_скидкой"] = price_mas[i][:price_mas[i].index("|")]
        else:
            dictionary["Цена"] = price_mas[i]
            dictionary["Цена_со_скидкой"]="-"
#РАЗМЕР
        size = soup.find_all('div',{'class':"block-size__item js-size-item"})
        for item in size:
            size_mas+=item.text.strip()+" "
        dictionary["Размер"] = size_mas
#ДЕТАЛИ
        left = soup.find_all('p',{'class':"cell-left"})
        right = soup.find_all('p',{'class':"cell-right"})
        for item in left:
            left_mas.append(item.text.strip().replace(":",""))
        for item in right:
            right_mas.append(item.text.strip())
        if "Коллекция" in left_mas:
            dictionary["Коллекция"] = right_mas[left_mas.index("Коллекция")]
        else:
            dictionary["Коллекция"] = "-"
        if "Состав" in left_mas:
            dictionary["Состав"] = right_mas[left_mas.index("Состав")]
        else:
            dictionary["Состав"] = "-"
        if "Рисунок" in left_mas:
            dictionary["Рисунок"] = right_mas[left_mas.index("Рисунок")]
        else:
            dictionary["Рисунок"] = "-"
        if "Артикул" in left_mas:
            dictionary["Артикул"] = right_mas[left_mas.index("Артикул")]
        else:
            dictionary["Артикул"] = "-"
        if "Цвет на бирке" in left_mas:
            dictionary["Цвет_на_бирке"] = right_mas[left_mas.index("Цвет на бирке")]
        else:
            dictionary["Цвет_на_бирке"] = "-"
#ОПИСАНИЕ
        description = soup.find_all('div',{'class':"product-information__item--text js-description-product-card"})
        for item in description:
              dictionary["Описание"] = item.text.strip()
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Коллекция','Цвет_на_бирке','Состав','Рисунок','Артикул', 'Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gloria', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Коллекция','Цвет_на_бирке','Состав','Рисунок','Артикул', 'Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gloria', conn, if_exists='append', index = False)
        i+=1


# In[ ]:




