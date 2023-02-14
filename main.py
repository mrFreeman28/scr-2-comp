
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, parse_qs
import time

def today_str():
    import datetime

    today_timestamp = datetime.datetime.today()
    return "%d.%d.%d %d-%d-%d" % (
        today_timestamp.year,
        today_timestamp.month,
        today_timestamp.day,
        today_timestamp.hour,
        today_timestamp.minute,
        today_timestamp.second
    )

# chrome_driver = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
chrome_driver = './chromedriver'
driver = webdriver.Chrome(service=Service(chrome_driver))

URL = "https://www.linkedin.com/"
driver.get(URL)

print("Login in LinkedIn, search for the people and press enter to start...")
string = str(input())

base_url = driver.current_url
base_parsed_url = urlparse(base_url)
total_entries_count = 0
f = open(today_str() + '.csv', 'w', encoding="utf-8")
f.writelines('URL;Name;Title;Location\n')

while True:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    entries = soup.find_all("li", class_="reusable-search__result-container")
    if not entries:
        break 
    total_entries_count += len(entries)
    for entry in entries:
        try:
            name_element = entry.findAll("span", {"class": "entity-result__title-text"})
            entry_url = name_element[0].findAll("a", {"class": "app-aware-link"})[0]['href']

            name_text_element = name_element[0].findAll("span", {"dir": "ltr"})
            if not name_text_element:
                # entry_name = name_element[0].getText().strip()
                total_entries_count -= 1
                continue
            else:
                entry_name = name_text_element[0].findAll("span")[0].getText()

            entry_subtitle = entry.findAll("div", {"class": "entity-result__primary-subtitle"})[0].getText().strip()
            entry_location = entry.findAll("div", {"class": "entity-result__secondary-subtitle"})[0].getText().strip()

            # print(entry_url + '   ' + entry_name + '   ' + entry_subtitle + '   ' + entry_location)
            entry_url = entry_url.replace(';', ',')
            entry_name = entry_name.replace(';', ',')
            entry_subtitle = entry_subtitle.replace(';', ',')
            entry_location = entry_location.replace(';', ',')
            f.writelines(entry_url + ';' + entry_name + ';' + entry_subtitle + ';' + entry_location + '\n')
        except Exception as e:
            print(e)
            continue

    f.flush()

    current_url = driver.current_url
    up = urlparse(current_url)
    url_params = parse_qs(up.query)
    if 'page' not in url_params:
        current_page = 1
    else:
        current_page = int(url_params['page'][0])
    current_page += 1
    new_up = base_parsed_url._replace(query=(base_parsed_url.query + '&page=' + str(current_page)))
    driver.get(new_up.geturl())
    time.sleep(5)

f.close()
driver.close()
print("Total entries: ", total_entries_count)

import signal
import sys
 
def signal_term_handler(signal, frame):
    f.close()
    driver.close()
    sys.exit(0)
 
signal.signal(signal.SIGTERM, signal_term_handler)