from undetected_chromedriver import Chrome as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from typing import List
from time import sleep
import random
import json
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

class Portatile:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

def scrapingPortatiles():
    # Initialize the Chrome driver
    driver = uc(options=options)
    try:
        # Visit the PC Componentes website
        driver.get("https://www.pccomponentes.com/search/?query=portatiles&or-relevance")

        print('entra nel timer')
        # Wait for the portatiles elements to load
        portatiles_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card"))
        )
        print('esce dal timer')

        # Extract the portatiles data
        portatiles = []

        for element in portatiles_elements:
            try:
                # Find name within each product card
                name_element = element.find_element(By.CSS_SELECTOR, ".product-card__title")
                name = name_element.text.strip()

                # Find price within each product card
                try:
                    # Attempt to find the price with the first CSS selector
                    price_element = element.find_element(By.CSS_SELECTOR, ".sc-cPyLVi.eFAgpZ")
                except:
                    # If first selector fails, try with the alternative selector
                    price_element = element.find_element(By.CSS_SELECTOR, ".sc-jJcwTH.euGkfE")

                # Extract text value of the price
                price_text = price_element.text.strip().replace("€", "").replace(".", "").replace(",", ".")
                price = float(price_text)

                # Create Portatile object and add to list
                new_portatile = Portatile(name, price)
                portatiles.append(new_portatile)

                print(f"Name: {name}, Price: {price}")

            except Exception as e:
                print(f"Error processing element: {e}")

            # Add random sleep to mimic human behavior
            sleep(random.uniform(1, 3))

        # Save the data as a JSON file
        with open('portatiles.json', 'w', encoding='utf-8') as f:
            json.dump({"portatiles": [{"name": p.name, "price": p.price} for p in portatiles]}, f, ensure_ascii=False, indent=4)

        return {
            "portatiles": [{"name": p.name, "price": p.price} for p in portatiles]
        }
    finally:
        # Close the driver
        driver.quit()

# Initiate the web scraping task
scrapingPortatiles()
