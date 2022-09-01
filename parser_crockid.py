#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
#ПОДГРУЖАЕМ SQL
conn = sqlite3.connect('database3')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS crockid (Наименование text, Цена number, Цена_со_скидкой number, Пол text, Категория text,Бренд text, Состав text, Тип_ткани text, Цвет text, Сезон text, Артикул text, Коллекция text, Описание text, Товарная_группа1 text, Товарная_группа2 text, Товарная_группа3 text, Товарная_группа4 text, Размер text, Ссылка text, Ссылка_картинка text, Дата text)')
conn.commit()
cursor = conn.execute("SELECT Ссылка, Цена, Цена_со_скидкой from crockid")
ultradata = [[] for i in range(3)]
for row in cursor:
    ultradata[0].append(row[0])
    ultradata[1].append(row[1])
    ultradata[2].append(row[2])
conn.commit()
def parser(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://www.crockid.ru/catalog/odezhda-dlya-malchikov?page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links = soup.find_all('div',{'class':"mid"})
    links_mas=[]
    for item in links:
        links_mas.append(item.find('a')['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('li',{'class':"item _card_"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('a').find('img')['src'])
    k=0
#ИДЕМ ПО ССЫЛКАМ
    for item in links_mas:
        dictionary ={}
        link = "https://www.crockid.ru" + item
        dictionary["Ссылка"] = link
        dictionary['Дата']=now.strftime("%d-%m-%Y")
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
#НАИМЕНОВАНИЕ И АРТИКУЛ
        name = soup.find_all('h1',{'class':"name"})
        names = []
        for item in name:
            names=re.split(r'\, ',item.text)
        dictionary['Наименование'] = names[0]
        dictionary['Артикул'] = names[1]
#КАРТИНКА
        dictionary['Ссылка_картинка']=images_mas[k]
        k+=1
#ДЕТАЛИ
        details = soup.find_all('div',{'class':"desc _about"})
        details_mas=[]
        for item in details:
            details_mas=item.text.split()
        if "Бренд:" in details_mas:
            dictionary['Бренд'] = details_mas[details_mas.index("Бренд:")+1]
        string=''
        if "Состав:" in details_mas and "Сезон:" in details_mas:
            index = details_mas.index("Состав:")+1
            while details_mas[index]!="Сезон:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Состав'] = string
        if "Сезон:" in details_mas:
            dictionary['Сезон'] = details_mas[details_mas.index("Сезон:")+1]
        if "ткани:" in details_mas:
            dictionary['Тип_ткани'] = details_mas[details_mas.index("ткани:")+1]
        string=''
        if "Коллекция:" in details_mas:
            index = details_mas.index("Коллекция:")+1
            while details_mas[index]!="Цвет:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Коллекция'] = string
        string=''
        if "Цвет:" in details_mas:
            index = details_mas.index("Цвет:")+1
            while details_mas[index]!="Сертификат":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Цвет'] = string
#ЦЕНЫ
        prices = soup.find_all('div',{'class':"cost"})
        price_mas = []
        price_mas_sale=[]
        for item in prices:
            price_mas.append(item.text)
        price_mas_sale=re.split(r'\n',price_mas[0])
        if price_mas_sale[2]!="":
            dictionary['Цена'] = price_mas_sale[2]
            dictionary['Цена_со_скидкой'] = price_mas_sale[1]
        else:
            dictionary['Цена'] = price_mas_sale[1]
            dictionary['Цена_со_скидкой'] = "-"
#РАЗМЕРЫ
        ids = soup.find_all('span',{'data-action':"showSizesTable"})
        for item in ids:
            id = item["data-id"]
        sizes = soup.find_all('li',{'data-good-id':id})
        sizes_mas = ''
        for item in sizes:
            if item['data-total']!="0":
                sizes_mas+=item.text.strip()+" "
        dictionary['Размер'] = sizes_mas
#КАТЕГОРИЯ
        types = soup.find_all('span',{'itemprop':"name"})[:-1]
        cat_mas=[]
        for item in types:
            cat_mas.append(item.text.strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#ОПИСАНИЕ
        description = soup.find_all('div',{'class':"desc"})[1]
        string= ""
        for item in description:
            string+= item.text.strip()
        dictionary["Описание"] = string
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 
def parser2(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://www.crockid.ru/catalog/girls?page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ИЩЕМ ССЫЛКИ
    links = soup.find_all('div',{'class':"mid"})
    links_mas=[]
    for item in links:
        links_mas.append(item.find('a')['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('li',{'class':"item _card_"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('a').find('img')['src'])
    k=0
#ИДЕМ ПО ССЫЛКАМ
    for item in links_mas:
        dictionary ={}
        link = "https://www.crockid.ru" + item
        dictionary["Ссылка"] = link
        dictionary['Дата']=now.strftime("%d-%m-%Y")
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
#НАЗВАНИЕ И АРТИКУЛ
        name = soup.find_all('h1',{'class':"name"})
        names = []
        for item in name:
            names=re.split(r'\, ',item.text)
        dictionary['Наименование'] = names[0]
        dictionary['Артикул'] = names[1]
#КАРТИНКА
        dictionary['Ссылка_картинка']=images_mas[k]
        k+=1
#ДЕТАЛИ
        details = soup.find_all('div',{'class':"desc _about"})
        details_mas=[]
        for item in details:
            details_mas=item.text.split()
        if "Бренд:" in details_mas:
            dictionary['Бренд'] = details_mas[details_mas.index("Бренд:")+1]
        string=''
        if "Состав:" in details_mas and "Сезон:" in details_mas:
            index = details_mas.index("Состав:")+1
            while details_mas[index]!="Сезон:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Состав'] = string
        if "Сезон:" in details_mas:
            dictionary['Сезон'] = details_mas[details_mas.index("Сезон:")+1]
        if "ткани:" in details_mas:
            dictionary['Тип_ткани'] = details_mas[details_mas.index("ткани:")+1]
        string=''
        if "Коллекция:" in details_mas:
            index = details_mas.index("Коллекция:")+1
            while details_mas[index]!="Цвет:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Коллекция'] = string
        string=''
        if "Цвет:" in details_mas:
            index = details_mas.index("Цвет:")+1
            while details_mas[index]!="Сертификат":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Цвет'] = string
#ЦЕНЫ
        prices = soup.find_all('div',{'class':"cost"})
        price_mas = []
        price_mas_sale=[]
        for item in prices:
            price_mas.append(item.text)
        price_mas_sale=re.split(r'\n',price_mas[0])
        if price_mas_sale[2]!="":
            dictionary['Цена'] = price_mas_sale[2]
            dictionary['Цена_со_скидкой'] = price_mas_sale[1]
        else:
            dictionary['Цена'] = price_mas_sale[1]
            dictionary['Цена_со_скидкой'] = "-"
#РАЗМЕРЫ
        ids = soup.find_all('span',{'data-action':"showSizesTable"})
        for item in ids:
            id = item["data-id"]
        sizes = soup.find_all('li',{'data-good-id':id})
        sizes_mas = ''
        for item in sizes:
            if item['data-total']!="0":
                sizes_mas+=item.text.strip()+" "
        dictionary['Размер'] = sizes_mas
#КАТЕГОРИЯ
        types = soup.find_all('span',{'itemprop':"name"})[:-1]
        cat_mas=[]
        for item in types:
            cat_mas.append(item.text.strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#ОПИСАНИЕ
        description = soup.find_all('div',{'class':"desc"})[1]
        string= ""
        for item in description:
            string+= item.text.strip()
        dictionary["Описание"] = string
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 
def parser3(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://www.crockid.ru/catalog/baby?page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ПОЛУЧАЕМ ССЫЛКИ
    links = soup.find_all('div',{'class':"mid"})
    links_mas=[]
    for item in links:
        links_mas.append(item.find('a')['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('li',{'class':"item _card_"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('a').find('img')['src'])
    k=0
#ИДЕМ ПО ССЫЛКАМ
    for item in links_mas:
        dictionary ={}
        link = "https://www.crockid.ru" + item
        dictionary["Ссылка"] = link
        dictionary['Дата']=now.strftime("%d-%m-%Y")
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
#НАЗВАНИЕ И АРТИКУЛ
        name = soup.find_all('h1',{'class':"name"})
        names = []
        for item in name:
            names=re.split(r'\, ',item.text)
        dictionary['Наименование'] = names[0]
        dictionary['Артикул'] = names[1]
#КАРТИНКА
        dictionary['Ссылка_картинка']=images_mas[k]
        k+=1
#ДЕТАЛИ
        details = soup.find_all('div',{'class':"desc _about"})
        details_mas=[]
        for item in details:
            details_mas=item.text.split()
        if "Бренд:" in details_mas:
            dictionary['Бренд'] = details_mas[details_mas.index("Бренд:")+1]
        string=''
        if "Состав:" in details_mas and "Сезон:" in details_mas:
            index = details_mas.index("Состав:")+1
            while details_mas[index]!="Сезон:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Состав'] = string
        if "Сезон:" in details_mas:
            dictionary['Сезон'] = details_mas[details_mas.index("Сезон:")+1]
        if "ткани:" in details_mas:
            dictionary['Тип_ткани'] = details_mas[details_mas.index("ткани:")+1]
        string=''
        if "Коллекция:" in details_mas:
            index = details_mas.index("Коллекция:")+1
            while details_mas[index]!="Цвет:":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Коллекция'] = string
        string=''
        if "Цвет:" in details_mas:
            index = details_mas.index("Цвет:")+1
            while details_mas[index]!="Сертификат":
                string+=details_mas[index] + " "
                index+=1
            dictionary['Цвет'] = string
#ЦЕНЫ
        prices = soup.find_all('div',{'class':"cost"})
        price_mas = []
        price_mas_sale=[]
        for item in prices:
            price_mas.append(item.text)
        price_mas_sale=re.split(r'\n',price_mas[0])
        if price_mas_sale[2]!="":
            dictionary['Цена'] = price_mas_sale[2]
            dictionary['Цена_со_скидкой'] = price_mas_sale[1]
        else:
            dictionary['Цена'] = price_mas_sale[1]
            dictionary['Цена_со_скидкой'] = "-"
#РАЗМЕРЫ
        ids = soup.find_all('span',{'data-action':"showSizesTable"})
        for item in ids:
            id = item["data-id"]
        sizes = soup.find_all('li',{'data-good-id':id})
        sizes_mas = ''
        for item in sizes:
            if item['data-total']!="0":
                sizes_mas+=item.text.strip()+" "
        dictionary['Размер'] = sizes_mas
#КАТЕГОРИЯ
        types = soup.find_all('span',{'itemprop':"name"})[:-1]
        cat_mas=[]
        for item in types:
            cat_mas.append(item.text.strip())
        dictionary['Товарная_группа1'] = cat_mas[1]
        if len(cat_mas)>2:
            dictionary['Товарная_группа2'] = cat_mas[2]
        if len(cat_mas)>3:
            dictionary['Товарная_группа3'] = cat_mas[3]
        if len(cat_mas)>4:
            dictionary['Товарная_группа4'] = cat_mas[4]
#ОПИСАНИЕ
        description = soup.find_all('div',{'class':"desc"})[1]
        string= ""
        for item in description:
            string+= item.text.strip()
        dictionary["Описание"] = string
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Бренд','Состав','Тип_ткани','Цвет','Сезон','Артикул','Коллекция','Описание','Товарная_группа1','Товарная_группа2','Товарная_группа3','Товарная_группа4','Размер','Ссылка','Ссылка_картинка','Дата'])
            df.to_sql('crockid', conn, if_exists='append', index = False) 

# In[ ]:




