import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dotenv import load_dotenv
import os

load_dotenv()

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    # initialize driver
    driver = webdriver.Remote(
            command_executor=os.getenv('SELENIUM_HOST') + '/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME)

    return driver

def get_download_link(url, link_text, driver):
    driver.get(url)
    dl_link = driver.find_element(By.LINK_TEXT, link_text)
    file_dl_link = dl_link.get_attribute("href")

    return file_dl_link

def get_data_tabs(numero_tag, driver, elt, index):
    elt[numero_tag].click()
    webelt = driver.find_elements(By.CLASS_NAME, 'Tabs')
    congestion_data_year = webelt[1].text.split()[index]
    congestion_data_year_percentages = driver.find_element(By.CLASS_NAME, 'StatWeekHours__labels-congestions').text.split('\n')

    return congestion_data_year, congestion_data_year_percentages