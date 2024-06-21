from undetected_chromedriver import Chrome as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
import re
import psycopg2

# Setup Chrome options
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# PostgreSQL connection details
conn = psycopg2.connect(
    dbname="mydatabase",
    user="postgres",
    password="ema",  # Replace with your password
    host="localhost",  # Or your database host
    port="5432"  # Or your database port
)

class Portatile:
    def __init__(self, name: str, price: float, link: str, photo_url: str):
        self.name = name
        self.price = price
        self.link = link
        self.photo_url = photo_url

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

def create_table_if_not_exists(cur):
    try:
        # Define the SQL query for creating table if not exists
        create_table_query = """
            CREATE TABLE IF NOT EXISTS portatiles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                price NUMERIC,
                photo TEXT,
                link TEXT
            )
        """
        cur.execute(create_table_query)
        print("Table 'portatiles' created successfully (if it did not exist).")
    except Exception as e:
        print(f"Error creating table: {e}")

def truncate_table(cur):
    try:
        # Define the SQL query for truncating the table
        truncate_query = "TRUNCATE TABLE portatiles RESTART IDENTITY"
        cur.execute(truncate_query)
        print("Table 'portatiles' truncated successfully.")
    except Exception as e:
        print(f"Error truncating table: {e}")

def scraping_portatiles():
    # Initialize the Chrome driver
    driver = uc(options=options)
    try:
        # Visit the PC Componentes website
        driver.get("https://www.pccomponentes.com/search/?query=portatiles&or-relevance")
        print("Opened PC Componentes search page.")

        # Accept cookies if the popup appears
        accept_cookies(driver)

        # Get total number of pages
        total_pages = get_total_pages(driver)
        if total_pages is None:
            return
        
        # Initialize database cursor
        cur = conn.cursor()

        # Create table if not exists
        create_table_if_not_exists(cur)

        # Truncate table before inserting new data
        truncate_table(cur)

        # Define the maximum number of pages to scrape
        max_pages = total_pages
        page_count = 0

        # List to store Portatile objects
        portatiles_to_insert = []

        while page_count < max_pages:
            portatiles_elements = driver.find_elements(By.CSS_SELECTOR, ".product-card")
            print(f"Found {len(portatiles_elements)} product cards on page {page_count + 1}.")

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

                    # Find link and photo URL within the product card's context
                    link_element = element.find_element(By.XPATH, "..")
                    link = link_element.get_attribute("href")

                    photo_element = element.find_element(By.CSS_SELECTOR, ".sc-hybRYi.fviDRD")
                    photo_url = photo_element.get_attribute("src")

                    # Create Portatile object and add to list
                    new_portatile = Portatile(name, price, link, photo_url)
                    portatiles_to_insert.append((new_portatile.name, new_portatile.price, new_portatile.photo_url, new_portatile.link))

                except Exception as e:
                    print(f"Error processing element: {e}")

            # Click next page button
            if not click_next_page(driver):
                break

            page_count += 1

            # Add random sleep to mimic human behavior
            sleep(random.uniform(1, 3))

        # Insert data into PostgreSQL in batch
        if portatiles_to_insert:
            insert_query = """
                INSERT INTO portatiles (name, price, photo, link)
                VALUES (%s, %s, %s, %s)
            """
            cur.executemany(insert_query, portatiles_to_insert)
            print(f"Inserted {len(portatiles_to_insert)} portatiles into database.")

        # Commit changes to the database
        conn.commit()
        print(f"Finished scraping. {len(portatiles_to_insert)} portatiles inserted into database.")

    finally:
        if cur:
            # Close cursor
            cur.close()
        # Close connection
        conn.close()
        # Close the driver
        driver.quit()

# Initiate the web scraping task
scraping_portatiles()
