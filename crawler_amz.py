import os
import glob
import pandas as pd
import time
from get_chrome_driver import GetChromeDriver
from selenium import webdriver
import pandas as pd
from pathlib import Path
from supabase import create_client, Client 
from scripts import seleniumDriverWrapper as wrap
from scripts import amz
from scripts import marcketCalc
from scripts import supabaseUtil
import csv


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, key)
supabase.postgrest.auth(service_key)

get_driver = GetChromeDriver()
get_driver.install()

amzBot = amz.amzCsvBot()
loader = marcketCalc.rawLoader()

writer = supabaseUtil.batchWriter()
editor = supabaseUtil.batchEditor()

dataDir = './data'
amzLoader = amz.amzWatchListCSVLoader()
amzList = amzLoader.getList('./amz.csv')

for row in amzList:
    wrapper = wrap.seleniumDriverWrapper()
    wrapper.begin(webdriver)
    amzBot.download(wrapper, dataDir, row['master_id'], row['url'], row['aff'])
    wrapper.end()

batch_items = []
df = loader.getUniqueRecodes(dataDir)
records = df.to_dict(orient='records')
batch_items = editor.getAffiliateItem(records)
writer.write(supabase, "affiliate_item", batch_items)
