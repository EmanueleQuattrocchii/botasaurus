from undetected_chromedriver import Chrome as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import random
import json
import re
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

def accept_cookies(driver):
    try:
        # Wait until the accept cookies button is clickable
        cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "cookiesAcceptAll"))
        )
        cookies_button.click()
        print("Clicked on 'Aceptar todas' button to accept cookies.")
    except Exception as e:
        print(f"Error accepting cookies: {e}")

def get_total_pages(driver):
    try:
        # Wait until the pagination span element is visible
        pagination_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.sc-deXhhX.tsXxX"))
        )
        # Get the text from the pagination element
        pagination_text = pagination_span.text.strip()
        # Use regex to extract the total number of pages
        match = re.search(r'Página \d+ de (\d+)', pagination_text)
        if match:
            total_pages = int(match.group(1))
            print(f"Total pages found: {total_pages}")
            return total_pages
        else:
            print("Failed to extract total pages.")
            return None
    except Exception as e:
        print(f"Error getting total pages: {e}")
        return None

def click_next_page(driver):
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Página siguiente']"))
        )
        next_page_button.click()
        print("Clicked on next page button")
        return True
    except Exception as e:
        print(f"Error clicking next page button: {e}")
        return False

def scraping_portatiles():
    # Initialize the Chrome driver
    driver = uc(options=options)
    try:
        # Visit the PC Componentes website
        driver.get("https://www.pccomponentes.com/search/?query=portatiles&or-relevance")

        # Accept cookies if the popup appears
        accept_cookies(driver)

        # Get total number of pages
        total_pages = get_total_pages(driver)
        if total_pages is None:
            return
        
        # Wait for the portatiles elements to load
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card")))

        # Extract the portatiles data
        portatiles = []

        # Define the maximum number of pages to scrape
        max_pages = total_pages
        page_count = 0

        while page_count < max_pages:
            portatiles_elements = driver.find_elements(By.CSS_SELECTOR, ".product-card")
            for element in portatiles_elements:
                try:
                    # Find name within each product card
                    name_element = element.find_element(By.CSS_SELECTOR, ".product-card__title")
                    name = name_element.text.strip()

                    # Find price within each product card
                    try:
                        price_element = element.find_element(By.CSS_SELECTOR, ".sc-cPyLVi.eFAgpZ")
                    except:
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

            # Click next page button
            if not click_next_page(driver):
                break

            page_count += 1

            # Add random sleep to mimic human behavior
            sleep(random.uniform(1, 3))

        print("NUMERO PORTATILI = ", len(portatiles))

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
scraping_portatiles()
