#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
c.execute('CREATE TABLE IF NOT EXISTS acoolakids (Наименование text, Цена number, Цена_со_скидкой number,Артикул text, Состав text, Цвет text, Описание text,Товарная_группа1 text, Товарная_группа2 text, Размер text, Ссылка text, Ссылка_картинка text,Дата text)')
conn.commit()
cursor = conn.execute("SELECT Ссылка, Цена, Цена_со_скидкой from acoolakids")
ultradata = [[] for i in range(3)]
for row in cursor:
    ultradata[0].append(row[0])
    ultradata[1].append(row[1])
    ultradata[2].append(row[2])
conn.commit()
def parser(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://acoolakids.ru/vsya-odezhda-dlya-devochek-2-8?tab=&sort_new=desc&limit=30&page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links = soup.find_all('a',{'class':"ak-card-product-min show"})
    links_mas = []
    for item in links:
        links_mas.append(item['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('div',{'class':"link"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('img')['src'])
    k = 0
    for item in links_mas:
        dictionary = {}
#ПОЛ И ВОЗРАСТ
        dictionary['Товарная_группа1'] = 'Девочки'
        dictionary['Товарная_группа2'] = 'От 3 до 8 лет'
        dictionary['Дата']=now.strftime("%d-%m-%Y")
#ССЫЛКИ
        link = item
        dictionary['Ссылка'] = link
        dictionary['Ссылка_картинка'] = images_mas[k]
        k+=1
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  
#НАИМЕНОВАНИЕ
        name = soup.find_all('h2',{'class':"ak-product-description__title"})
        if name ==[]:
            continue
        for item in name:
            dictionary['Наименование'] = item.text.strip()
#АРТИКУЛ
        art = soup.find_all('div',{'class':"code"})
        for item in art:
            dictionary['Артикул']=item.text.split()[1]
#ЦВЕТ
        colour = soup.find_all('li',{'class':"tooltipster"})
        for item in colour:
            dictionary['Цвет']=item['data-title']
#ЦЕНЫ
        price = soup.find_all('div',{'class':"costs relative"})
        price_mas=[]
        for item in price:
            price_mas=(item.text.replace("\n","").split('.'))
        if len(price_mas)>2:
            dictionary['Цена'] = price_mas[1]
            dictionary['Цена_со_скидкой'] = price_mas[0]
        else:
            dictionary['Цена'] = price_mas[0]
            dictionary['Цена_со_скидкой'] = '-'
#РАЗМЕРЫ
        size = soup.find_all('input',{'type':"radio"})
        size_mas=''
        for item in size:
            try:
                if item['disabled']=='disabled':
                    pass
            except KeyError:
                size_mas+=item['value']+' '
        dictionary['Размер'] = size_mas
#ОПИСАНИЕ И СОСТАВ
        desc = soup.find_all('div',{'class':"text"})[0]
        description = []
        for item in desc:
            description.append(item.text.split("\n"))
        dictionary['Состав']=description[1][1]
        dictionary['Описание']=description[1][2]
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
def parser2(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://acoolakids.ru/vsya-odezhda-dlya-devochek-8-14?tab=&sort_new=desc&limit=30&page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links = soup.find_all('a',{'class':"ak-card-product-min show"})
    links_mas = []
    for item in links:
        links_mas.append(item['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('div',{'class':"link"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('img')['src'])
    k = 0
    for item in links_mas:
        dictionary = {}
#ПОЛ И ВОЗРАСТ
        dictionary['Товарная_группа1'] = 'Девочки'
        dictionary['Товарная_группа2'] = 'От 8 до 14 лет'
        dictionary['Дата']=now.strftime("%d-%m-%Y")
#ССЫЛКИ
        link = item
        dictionary['Ссылка'] = link
        dictionary['Ссылка_картинка'] = images_mas[k]
        k+=1
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  
#НАИМЕНОВАНИЕ
        name = soup.find_all('h2',{'class':"ak-product-description__title"})
        if name ==[]:
            continue
        for item in name:
            dictionary['Наименование'] = item.text.strip()
#АРТИКУЛ
        art = soup.find_all('div',{'class':"code"})
        for item in art:
            dictionary['Артикул']=item.text.split()[1]
#ЦВЕТ
        colour = soup.find_all('li',{'class':"tooltipster"})
        for item in colour:
            dictionary['Цвет']=item['data-title']
#ЦЕНЫ
        price = soup.find_all('div',{'class':"costs relative"})
        price_mas=[]
        for item in price:
            price_mas=(item.text.replace("\n","").split('.'))
        if len(price_mas)>2:
            dictionary['Цена'] = price_mas[1]
            dictionary['Цена_со_скидкой'] = price_mas[0]
        else:
            dictionary['Цена'] = price_mas[0]
            dictionary['Цена_со_скидкой'] = '-'
#РАЗМЕРЫ
        size = soup.find_all('input',{'type':"radio"})
        size_mas=''
        for item in size:
            try:
                if item['disabled']=='disabled':
                    pass
            except KeyError:
                size_mas+=item['value']+' '
        dictionary['Размер'] = size_mas
#ОПИСАНИЕ И СОСТАВ
        desc = soup.find_all('div',{'class':"text"})[0]
        description = []
        for item in desc:
            description.append(item.text.split("\n"))
        dictionary['Состав']=description[1][1]
        dictionary['Описание']=description[1][2]
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
def parser3(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://acoolakids.ru/vsya-odezhda-dlya-malchikov-3-8?tab=&sort_new=desc&limit=30&page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links = soup.find_all('a',{'class':"ak-card-product-min show"})
    links_mas = []
    for item in links:
        links_mas.append(item['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('div',{'class':"link"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('img')['src'])
    k = 0
    for item in links_mas:
        dictionary = {}
#ПОЛ И ВОЗРАСТ
        dictionary['Товарная_группа1'] = 'Мальчики'
        dictionary['Товарная_группа2'] = 'От 3 до 8 лет'
        dictionary['Дата']=now.strftime("%d-%m-%Y")
#ССЫЛКИ
        link = item
        dictionary['Ссылка'] = link
        dictionary['Ссылка_картинка'] = images_mas[k]
        k+=1
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  
#НАИМЕНОВАНИЕ
        name = soup.find_all('h2',{'class':"ak-product-description__title"})
        if name ==[]:
            continue
        for item in name:
            dictionary['Наименование'] = item.text.strip()
#АРТИКУЛ
        art = soup.find_all('div',{'class':"code"})
        for item in art:
            dictionary['Артикул']=item.text.split()[1]
#ЦВЕТ
        colour = soup.find_all('li',{'class':"tooltipster"})
        for item in colour:
            dictionary['Цвет']=item['data-title']
#ЦЕНЫ
        price = soup.find_all('div',{'class':"costs relative"})
        price_mas=[]
        for item in price:
            price_mas=(item.text.replace("\n","").split('.'))
        if len(price_mas)>2:
            dictionary['Цена'] = price_mas[1]
            dictionary['Цена_со_скидкой'] = price_mas[0]
        else:
            dictionary['Цена'] = price_mas[0]
            dictionary['Цена_со_скидкой'] = '-'
#РАЗМЕРЫ
        size = soup.find_all('input',{'type':"radio"})
        size_mas=''
        for item in size:
            try:
                if item['disabled']=='disabled':
                    pass
            except KeyError:
                size_mas+=item['value']+' '
        dictionary['Размер'] = size_mas
#ОПИСАНИЕ И СОСТАВ
        desc = soup.find_all('div',{'class':"text"})[0]
        description = []
        for item in desc:
            description.append(item.text.split("\n"))
        dictionary['Состав']=description[1][1]
        dictionary['Описание']=description[1][2]
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
def parser4(n):
    print(n)
    now = datetime.datetime.now()
    link = "https://acoolakids.ru/vsya-odezhda-dlya-malchikov-8-14?tab=&sort_new=desc&limit=30&page=" + str(n+1)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
#ССЫЛКИ
    links = soup.find_all('a',{'class':"ak-card-product-min show"})
    links_mas = []
    for item in links:
        links_mas.append(item['href'])
#ССЫЛКИ НА КАРТИНКИ
    images = soup.find_all('div',{'class':"link"})
    images_mas = []
    for item in images:
        images_mas.append(item.find('img')['src'])
    k = 0
    for item in links_mas:
        dictionary = {}
#ПОЛ И ВОЗРАСТ
        dictionary['Товарная_группа1'] = 'Мальчики'
        dictionary['Товарная_группа2'] = 'От 8 до 14 лет'
        dictionary['Дата']=now.strftime("%d-%m-%Y")
#ССЫЛКИ
        link = item
        dictionary['Ссылка'] = link
        dictionary['Ссылка_картинка'] = images_mas[k]
        k+=1
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')  
#НАИМЕНОВАНИЕ
        name = soup.find_all('h2',{'class':"ak-product-description__title"})
        if name ==[]:
            continue
        for item in name:
            dictionary['Наименование'] = item.text.strip()
#АРТИКУЛ
        art = soup.find_all('div',{'class':"code"})
        for item in art:
            dictionary['Артикул']=item.text.split()[1]
#ЦВЕТ
        colour = soup.find_all('li',{'class':"tooltipster"})
        for item in colour:
            dictionary['Цвет']=item['data-title']
#ЦЕНЫ
        price = soup.find_all('div',{'class':"costs relative"})
        price_mas=[]
        for item in price:
            price_mas=(item.text.replace("\n","").split('.'))
        if len(price_mas)>2:
            dictionary['Цена'] = price_mas[1]
            dictionary['Цена_со_скидкой'] = price_mas[0]
        else:
            dictionary['Цена'] = price_mas[0]
            dictionary['Цена_со_скидкой'] = '-'
#РАЗМЕРЫ
        size = soup.find_all('input',{'type':"radio"})
        size_mas=''
        for item in size:
            try:
                if item['disabled']=='disabled':
                    pass
            except KeyError:
                size_mas+=item['value']+' '
        dictionary['Размер'] = size_mas
#ОПИСАНИЕ И СОСТАВ
        desc = soup.find_all('div',{'class':"text"})[0]
        description = []
        for item in desc:
            description.append(item.text.split("\n"))
        dictionary['Состав']=description[1][1]
        dictionary['Описание']=description[1][2]
#ГРУЗИМ В SQL
        if dictionary['Ссылка'] in ultradata[0] and (dictionary['Цена']!=ultradata[1][ultradata[0].index(dictionary['Ссылка'])] or dictionary['Цена_со_скидкой']!=ultradata[2][ultradata[0].index(dictionary['Ссылка'])]):
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)
        elif dictionary['Ссылка'] not in ultradata[0]:
            df = pd.DataFrame([dictionary], columns= ['Наименование','Цена','Цена_со_скидкой','Артикул','Состав','Цвет','Описание','Артикул','Описание','Товарная_группа1','Товарная_группа2','Размер','Ссылка','Ссылка_картинка', 'Дата'])
            df.to_sql('acoolakids', conn, if_exists='append', index = False)

