#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import importlib
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib3
import string
import pymysql

root_url = 'http://www.jokeji.cn/hot.asp?action=brow'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit\
        /537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'


def getmeichannel(url):
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': user_agent
    }
    http = urllib3.PoolManager()
    web_data = http.request('GET', url, headers=headers).data
    # soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    soup = BeautifulSoup(web_data, 'html5lib')
    channel = []
    tables = soup.findAll(height='30')
    for table in tables:
        try:
            for tr in table.findAll('tr'):
                channel.append(tr)
                pass
        except Exception as e:
            print('Error:', e)
            pass
    return channel


def getpages(url):
    print(url)
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': user_agent
    }
    http = urllib3.PoolManager()
    web_data = http.request('GET', url, headers=headers).data
    soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    print(web_data)
    span = soup.find(class_='main_title')
    tds = span.findAll('td')
    td = tds[len(tds)-2]
    pages = td.select('a')[0].get('href').replace('hot.asp?action=brow&me_page=', '')
    print(pages)
    return pages


def getdetail(url):
    url = quote(url, safe=string.printable)
    headers = {
        'User-Agent': user_agent
    }
    http = urllib3.PoolManager()
    r = http.request('GET', url, headers=headers)
    web_data = r.data
    soup = BeautifulSoup(web_data, 'html.parser', from_encoding='GBK')
    font = soup.find(attrs={'id': 'text110'})
    try:
        return font.get_text()
        pass
    except Exception as e:
        print(str(e))
        return ''
        pass


def requestpage(db1, url):
    channel_list = getmeichannel(url)
    list1 = []
    for tr in channel_list:
        dict1 = {}
        a = tr.find(class_='main_14')
        herf = 'http://www.jokeji.cn'+a.get('href')
        title = a.get_text()
        print(str(herf)+' --- '+str(title))
        date = tr.find(class_='date').get_text().replace('\r\n          ', '')
        detail = getdetail(herf)
        insetdb(db1=db1, herf=herf, title=title, date=date, detail=detail)
        list1.append(dict1)
    return list1


def spider(db1, url):
    i = 1
    pages = getpages(url)
    while i <= int(pages):
        pageurl = 'http://www.jokeji.cn/hot.asp?action=brow&me_page='+str(i)
        print(pageurl)
        requestpage(db1, pageurl)
        i = i+1
        pass
    else:
        print('大于页数')
        pass


def connectdb():
    db1 = pymysql.connect(
        host="localhost",
        user="root",
        passwd="666666",
        port=3306,
        db="joke")
    cursor = db1.cursor()
    cursor.execute("DROP TABLE IF EXISTS joke")
    sql = """CREATE TABLE joke (herf TEXT NOT NULL, title TEXT, date TEXT, detail TEXT)"""
    try:
        cursor.execute(sql)
        cursor.execute("""SET SQL_SAFE_UPDATES = 0;""")
        pass
    except Exception as e:
        print(str(e))
        pass
    return db1


def insetdb(db1, herf, title, date, detail):
    sql = "insert into joke(herf, title, date, detail) \
    values ('%s', '%s', '%s', '%s');" % \
       (herf, title, date, detail)
    try:
        cursor = db1.cursor()
        cursor.execute(sql)
        db1.commit()
        pass
    except Exception as e:
        print(str(e))
        db1.rollback()
        pass


if __name__ == "__main__":
    importlib.reload(sys)
    db2 = connectdb()
    spider(db2, root_url)
    db2.close()
