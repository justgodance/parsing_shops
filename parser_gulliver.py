#!/usr/bin/env python
# coding: utf-8

# In[5]:


import time
import requests
import sqlite3
import re
from multiprocessing import Pool
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
from pathlib import Path
import datetime
#ИМПОРТИРУЕМ SQL
conn = sqlite3.connect('database3')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS gulliver (Наименование text, Цена number, Цена_со_скидкой number, Бренд text, Коллекция text, Название_коллекции text, Возраст text, Цвет text, Состав text,Описание text, Артикул text, Товарная_группа1 text, Товарная_группа2 text, Товарная_группа3 text, Товарная_группа4 text, Размер text, Размер_розница text, Ссылка text, Ссылка_картинка text, Дата text)')
conn.commit()
cursor = conn.execute("SELECT Ссылка, Цена, Цена_со_скидкой from gulliver")
ultradata = [[] for i in range(3)]
for row in cursor:
    ultradata[0].append(row[0])
    ultradata[1].append(row[1])
    ultradata[2].append(row[2])
conn.commit()
def parser(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://www.gulliver.ru/catalog/odezhda/b/gulliver?sort=our_choice,asc" + "&page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')  
    names_mas = []
    prices_mas = []
#ССЫЛКИ
    check = soup.find_all('a',{'class':"card js-product-click-gtm"})
#НАЗВАНИЯ
    names = soup.find_all('span',{'class':"card__title-text"})
    for item in names:
        names_mas.append(item.text.strip())
#ЦЕНЫ
    prices = soup.find_all('div',{'class':"price font-medium card__price"})
    for item in prices:
        prices_mas.append(item.text.strip().replace(" \n ","|"))
    i=0
    images_mas = []
    images = soup.find_all('div',{'class':"card__image"})
    for item in images:
        images_mas.append(item.find('img')['data-src'])
#ЦИКЛ ССЫЛОК
    for item in check:
        dictionary = {}
        details_mas=[]
        p=0
        link = item['href']
        dictionary['Дата']=now.strftime("%d-%m-%Y")
#ССЫЛКА
        dictionary['Ссылка'] = link
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        buf = []
#АРТИКУЛ
        art = soup.find_all('span',{'class':"page-header__article-text"})
        for item in art:
            dictionary['Артикул'] = item.text
#РАЗМЕРЫ
        string=''
        string_ros = ''
        size = soup.find_all('input',{'class':"check-btn__input"})
        for item in size:
            if item["value"] in buf:
                break
            buf.append(item["value"])
            if item['data-rest_count']!="0":
                string+=item["value"].strip()+" "
            elif item['data-rest_count']=="0" and item['data-rests_has_only_retail']=="1":
                string_ros+=item["value"].strip()+" "
            elif item['data-rest_count']=="0" and item['data-rests_has_only_retail']!="1":
                pass
        dictionary["Размер"] = string
        dictionary["Размер_розница"] = string_ros
#КАТЕГОРИЯ
        cat = soup.find_all('a',{'class':"breadcrumb__link"})[:-1]
        cat_mas = []
        for item in cat:
            cat_mas.append(item.text.replace("\n","").replace("/","").strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#ДЕТАЛИ
        details = soup.find_all('span',{'class':"specifications__value specifications__value--small"})
        for k in details:
            details_mas.append(k.text.strip())
        dictionary["Бренд"] = details_mas[0]
        dictionary["Коллекция"] = details_mas[1]
        if details_mas[3]=="Женский" or details_mas[3]=="Мужской":
            dictionary["Название_коллекции"] = "-"
            dictionary["Возраст"] = details_mas[2]
            dictionary["Пол"] = details_mas[3]
            dictionary["Цвет"] = details_mas[4]
            dictionary["Состав"] = details_mas[5].replace("\n",'')
        else:
            dictionary["Название_коллекции"] = details_mas[2]
            dictionary["Возраст"] = details_mas[3]
            dictionary["Пол"] = details_mas[4]
            dictionary["Цвет"] = details_mas[5]
            dictionary["Состав"] = details_mas[6].replace("\n",'')
        if "|" in prices_mas[i]:
            dictionary['Наименование'] = names_mas[i]
            dictionary['Цена'] = prices_mas[i][:prices_mas[i].index("|")]
            dictionary['Цена_со_скидкой'] = prices_mas[i][prices_mas[i].index("|")+1:]
        else:
            dictionary['Наименование'] = names_mas[i]
            dictionary['Цена'] = prices_mas[i]
            dictionary['Цена_со_скидкой'] = "-"
#ОПИСАНИЕ
        description = soup.find_all('p',{'class':"product__description-text pre-lined"})
        for item in description:
            dictionary['Описание'] = item.text.strip()
#ССЫЛКА НА КАРТИНКУ
        dictionary['Ссылка_картинка'] = images_mas[i]
#ЗАБИВАЕМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Коллекция','Название_коллекции','Возраст','Цвет','Состав','Описание','Артикул','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4', 'Размер', 'Размер_розница', 'Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gulliver', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Коллекция','Название_коллекции','Возраст','Цвет','Состав','Описание','Артикул','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4', 'Размер', 'Размер_розница', 'Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('gulliver', conn, if_exists='append', index = False)
        i+=1


# In[ ]:




