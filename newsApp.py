# _*_ coding: utf-8 _*_

from selenium import webdriver
import requests
import urllib.request
from lxml import etree
from time import sleep
import time
import os
import numpy as np
import pandas as pd
from selenium.webdriver.chrome.options import Options

# 访问主页面
def request_main(url, headers):
    response = requests.get(url=url, headers=headers)
    response.encoding = "utf-8"
    content = response.text
    # print(content)
    # sleep(100)
    tree = etree.HTML(content)
    url_div = tree.xpath('//div[@class="bd"]/div/ul/li/a')
    # alist = [0, 1, 2, 3, 4, 5, 6]
    # alist = [2, 3, 5, 6]
    alist = [6]
    modules_urls = []
    for index in alist:
        module_url = url_div[index].xpath('./@href')[0]
        modules_urls.append(module_url)
    return modules_urls

# 访问模块，数据动态加载

def request_module(path, url_list):
    # options = Options()
    # options.add_argument("--headless")
    browser = webdriver.Chrome(path)
    title_list = []
    detail_url_list = []
    hits_list = []
    hits_url_list = []
    for url in url_list:
        browser.get(url)
        sleep(2)
        js_bottom = 'document.documentElement.scrollTop=200000'
        browser.execute_script(js_bottom)
        sleep(3)
        browser.execute_script(js_bottom)
        sleep(3)
        browser.execute_script(js_bottom)
        sleep(3)
        page_text = browser.page_source
        module_tree = etree.HTML(page_text)
        title_list += module_tree.xpath('/html/body/div/div[3]/div[4]/div[1]/div[1]/div/ul/li/div/div/div/div[1]/h3/a/text()')

        detail_url_list += module_tree.xpath('/html/body/div/div[3]/div[4]/div[1]/div[1]/div/ul/li/div/div/div/div[1]/h3/a/@href')

        # hits_list += module_tree.xpath('//div[@class="ndi_main"]//div[@class="na_detail clearfix "]/div[3]/a/div/span[1]/text()')
        hits_list += module_tree.xpath('//span[@class="post_recommend_tie_text"]/text()')
        # hits_url_list += module_tree.xpath('//div[@class="ndi_main"]//div[@class="na_detail clearfix "]/div[3]/a/@href')
        hits_url_list += module_tree.xpath('/html/body/div/div[3]/div[4]/div[1]/div[1]/div/ul/li/div/div[1]/div/div[3]/a/@href')
    browser.quit()
    return title_list, detail_url_list, hits_list, hits_url_list
# 解析文章的详情页
def request_detail(detail_url_list, headers):
    # 让url集和中的数据全部变力访问，获取其中的点击，评论，时间
    time_list = []
    public_list = []
    for url in detail_url_list:
        detail_response = requests.get(url=url, headers=headers)
        detail_response.encoding = "utf-8"
        content = detail_response.text
        tree = etree.HTML(content)
        timeArray = tree.xpath('//div[@class="post_info"]/text()')
        timeArray = ''.join(timeArray).replace('\n', '').strip()[0:19]
        # article_source = ''
        source = tree.xpath('//div[@class="post_info"]/a[1]/text()')
        source = ''.join(source).replace('\n', '').strip()
        time_list.append(timeArray)
        public_list.append(source)
    return time_list, public_list

# 封装
def format_data(title, time, pulish, hits):
    data_list = []
    for index in range(len(title)):
        data_dic = {}
        data_dic["title"] = title[index]
        data_dic["time"] = time[index]
        data_dic["pulish"] = pulish[index]
        data_dic["hits"] = hits[index]
        data_list.append(data_dic)
    return data_list

def save(data, path='./download/'):
    folder = os.path.exists(path)
    if not folder:
        os.mkdir(path)
    time_path = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    data.to_excel(path + 'article' + time_path + '.xlsx', index=False)
def format_pd(data):
    data_dic = {}
    for key in data[0]:
        value_list = []
        for index in range(len(data)):
            value_list.append(data[index][key])
        data_dic[key] = value_list

    dataSourceDF = pd.DataFrame(data_dic)
    return dataSourceDF
if __name__ == '__main__':
    url = 'https://news.163.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'
       }
    path = './chromedriver.exe'

    print("----------进入首页----------")
    urls = request_main(url, headers)
    print("----------获取模块URL----------")

    # 访问模块
    print("----------进入个模块详情网页----------")
    # for m_url in urls:
    title_list, detail_url_list, hits_list, hits_url_list = request_module(path, urls)
    print("----------获取模块详情页新闻完毕----------")
    # 访问详情
    print("----------进入新闻详情页----------")
    time_list, public_list = request_detail(detail_url_list, headers)
    print("----------获取新闻发布时间和来源完毕----------")

    print("----------正在封装数据----------")
    data = format_data(title_list, time_list, public_list, hits_list)
    print("----------数据封装完毕----------")
    dataSourceDF = format_pd(data)
    print(dataSourceDF.head(5))

    # dataSourceDF.to_excel('./download/article.xlsx', index= False)
    print("----------正在保存数据----------")
    save(data=dataSourceDF)
    print("----------数据保存完毕----------")
    # df = pd.DataFrame(data)
    # df.head()