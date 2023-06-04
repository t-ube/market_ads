from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import csv
import os
import datetime
import re
from . import jst
from . import seleniumDriverWrapper as wrap
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import traceback
import time

class amzWatchListCSVLoader():
    def getList(self,file_path:str):
        l = list()
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                l.append(row)
        return l

class amzListParser():
    def __init__(self, _html):
        self.__html = _html

    def getItemList(self, master_id:str, link:str):
        soup = BeautifulSoup(self.__html, 'html.parser')
        l = list()
        product = {}
        product_title_element = soup.find('span', id='productTitle')
        availability_element = soup.find('span', class_='a-size-base a-color-price a-text-bold')
        if product_title_element != None and availability_element != None:
            title = product_title_element.get_text(strip=True)
            stock = availability_element.get_text(strip=True)
            price = soup.find('span', class_='a-offscreen').text.strip()
            if price != None:
                print(title)
                print(price)
                product['master_id'] = master_id
                title = title.replace('ポケモンカードゲーム','')
                title = title.replace('ポケモンカード','')
                title = title.replace('【','')
                title = title.replace('】','')
                title = title.replace(' ','')
                product['market'] = 'amazon'
                product['link'] = link
                product['price'] = int(price.replace('円', '').replace('￥', '').replace(',', ''))
                product['name'] = '{:.10}'.format(title)
                product['date'] = None
                product['datetime'] = None
                product['stock'] = int(self.getStock(stock.replace(',', '')))
                l.append(product)
        return l

    def getStock(self,url):
        pattern = r"([0-9]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            return 1

class amzSearchCsv():
    def __init__(self,_out_dir):
        dt = jst.now().replace(microsecond=0)
        self.__out_dir = _out_dir
        self.__list = list()
        self.__date = str(dt.date())
        self.__datetime = str(dt)
        self.__file = _out_dir+'/'+self.__datetime.replace("-","_").replace(":","_").replace(" ","_")+'_amz.csv'

    def init(self):
        labels = [
         'master_id',
         'market',
         'link',
         'price',
         'name', 
         #'image',
         'date',
         'datetime',
         'stock'
         ]
        try:
            with open(self.__file, 'w', newline="", encoding="utf_8_sig") as f:
                writer = csv.DictWriter(f, fieldnames=labels)
                writer.writeheader()
                f.close()
        except IOError:
            print("I/O error")

    def add(self, data):
        data['date'] = str(self.__date)
        data['datetime'] = str(self.__datetime)
        self.__list.append(data)
        
    def save(self):
        if len(self.__list) == 0:
            return
        df = pd.DataFrame.from_dict(self.__list)
        if os.path.isfile(self.__file) == False:
            self.init()
        df.to_csv(self.__file, index=False, encoding='utf_8_sig')

class amzCsvBot():
    def download(self, drvWrapper, out_dir, master_id, url, aff):
        # カード一覧へ移動
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        searchCsv = amzSearchCsv(out_dir)
        if url != None:
            time.sleep(10)
            self.getResultPageNormal(drvWrapper.getDriver(), url)
            try:
                drvWrapper.getWait().until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'navFooterBackToTopText')))
                listHtml = drvWrapper.getDriver().page_source.encode('utf-8')
                parser = amzListParser(listHtml)
                l = parser.getItemList(master_id,aff)
                for item in l:
                    searchCsv.add(item)
                    print(item)
            except TimeoutException as e:
                print("TimeoutException")
            except Exception as e:
                print(traceback.format_exc())
        searchCsv.save()
        
    def getResultPageNormal(self, driver, url):
        print(url)
        try:
            driver.get(url)
        except WebDriverException as e:
            print("WebDriverException")
        except Exception as e:
            print(traceback.format_exc())
