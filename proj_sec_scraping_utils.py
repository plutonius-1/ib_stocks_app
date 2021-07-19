import time
import cfg
from selenium import webdriver
import re
from cfg import *
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

### LOCAL CONSTS ###
XML_INDUTRY_INFO_PATH = "./peerInfo/IndustryInfo"
SIC_KEY = "sic"
CODE_KEY = "code"

SEC_SEARCH_ACTIVE_COMPS_URL = "https://www.sec.gov/cgi-bin/srch-edgar?text=ASSIGNED-SIC%3D{}%20and%20FORM-TYPE%3D10-Q&start={}&count=80&first=2020&last=2021"
SEC_BASE_ADDR = "https://www.sec.gov/"
SEC_SEARCH_BY_CIK_URL = "https://www.sec.gov/Archives/edgar/data/{}"

def get_companys_sic(cik : str):
    url = SEC_SEARCH_BY_CIK_URL.format(cik) + "/"
    r = requests.get(url)
    patt = re.compile(r'SIC=\d+')
    assert r.ok
    soup = BeautifulSoup(r.content, "lxml")
    dir_links = [i.attrs['href'] for i in soup.find_all("a") if 'href' in i.attrs and "Archives/edgar/data" in i.attrs['href']]
    for link in dir_links:
        try:
            url = SEC_BASE_ADDR + link
            dir_page = requests.get(url)
            soup = BeautifulSoup(dir_page.content, "lxml")
            div  = soup.find_all("div",)
            html_links = [i.attrs['href'] for i in soup.find_all("a") if 'href' in i.attrs and "Archives/edgar/data" in i.attrs['href']]

            for l in html_links:
                url = SEC_BASE_ADDR + link
                comp_page = r.get(url)
                soup = BeautifulSoup(comp_page.content, "lxml")
                comp_page_links = soup.find_all("a")
                for page_link in comp_page_links:
                    res = patt.search(page_link.attrs['href'])
                    if (res):
                        name = res.group(0).split("=")[1]
                        if (name != None):
                            return name
        except:
            continue

    return None

def get_companies_by_sic(sic_code):

    def verify_page_available(browser, url):
        tries = 3
        ok = False

        while tries >= 0 and ok is False:
            browser.get(url)
            time.sleep(4)
            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            if ("unavailable" not in soup.text.lower()):
                ok = True
            else:
                soup = None
            tries -= 1

        return soup

    def filter_sec_sic_search(df):
        # if df.empty == False:
            # tags = "".join([str(i) for i in df.columns])
            # tags = tags.lower()
        df = df.get_text()
        if ("company" in df.lower() and "filing date" in df.lower()):
            return True
        return False

    sics_tickers = []

    # go to first SEC SIC page (start 0)
    start = 1
    companies_by_sic_req = requests.get(SEC_SEARCH_ACTIVE_COMPS_URL.format(str(sic_code), str(start)))
    try:
        browser = webdriver.Firefox(executable_path = r"/mnt/c/Users/avsha/Documents/geckodriver.exe")
    except:
        browser = webdriver.Firefox()

    visited_companies = []

    while (companies_by_sic_req.ok and "table" in companies_by_sic_req.text):
        # get all links to SEC companies filings
        links = []

        # browser.get(SEC_SEARCH_ACTIVE_COMPS_URL.format(str(sic_code), str(start)))
        # time.sleep(4)
        # html = browser.page_source

        # soup = BeautifulSoup(companies_by_sic_req.text, "lxml")
        # soup = BeautifulSoup(html, 'lxml')
        soup = verify_page_available(browser, SEC_SEARCH_ACTIVE_COMPS_URL.format(str(sic_code), str(start)))
        table = soup.find_all('table')

        filt = list(filter(filter_sec_sic_search, table))

        if (len(filt) == 1):
            trs = filt[0].findAll("tr")
            if (len(trs) == 1):
                break

            for i in trs:
                try:
                    comp_name = i.text.split("\n")[2]
                    if (comp_name in visited_companies):
                        continue
                    else:

                        link = i.find('a')['href']
                        comp_soup = verify_page_available(browser ,SEC_BASE_ADDR + link)

                        # verify
                        cik_link = None
                        # try:
                        cik_link = [i.attrs['href'] for i in comp_soup.findAll('a') if 'see all' in i.text][0]
                        # except:
                            # pass

                        if (cik_link != None):
                            visited_companies.append(comp_name)
                            soup = verify_page_available(browser, SEC_BASE_ADDR + cik_link)
                            a = soup.find('span',{"id":"ticker"})
                            #####
                            exchanges = a.text.split(",")
                            for e in exchanges:
                                if ("null" not in e):
                                    ticker = e.split()[0]
                            ####
                            # ticker = a.text.split()[0]
                                    sics_tickers.append(ticker)
                            # verificatio - delete
                            name = soup.find('span', {"id" : "name"})
                            # print(name.text)

                except:
                    pass

        # Go to next page and get more tickers
        else:
            break
        start += 80
        companies_by_sic_req = requests.get(SEC_SEARCH_ACTIVE_COMPS_URL.format(str(sic_code), str(start)))

    # close browser
    browser.quit()

    # remove ticker copies
    res = []
    sics_ticker = sics_tickers.sort()
    temp_ticker = None
    for ticker in sics_tickers:
        if ticker != temp_ticker:
            res.append(ticker)

        temp_ticker = ticker

    return res
# print(get_companies_by_sic(3841))


def get_company_sic(ticker : str):
    """
    @ param ticker - the ticker of the comapny we want to find the SIC for
    returns the sic as int
    """
    CIK_URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    SIC_RE = re.compile(r'SIC=\d+')
    # CIK    = self.get_company_cik(ticker)
    URL = CIK_URL.format(ticker)
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"}
    r = requests.get(URL, headers = headers)
    if not r.ok:
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"}
        r = requests.get(URL, headers = headers)
    assert r.ok
    results = SIC_RE.search(r.text)

    # assert len(results) >0, "MarketReasercher - Did not find the SIC for {}".format(ticker)
    # SIC = results[0].split()[1]
    try:
        SIC = results.group(0).split("=")[1]
    except:
        SIC = None
    return SIC
