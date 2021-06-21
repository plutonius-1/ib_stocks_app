import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import time

url = "https://www.sec.gov/edgar/browse/?CIK=0001275187"
browser = webdriver.Firefox()
browser.get(url)
time.sleep(3)

html = browser.page_source
soup = BeautifulSoup(html, 'lxml')
a = soup.find('span',{"id":"ticker"})
print(a.text)
