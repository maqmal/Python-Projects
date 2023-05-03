from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from lxml import html
import json
import asyncio
from pyppeteer import launch

username = "example-username"
password = "example-password"

def get_table_data():
    print("Initiating driver...")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(0)
    driver.set_window_size(364, 29800)
    # driver.maximize_window()

    print("Initiating login...")
    driver.get("https://example-website.com")
    time.sleep(2)
    driver.find_element(By.ID, "txtUsername").send_keys(username)
    driver.find_element(By.ID, "txtPassword").send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="btnLogin"]').click()

    time.sleep(10)
    print("Go to the allStock table...")

    element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="mainMenu1"]/div/div/div[1]'))
    WebDriverWait(driver, 60).until(element_present)

    driver.find_element(By.XPATH, '//*[@id="mainMenu1"]/div/div/div[1]').click()
    driver.find_element(By.XPATH, '//*[@id="subMenu1"]/div/div[2]').click()

    time.sleep(5)

    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")

    print("Crawling data...")
    # Find all the relevant data
    all_code_data = soup.find_all("div", attrs={"class": "ember-table-left-table-block"})[1]
    all_column_data = soup.find_all("div", attrs={"class": "ember-table-header-row"})[1]
    code_data = all_code_data.find_all("div", attrs={"class": "symbol-fore-color"})
    column_data = all_column_data.find_all("div", attrs={"class": "font-table-header"})

    column_array = [value.text.strip() for value in column_data if value.text != ""]
    code_array = [value.text.strip() for value in code_data if value.text != ""]

    full_column = ["Symbol"] + column_array
    full_column.remove('Cash Map')

    source = driver.page_source
    tree = html.fromstring(source)

    all_table_data = tree.cssselect("div.ember-table-tables-container")[0]
    stock_spans = all_table_data.cssselect("span")

    stock_array = [value.text.strip() for value in stock_spans if value.text is not None]

    stock_length = int(len(stock_array) / len(code_array))

    list_sub_lists = [stock_array[x:x + stock_length] for x in range(0, len(stock_array), stock_length)]

    list_of_dictionary = []
    list_sub_lists.pop()
    list_sub_lists.pop()

    list_of_dictionary = [{column_name: value for column_name, value in zip(full_column, [code_array[index]] + item)} for index, item in
                            enumerate(list_sub_lists) if code_array[index] != ""]
    
    driver.quit()

    df = pd.DataFrame(list_of_dictionary)
    list_of_dicts = df.T.to_dict().values()
    dicts_of_dicts = {}

    for temp_dict in list_of_dicts:
        dicts_of_dicts[temp_dict['Symbol']] = temp_dict

    return dicts_of_dicts


def extract_payload_data(data):
    try:
        payload_data = data['response']['payloadData']
        # Formatting the string
        payload_data = payload_data[payload_data.index('{'):]
        return json.loads(payload_data)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error extract payload data: {e}")
        return None

def run_websocket(dict_of_dict, dict_stock_stock_data_pair_manager):
    print("Dataframe created. Continue to websocket...")

    async def main():
        browser = await launch(
            headless=False,
            autoClose=False,
            executablePath='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        )
        page = await browser.newPage()
        await page.goto('https://example-website.com')
        time.sleep(5)
        await page.waitForSelector('#txtUsername')
        await page.type('#txtUsername', username)
        await page.type('#txtPassword', password)

        await page.click("#btnLogin")

        time.sleep(5)
        cdp = await page.target.createCDPSession()
        await cdp.send('Network.enable')
        await cdp.send('Page.enable')

        event = asyncio.Event()

        def responseHandler(response):
            data = extract_payload_data(response)
            column_map = {
                'ltp': 'Last Traded',
                'ltq': 'Last Qty',
                'nChg': 'Chg',
                'bbq': 'Bid Lots',
                'bbp': 'Bid',
                'bap': 'Offer',
                'baq': 'Offer Lots',
                'vol': 'Lots',
                'tovr': 'Value',
                'trades': 'Frequency',
                'high': 'High',
                'low': 'Low',
                'open': 'Open',
            }

            if 'sym' in data:
                symbol = data['sym']
                if symbol in dict_of_dict:
                    for key, value in column_map.items():
                        if key in data:
                            dict_of_dict[symbol][value] = data[key]
                            dict_stock_stock_data_pair_manager['stock'] = dict_of_dict

            event.set()

        while True:
            cdp.on('Network.webSocketFrameReceived', responseHandler)
            await page.click("#menuWrapper2")
            await event.wait()
            event.clear()

    asyncio.get_event_loop().run_until_complete(main())