from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# For Local Use this Driver Setup
# def setup_driver():
#     """Set up the Selenium WebDriver."""
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-notifications")
#     options.add_argument("--disable-popup-blocking")
#     return webdriver.Chrome(options=options)

# For Deployment Use this Driver Setup

def setup_driver():
    """Set up the Selenium WebDriver in headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use headless mode (newer version for better compatibility)
    options.add_argument("--start-maximized")  # Maximized viewport (optional in headless)
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")  # Recommended for headless mode on Linux servers
    options.add_argument("--disable-dev-shm-usage")  # Avoid issues with /dev/shm on Linux
    options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional but helpful in headless)
    options.add_argument("--window-size=1920,1080")  # Set default window size for headless browser

    return webdriver.Chrome(options=options)


def search_google_maps(driver, search_query):
    """Search for a query on Google Maps."""
    driver.get("https://www.google.com/maps")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for results to load

def scroll_and_scrape(driver):
    """Scroll through Google Maps results and scrape data."""
    results = []
    end_of_list_detected = False

    while not end_of_list_detected:
        try:
            # Wait for the scrollable results container to load
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )

            # Fetch all visible business results
            businesses = scrollable_div.find_elements(By.CLASS_NAME, "Nv2PK")

            for business in businesses:
                try:
                    # Extract name of the business
                    name = business.find_element(By.CLASS_NAME, "qBF1Pd").text
                except:
                    name = "N/A"

                try:
                    # Extract rating (including reviews count) from the correct element
                    rating_element = business.find_element(By.CLASS_NAME, "MW4etd")
                    reviews_element = business.find_element(By.CLASS_NAME, "UY7F9")
                    rating = f"{rating_element.text} {reviews_element.text}"  # Combine rating and review count
                except:
                    rating = "N/A"

                try:
                    # Extract description (like "Open 24 hours" or other details) from the second W4Efsd div
                    description = "No Description"
                    description_elements = business.find_elements(By.CLASS_NAME, "W4Efsd")
                    if len(description_elements) > 1:
                        description = description_elements[1].text.strip()  # Use the second W4Efsd div
                    if not description:
                        description = "No Description"
                except:
                    description = "No Description"

                try:
                    # Extract image URL (first image tag)
                    image = business.find_element(By.TAG_NAME, "img").get_attribute("src")
                except:
                    image = "N/A"

                try:
                    # Wait explicitly for the <a> tag with visited link (hfpxzc class) to appear
                    visited_link = business.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
                except:
                    visited_link = "N/A"  # Default value if the link is not found

                # Avoid duplicates by checking the unique combination of Name and Rating
                if {"Name": name, "Rating": rating, "Description": description, "Image": image, "Visited Link": visited_link} not in results:
                    results.append({"Name": name, "Rating": rating, "Description": description, "Image": image, "Visited Link": visited_link})

            # Check for the "end of list" message using class name (PbZDve)
            try:
                end_of_list = driver.find_element(By.CLASS_NAME, "PbZDve")
                if end_of_list.is_displayed():
                    print("End of list detected.")
                    end_of_list_detected = True  # End of list is detected, stop scraping
            except:
                pass  # No "end of list" message, continue scrolling

            # Scroll down to load more results
            driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
            time.sleep(1)  # Allow time for new results to load

        except Exception as e:
            print(f"Error during scrolling: {e}")
            end_of_list_detected = True

    # Quit the driver when the loop ends
    print("Quitting driver after scraping is complete.")
    driver.quit()  # Forcefully quit the driver after scraping ends
    return results


def scrape_google_maps(industry, country, city):
    """Perform the Google Maps scrape for the provided search parameters."""
    search_query = f"{industry} in {city}, {country}"
    driver = setup_driver()
    results = []

    try:
        search_google_maps(driver, search_query)
        results = scroll_and_scrape(driver)
    finally:
        driver.quit()  # Ensure driver is quit when scraping is complete

    return results
