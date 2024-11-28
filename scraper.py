import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure logging
logging.basicConfig(
    filename='scraper.log',  # Log file name
    level=logging.INFO,  # Logging level (INFO for general messages, DEBUG for more detailed logs)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format in logs
)

def setup_driver():
    """Set up the Selenium WebDriver in headless mode."""
    logging.info("Setting up the Selenium WebDriver.")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    logging.info("WebDriver setup complete.")
    return webdriver.Chrome(options=options)

def search_google_maps(driver, search_query):
    """Search for a query on Google Maps."""
    try:
        logging.info(f"Navigating to Google Maps with query: {search_query}")
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))

        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        logging.info(f"Search query '{search_query}' submitted.")
        time.sleep(5)  # Wait for results to load
    except Exception as e:
        logging.error(f"Error during search: {e}")

def scroll_and_scrape(driver):
    """Scroll through Google Maps results and scrape data."""
    logging.info("Starting the scroll and scrape process.")
    results = []
    end_of_list_detected = False

    while not end_of_list_detected:
        try:
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )
            businesses = scrollable_div.find_elements(By.CLASS_NAME, "Nv2PK")
            logging.info(f"Found {len(businesses)} businesses in this scroll.")

            for business in businesses:
                try:
                    name = business.find_element(By.CLASS_NAME, "qBF1Pd").text
                except:
                    name = "N/A"

                try:
                    rating_element = business.find_element(By.CLASS_NAME, "MW4etd")
                    reviews_element = business.find_element(By.CLASS_NAME, "UY7F9")
                    rating = f"{rating_element.text} {reviews_element.text}"
                except:
                    rating = "N/A"

                try:
                    description = "No Description"
                    description_elements = business.find_elements(By.CLASS_NAME, "W4Efsd")
                    if len(description_elements) > 1:
                        description = description_elements[1].text.strip()
                    if not description:
                        description = "No Description"
                except:
                    description = "No Description"

                try:
                    image = business.find_element(By.TAG_NAME, "img").get_attribute("src")
                except:
                    image = "N/A"

                try:
                    visited_link = business.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
                except:
                    visited_link = "N/A"

                if {"Name": name, "Rating": rating, "Description": description, "Image": image, "Visited Link": visited_link} not in results:
                    results.append({"Name": name, "Rating": rating, "Description": description, "Image": image, "Visited Link": visited_link})

            try:
                end_of_list = driver.find_element(By.CLASS_NAME, "PbZDve")
                if end_of_list.is_displayed():
                    logging.info("End of list detected. Stopping scrolling.")
                    end_of_list_detected = True
            except:
                pass

            driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error during scrolling: {e}")
            end_of_list_detected = True

    logging.info(f"Scraping completed. Total results: {len(results)}.")
    driver.quit()
    return results

def scrape_google_maps(industry, country, city):
    """Perform the Google Maps scrape for the provided search parameters."""
    search_query = f"{industry} in {city}, {country}"
    logging.info(f"Starting scrape for: {search_query}")
    driver = setup_driver()
    results = []

    try:
        search_google_maps(driver, search_query)
        results = scroll_and_scrape(driver)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver closed after scraping.")

    logging.info("Scrape completed.")
    return results
