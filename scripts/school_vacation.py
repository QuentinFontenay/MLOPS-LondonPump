from pymongo import mongo_client
import os
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

load_dotenv('../.env.production')

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    command_executor=os.environ.get('SELENIUM_HOST') + '/wd/hub'
    # initialize driver
    driver = webdriver.Remote(
            command_executor=command_executor,
            desired_capabilities=DesiredCapabilities.CHROME)
    return driver

def connect_to_mongo():
    client = mongo_client.MongoClient(
        os.environ.get('DATABASE_URL'), serverSelectionTimeoutMS=5000)

    try:
        conn = client.server_info()
        print(f'Connected to MongoDB {conn.get("version")}')
    except Exception:
        print("Unable to connect to the MongoDB server.")

    db = client[os.environ.get('MONGO_INITDB_DATABASE')]
    school_vacation = db.schoolVacations

    return school_vacation

driver = get_driver()
    # Accès à la page
driver.get('https://publicholidays.co.uk/school-holidays/england/barking-and-dagenham/')
    # Agrandissement de la fenêtre
driver.minimize_window()
    # accepter les cookies
time.sleep(2) # temporisation pour attendre que la fenêtre soit affichée
driver.find_element(By.CSS_SELECTOR, '.css-6napma.css-6napma.css-6napma.css-6napma .qc-cmp2-footer .qc-cmp2-summary-buttons button:last-of-type').click()
r = re.compile(r"[0-9]{1,2} [A-Za-z]{3} [0-9]{4}")
holidays_periods = []

for i in driver.find_elements(By.CLASS_NAME, 'odd'):
    holiday = r.findall(i.text)
    if len(holiday) == 2:
        holidays_periods.append(holiday)

for i in driver.find_elements(By.CLASS_NAME, 'even'):
    holiday = r.findall(i.text)
    if len(holiday) == 2:
        holidays_periods.append(holiday)
driver.close()
# Créer un df des plages de vacances scolaires
holidays_df = pd.DataFrame(holidays_periods).rename({0: "beg", 1: "end"}, axis = 1)
holidays_df = holidays_df.astype('datetime64')
school_vacation = connect_to_mongo()
# Créer la liste des jours de vacances scolaires
holidays_list = []
for i in holidays_df.index:
    day = holidays_df.loc[i]['beg']
    while day <= holidays_df.loc[i]['end']:
        holidays_list.append(day)
        day += timedelta(1)
        
holidays_list_df = pd.DataFrame(holidays_list)
holidays_list_df = holidays_list_df.rename({0: "date"}, axis=1)
holidays_list_df['weekday'] = holidays_list_df['date'].apply(lambda x: x.weekday())
final_list = holidays_list_df[holidays_list_df['weekday']<5]['date']
final_list = final_list.sort_values()
year_vacation = list(school_vacation.find({}, { 'year': 1 }))
old_year = 0
array = []
for index, date_vacation in final_list.items():
    if any(obj['year'] == date_vacation.year for obj in year_vacation) == False:
        if date_vacation.year > old_year:
            if len(array) > 0:
                object = { "year": old_year, "dates": array }
                school_vacation.insert_one(object)
                print("Inserted year= %s" % old_year)
                result = school_vacation.delete_one({"year": old_year - 4})
                if (result == 1):
                    print("Deleted year= %s" % (old_year - 4))
                array = []
            old_year = date_vacation.year
        if date_vacation.year == old_year:
            array.append(date_vacation)
