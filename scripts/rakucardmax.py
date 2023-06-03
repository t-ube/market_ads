from bs4 import BeautifulSoup
import requests
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

class rakucardmaxListParser():
    def __init__(self, _html):
        self.__html = _html

    def getItemList(self):
        soup = BeautifulSoup(self.__html, 'html.parser')
        l = list()
        print(soup)
        for item in soup.find_all('td', {'style': 'padding:0px 5px 0px 10px;'}):
            product = {}
            title = item.find('a', class_='category_itemnamelink').text.strip()
            print(title)
            master_id = self.generateMasterId(title)
            link = item.find('a', class_='category_itemnamelink')['href']
            pid = self.generatePid(link)
            if master_id != None and pid != None:
                product['master_id'] = master_id
                title = title.replace('ポケモンカード','')
                product['market'] = 'rakucardmax'
                product['link'] = self.generateLink(pid)
                product['price'] = int(item.find('span', class_='category_itemprice').text.strip().replace('円', '').replace(',', ''))
                product['name'] = '{:.10}'.format(title)
                product['date'] = None
                product['datetime'] = None
                product['stock'] = 1
                l.append(product)
        return l

    def generateMasterId(self,title):
        pattern = r'^(\w+).*?\(\w+\).*?\((\d+/\d+)\)'
        match = re.search(pattern,title)
        if match:
            set_code = match.group(1)
            card_number = match.group(2)
            master_id = f"{set_code}_{card_number}"
            master_id = master_id.replace('/','_')
            return master_id.lower()
        else:
            return None

    def generatePid(self,url):
        pattern = r"/cardmax/(.+)/"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            return None

    def generateLink(self,pid):
        link = 'https://hb.afl.rakuten.co.jp/ichiba/32ae7b95.cbbcd87b.32ae7b96.843343cd/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fcardmax%2F'
        link += pid
        link += '%2F&link_type=hybrid_url&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJoeWJyaWRfdXJsIiwic2l6ZSI6IjI0MHgyNDAiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9'
        return link

class rakucardmaxSearchCsv():
    def __init__(self,_out_dir):
        dt = jst.now().replace(microsecond=0)
        self.__out_dir = _out_dir
        self.__list = list()
        self.__date = str(dt.date())
        self.__datetime = str(dt)
        self.__file = _out_dir+'/'+self.__datetime.replace("-","_").replace(":","_").replace(" ","_")+'_rakucardmax.csv'

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

class rakucardmaxCsvBot():
    def download(self, drvWrapper, out_dir):
        # カード一覧へ移動
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        searchCsv = rakucardmaxSearchCsv(out_dir)
        for page in range(5):
            url = self.getUrl(page)
            if url != None:
                time.sleep(10)
                print(url)
                self.getResultPageNormal(drvWrapper.getDriver(), url)
                try:
                    drvWrapper.getCustomWait(10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'risfAllPages')))
                    listHtml = drvWrapper.getDriver().page_source.encode('utf-8')
                    parser = rakucardmaxListParser(listHtml)
                    l = parser.getItemList()
                    for item in l:
                        searchCsv.add(item)
                        print(item)
                except TimeoutException as e:
                    print("TimeoutException")
                except Exception as e:
                    print(traceback.format_exc())
        searchCsv.save()

    def getUrl(self, page: int):
        if page < 2:
            keyword = ""
            if page == 0: keyword = '0000001142'# 強化拡張パック
            if page == 1: keyword = '0000001249'# ハイクラスパック
            return 'https://item.rakuten.co.jp/cardmax/c/'+keyword+'/?s=3&i=1#risFil'
        else:
            keyword = ""
            p = ""
            if page >= 2 and page <= 4:
                keyword = '0000001125'# 拡張パック
                if page == 2: p = '1'
                if page == 3: p = '2'
                if page == 4: p = '3'
                return 'https://item.rakuten.co.jp/cardmax/c/'+keyword+'/?p='+p+'&s=3&i=1#risFil'
        return None
        
    def getResultPageNormal(self, driver, url):
        print(url)
        try:
            driver.get(url)
        except WebDriverException as e:
            print("WebDriverException")
        except Exception as e:
            print(traceback.format_exc())

class rakucardmaxCsvBotV2():
    def download(self, out_dir):
        # カード一覧へ移動
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        searchCsv = rakucardmaxSearchCsv(out_dir)
        for page in range(1):
            url = self.getUrl(page)
            if url != None:
                time.sleep(10)
                print(url)
                try:
                    response = requests.get(url, timeout=20)
                    response.raise_for_status()
                    html = response.content
                    parser = rakucardmaxListParser(html)
                    l = parser.getItemList()
                    for item in l:
                        searchCsv.add(item)
                        print(item)
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 503:
                        print("503エラー：サービスが利用できません")
                    else:
                        print("HTTPエラーが発生しました:", str(e))
                except requests.exceptions.Timeout:
                    print("タイムアウトエラー：リクエストがタイムアウトしました")
                except requests.exceptions.RequestException as e:
                    print("その他のリクエストエラーが発生しました:", str(e))
        searchCsv.save()

    def getUrl(self, page: int):
        if page < 2:
            keyword = ""
            if page == 0: keyword = '0000001142'# 強化拡張パック
            if page == 1: keyword = '0000001249'# ハイクラスパック
            return 'https://item.rakuten.co.jp/cardmax/c/'+keyword+'/?s=3&i=1#risFil'
        else:
            keyword = ""
            p = ""
            if page >= 2 and page <= 4:
                keyword = '0000001125'# 拡張パック
                if page == 2: p = '1'
                if page == 3: p = '2'
                if page == 4: p = '3'
                return 'https://item.rakuten.co.jp/cardmax/c/'+keyword+'/?p='+p+'&s=3&i=1#risFil'
        return None

