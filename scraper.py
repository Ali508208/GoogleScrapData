from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


def setup_driver():
    """Set up the Selenium WebDriver in headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)


def search_google_maps(driver, search_query):
    """Search for a query on Google Maps."""
    try:
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))

        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        time.sleep(5)
    except TimeoutException:
        print("Error: Timeout while loading Google Maps or finding the search box.")
        raise
    except Exception as e:
        print(f"Error during search operation: {e}")
        raise


def extract_business_data(business):
    """Extract details for a single business."""
    try:
        name = business.find_element(By.CLASS_NAME, "qBF1Pd").text or "N/A"
    except NoSuchElementException:
        name = "N/A"

    try:
        rating = business.find_element(By.CLASS_NAME, "MW4etd").text
        reviews = business.find_element(By.CLASS_NAME, "UY7F9").text
        rating = f"{rating} {reviews}"
    except NoSuchElementException:
        rating = "N/A"

    try:
        description = "No Description"
        description_elements = business.find_elements(By.CLASS_NAME, "W4Efsd")
        if len(description_elements) > 1:
            description = description_elements[1].text.strip() or "No Description"
    except NoSuchElementException:
        pass

    try:
        image = business.find_element(By.TAG_NAME, "img").get_attribute("src") or "N/A"
    except NoSuchElementException:
        image = "N/A"

    try:
        visited_link = business.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href") or "N/A"
    except NoSuchElementException:
        visited_link = "N/A"

    return {
        "Name": name,
        "Rating": rating,
        "Description": description,
        "Image": image,
        "Visited Link": visited_link,
    }


def scroll_and_scrape(driver):
    """Scroll through Google Maps results and scrape data."""
    results = []
    end_of_list_detected = False

    while not end_of_list_detected:
        try:
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )
            businesses = scrollable_div.find_elements(By.CLASS_NAME, "Nv2PK")

            for business in businesses:
                business_data = extract_business_data(business)
                if business_data not in results:
                    results.append(business_data)

            try:
                end_of_list = driver.find_element(By.CLASS_NAME, "PbZDve")
                if end_of_list.is_displayed():
                    end_of_list_detected = True
            except NoSuchElementException:
                pass

            driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
            time.sleep(1)
        except TimeoutException:
            print("Error: Timeout while scrolling through results.")
            end_of_list_detected = True
        except Exception as e:
            print(f"Error during scrolling and scraping: {e}")
            end_of_list_detected = True

    driver.quit()
    return results


def scrape_google_maps(industry, country, city):
    """Perform the Google Maps scrape for the provided search parameters."""
    search_query = f"{industry} in {city}, {country}"
    driver = setup_driver()
    results = []

    try:
        search_google_maps(driver, search_query)
        results = scroll_and_scrape(driver)
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()

    return results
