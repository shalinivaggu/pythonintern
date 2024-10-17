import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import traceback

# Function to download an image
def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded: {save_path}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")

def download_file(file_url, save_path):
    try:
        # Follow redirects to get the final file URL
        response = requests.get(file_url, allow_redirects=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded: {save_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading file: {e}")

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

url = "https://www.sick.com/in/en/catalog/products/detection-sensors/photoelectric-sensors/w4/wtb4fp-22161120a00/p/p661408?tab=detail"
driver.get(url)
    
try:
    # Wait for the technical details section to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'technical-details')))

    # Extract technical details from the relevant tables
    technical_details = {}
    tables = driver.find_elements(By.CSS_SELECTOR, ".tech-table")  # Select all tables with class 'tech-table'

    for table in tables:
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) == 2:  # Ensure that there are two columns
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                technical_details[key] = value

    print("Technical Product Details:")
    for key, value in technical_details.items():
        print(f"{key}: {value}")

except Exception as e:
    print(f"An error occurred: {e}")


try:
    # Wait for the product image to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[title='W4F, NextGen, WTB4FP, M8 plug']")))

    # Download the product image
    image_element = driver.find_element(By.CSS_SELECTOR, "img[alt='W4F, NextGen, WTB4FP, M8 plug']")
    # After locating the image element
    try:
        # Assuming image_element is your WebElement
        image_url = image_element.get_attribute('data-src')
        print(f"Image URL: {image_url}")  # Output the URL for debugging

        if image_url:
            image_save_path = os.path.join(os.getcwd(), 'product_image.png')
            download_image(image_url, image_save_path)
        else:
            print("Image URL is None. Check the selector.")
    except Exception as e:
        print(f"Error retrieving image URL: {e}")

    try:
        # Wait for the product datasheet link to load
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ui-split-button .action-button"))
        )

        # Print button details for debugging
        print(f"Download Button: {download_button}")
        print(f"Button Text: {download_button.text}")

        driver.execute_script("arguments[0].click();", download_button)

        # Wait for the dropdown menu to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".split-button-dropdown li"))
        )

        # Find the specific language option (e.g., English button)
        english_button = driver.find_element(By.XPATH, "//span[contains(text(), 'English')]/..")

        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", english_button)

        # Use ActionChains to move to the element and click it
        actions = ActionChains(driver)
        actions.move_to_element(english_button).click().perform()

        # Wait for a brief moment to allow the new tab to open
        time.sleep(2)  # Adjust the sleep time as necessary

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[1])

        navigated_url = driver.current_url
        print(navigated_url)
        pdf_url = navigated_url
        pdf_save_path = os.path.join(os.getcwd(), 'datasheet_WTB4FP.pdf')

        # Download the PDF file
        download_file(pdf_url, pdf_save_path)



    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

finally:
    driver.quit()  # Close the browser
