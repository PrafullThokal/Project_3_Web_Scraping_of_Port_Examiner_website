"""
@author: Prafull_Thokal
"""

# Importing required libraries
import pandas as pd
import os 
import yaml
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Setting up logging
logger = logging.getLogger('scraper')
logger.setLevel(logging.DEBUG)

# Reading configuration from config.yml file
with open('config.yml') as f:
    config = yaml.safe_load(f)

# Extracting companies and output file path from configuration
companies = config['companies']
output_file_path = config['output_file_path']

# Formatting logging output
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setting up file handler for logging
file_handler = logging.FileHandler('Prafull_3.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Function to create and return a webdriver instance
def create_webdriver():
    driver_path = "chromedriver.exe" 
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    return driver

# Function to get URLs for a given company
def get_company_urls(driver, company):
    try:
        # Selecting 'consignee' from dropdown
        dropdown = Select(driver.find_element(By.NAME, "search-field-1"))
        dropdown.select_by_value('consignee')
        
        # Entering company name in search bar and clicking search button
        search_bar = driver.find_element(By.ID, "input-box")
        search_bar.send_keys(company)
        search_button = driver.find_element(By.ID, "search-button")
        search_button.click()
        
        # Extracting URLs from search results
        search_items = driver.find_elements(By.CLASS_NAME, "search-item")
        urls = []
        for items in search_items:
            links = items.find_elements(By.TAG_NAME, "a")
            for link in links:
                urls.append(link.get_attribute("href"))
        return urls
    except Exception as e:
        logger.error(f"Error while searching for company {company}: {e}")
        return []

# Function to parse data for a given company and URLs
def parse_company_data(driver, urls, company):
    try:
        results = []
        for url in urls:
            driver.get(url)
            set1 = {"Company": company}
            xpath_dict = {
                "//*[@id='shipper']/div/div/h1/a/span": "Shipper",
                "//*[@id='consignee']/div/div/h1/a/span": "Consignee",
                "//*[@id='details']/div/div/div/div[1]/div": "Bill of Landing No",
                "//*[@id='details']/div/div/div/div[2]/div": "Vessel Name",
                "//*[@id='details']/div/div/div/div[3]/div": "Voyage No",
                "//*[@id='details']/div/div/div/div[4]/div/span": "Place of Receipt",
                "//*[@id='details']/div/div/div/div[5]/div/span": "Port of Loading",
            }
            # Extracting data for each element using XPath
            for xpath, column_name in xpath_dict.items():
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    set1[column_name] = element.get_attribute('innerHTML')
                except:
                    set1[column_name] = ""
            results.append(set1)
        return results
    except Exception as e:
        logger.error(f"Error while scraping data for company {company}: {e}")
        return []

# Define a function to export data from a DataFrame to a CSV file
def export_to_csv(df , filepath = r'C:\Users\Prafull_Thokal\A3_output.csv'):
    # Create the directory to store the CSV file if it does not exist
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Export the data to a CSV file
    df.to_csv(filepath, index=False)
    # Print a message to indicate that the CSV file has been saved
    print(f"CSV file saved at {filepath}")
    # Log a message to indicate that the CSV file has been saved
    logger.info(f"CSV file saved at {filepath}")
    
# Define a function to scrape data from the website and save it to a DataFrame
def scrape_and_save_data():
    # Create a new instance of the Chrome browser
    driver = create_webdriver()
    # Load the website
    driver.get('https://portexaminer.com/')
    # Create an empty list to store the results
    results = []
    # Loop through each company in the list of companies
    for company in companies:
        # Get the URLs associated with the company
        urls = get_company_urls(driver, company)
        # If there are URLs associated with the company, scrape the data and store it in the results list
        if len(urls) > 0:
            company_data = parse_company_data(driver, urls, company)
            results.extend(company_data)
    driver.quit()
    df = pd.DataFrame(results)
    return df

# Scrape the data and save it to a DataFrame
df = scrape_and_save_data()
export_to_csv(df)
print(df)

# Log the DataFrame
logger.info(df)
