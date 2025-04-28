from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

chrome_options.page_load_strategy = 'normal'

service = Service(ChromeDriverManager().install())


def get_sub_links(driver, product_elements, wait):
    try:
        wait = WebDriverWait(driver, 50)
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'products-list'))
        )
        print("Find sublinks!")
        ul = driver.find_element(By.CLASS_NAME, "products-list")
        links = ul.find_elements(By.TAG_NAME, "a")
        for a in links:
            href = a.get_attribute("href")
            title = a.find_element(By.TAG_NAME, "span").text
            if title == "Dishwasher" or title == "Refrigerator":
                product_elements.append(href)

    except Exception as e:
        print(f"could not find links: {e}")

def test_print(url):
    print(url)

def get_repair(url, repair_list):
    driver = None
    try:
        print(url)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        title = driver.find_element(By.CLASS_NAME, "title-main").text
        symptom_list = driver.find_element(By.CLASS_NAME, "symptom-list")
        section =  symptom_list.find_elements(By.TAG_NAME, "h2")
        desc = symptom_list.find_elements(By.CLASS_NAME, "symptom-list__desc")
        for i in range(len(section)):
            part_info = {
                "title": title, 
                "sympton-title": section[i].text, 
                "description": desc[i].find_elements(By.TAG_NAME, "p")[0].text,
            }
            repair_list.append(part_info)
        driver.quit()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        if driver:
            driver.quit()

def save_file(product_data):
    with open('repair.json', 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=4)


def main():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://www.partselect.com/Repair')
    # print(driver.page_source)
    sub_links = []
    get_sub_links(driver, sub_links,  driver)
    print(f"[INFO] Found {len(sub_links)} sub__links ")
    driver.quit()

    sub_sub_links = []
    repair_list = []
    for url in sub_links:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        ul = driver.find_element(By.CLASS_NAME, "symptom-list")
        links = ul.find_elements(By.TAG_NAME, "a")
        for a in links:
            href = a.get_attribute("href")
            sub_sub_links.append(href)
        driver.quit()
    count = 0
    for url in sub_sub_links:
        # count += 1
        # if count > 3:
        #     break
        get_repair(url, repair_list)

    save_file(repair_list)


if __name__ == "__main__":
    main()
