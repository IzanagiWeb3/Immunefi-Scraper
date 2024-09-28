import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get('https://immunefi.com/bug-bounty/')

time.sleep(2)

last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

results = []
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

for a in soup.findAll(attrs={'class': 'line-clamp-2'}):
    if a.get('data-testid') == 'ProjectNameCell_name':
        name = a.text.strip()
        if name not in results:
            results.append(name)

df = pd.DataFrame({'Names': results})
df.to_csv('names.csv', index=False)
