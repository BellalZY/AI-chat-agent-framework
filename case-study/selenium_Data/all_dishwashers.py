
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


base_url = "https://www.partselect.com"

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

chrome_options.page_load_strategy = 'eager'

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

def get_sub_links(model_links, wait):
    try:
        wait = WebDriverWait(driver, 60)
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'nf__links'))
        )
        ul = driver.find_elements(By.CLASS_NAME, "nf__links")
        lis = ul[2].find_elements(By.TAG_NAME, "li")
        print(f"Found {len(lis)} model links")
        for li in lis:
            a = li.find_element(By.TAG_NAME, "a")
            href = a.get_attribute("href")
            model_links.append(href)

    except Exception as e:
        print(f"could not find links: {e}")

def test_print(url):
    print(url)

def get_product(url, max_retries=5, backoff_factor=1.5):
    retry_count = 0
    newdriver = None
    while retry_count < max_retries:
        try:
            print(url)
            product_data = [] 
            newdriver = webdriver.Chrome(service=service, options=chrome_options)
            newdriver.get(url)
            time.sleep(6)

            WebDriverWait(newdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "title-main")))

            model = newdriver.find_elements(By.CLASS_NAME, "title-main")[0].text
            model_parts = newdriver.find_element(By.CLASS_NAME, "align-items-stretch")
            product_details = model_parts.find_elements(By.CLASS_NAME, "mega-m__part")

            for product in product_details:
                try:
                # Title & URL
                    title_elem = product.find_element(By.CLASS_NAME, "mega-m__part__name")
                    title = title_elem.text.strip()
                    newurl = product.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    title = ""
                    newurl = ""
                    print("no title")

                # Rating from style="width: 87%"
                try:
                    star_div = product.find_element(By.CLASS_NAME, "rating__stars__upper")
                    style = star_div.get_attribute("style")  # e.g., "width: 76%;"
                    width_percent = float(style.strip().split(":")[1].replace("%", "").replace(";", ""))
                    rating = round(width_percent / 20, 1)
                except e:
                    rating = ""
                    print("no rating:" + str(e))

                # PartSelect #
                partselect_elem = product.find_element(By.XPATH, ".//span[text()='PartSelect #:']/..")
                partselect_number = partselect_elem.text.replace("PartSelect #:", "").strip()

                # Manufacturer #
                manufacturer_elem = product.find_element(By.XPATH, ".//span[text()='Manufacturer #:']/..")
                manufacturer_number = manufacturer_elem.text.replace("Manufacturer #:", "").strip()

                try:
                    wrapper_div = product.find_element(By.CSS_SELECTOR, ".d-flex.flex-col.justify-content-between > div")
                    description = wrapper_div.text.strip().split("\n")
                except:
                    description = ""
                    print("no desc")

                # Price
                try:
                    price_elem = product.find_element(By.CLASS_NAME, "mega-m__part__price")
                    price = price_elem.text.strip()
                except:
                    price = ""
                    print("no price")

                part_info = {
                    "model": model,
                    "title": title,
                    "url": "https://www.partselect.com" + str(newurl) if newurl else "",
                    "rating": rating,
                    "partselect_number": partselect_number,
                    "manufacturer_number": manufacturer_number,
                    "price": price,
                    "description": description
                }

                product_data.append(part_info)

            newdriver.quit()
            return product_data

        except Exception as e:
            if newdriver:
                newdriver.quit()
            print(f"Error fetching {url}: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = backoff_factor ** retry_count + random.uniform(0, 1) + 20
                print(f"Retrying {url} in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Max retries reached for {url}. Skipping.")
                return None
        finally:
            if newdriver:
                newdriver.quit()


def save_file(product_data, name):
    with open(name +'.json', 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=4)


def main():

    driver.get('https://www.partselect.com/Dishwasher-Parts.htm')
    # print(driver.page_source)
    model_links = []
    get_sub_links(model_links, driver)
    print(f"[INFO] Found {len(model_links)} model__links ")
    save_file(model_links, "model_links")
    driver.quit()

    product_data = []
    with open('model_links.json', 'r') as file:
        data = json.load(file)

    try:
        with ThreadPoolExecutor(max_workers = 5) as executor:
            futures = [executor.submit(get_product, url) for url in data]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    product_data.extend(result)
        save_file(product_data, "product_data")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()