import os
import sys
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

class seleniumDriverWrapper():
    def __init__(self):
        self.__driver = None
        self.__wait = None

    def begin(self,webdriver):
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--start-maximized')
        options.set_capability('pageLoadStrategy', 'eager')
        user_agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        ]
        UA = user_agent[random.randrange(0, len(user_agent), 1)]
        options.add_argument('--user-agent=' + UA)
        self.__driver = webdriver.Chrome(options=options)
        self.__wait = WebDriverWait(driver=self.__driver, timeout=30)
        self.__driver.execute_script("window.open()")
        self.__driver.switch_to.window(self.__driver.window_handles[1])

    def getDriver(self):
        return self.__driver

    def getWait(self):
        self.__wait = WebDriverWait(driver=self.__driver, timeout=5)
        return self.__wait

    def getCustomWait(self,seconds):
        self.__wait = WebDriverWait(driver=self.__driver, timeout=seconds)
        return self.__wait

    def end(self):
        self.__driver.quit()

    def clickXPath(self,xpath):
        element = WebDriverWait(self.__driver, 10).until(lambda x: x.find_element(By.XPATH,xpath))
        #element = self.__driver.find_element(By.XPATH,xpath)
        element.click()

    def inputXPath(self,xpath,text):
        element = self.__driver.find_element(By.XPATH,xpath)
        element.send_keys(text)
