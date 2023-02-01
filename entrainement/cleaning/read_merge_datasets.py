import pandas as pd
import os
from utils.mongodb import connect_to_mongo
from utils.selenium import get_driver, get_download_link, get_data_tabs
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By

# initial data location (if main clean file in /entrainement/clean_data_add_features/)
# data_loc = "../../data/"

# initial data location (if main clean file in /entrainement/)
# data_loc = "../data/"

#os.chdir(os.path.dirname(os.path.abspath(__file__)))

# original files => see later how (database / scrap)
incidents_file = 'LFB Incident data Last 3 years'
mobilisations_file = 'LFB Mobilisation data Last 3 years'
stations_file = 'pos station.csv'                                # only once (no change except if new stations built)
school_holidays_file = 'holidays.csv'                            # to be updated when new calendar available
weather_file = 'Weather London.csv'                              # to be updated (get past month data, once a month ?)
traffic_file = 'london_congestion.csv'

def get_holidays():
    '''
    get holidays from mongodb
    '''
    db = connect_to_mongo()
    year_date_now = datetime.now().year
    dates_vacations = list(db.schoolVacations.find({ 'year': {'$gte': year_date_now - 3, '$lte': year_date_now }}, { 'dates': 1, '_id': 0 }))
    if len(dates_vacations) < 3:
        raise Exception("No three year data found in MongoDB")
    merge_dates_vacations = dates_vacations[0]['dates'] + dates_vacations[1]['dates'] + dates_vacations[2]['dates']
    formattedList = [member.strftime("%d/%m/%Y") for member in merge_dates_vacations]
    df_dates_vacations = pd.DataFrame(formattedList, columns=['date'])

    return df_dates_vacations

def get_stations():
    '''
    get stations from mongodb
    '''
    db = connect_to_mongo()
    stations = list(db.stations.find({}, { '_id': 0 }))
    code = [station['code'] for station in stations]
    name = [station['name'] for station in stations]
    latitude = [station['latitude'] for station in stations]
    longitude = [station['longitude'] for station in stations]
    df_stations = pd.DataFrame(list(zip(code, name, latitude, longitude)), columns=['Station_Code', 'Station_Name', 'Station_Latitude', 'Station_Longitude'])

    return df_stations

def get_data_london():
    '''
    get data from london data portal
    '''
    # initialize driver
    driver = get_driver()
    incidents_dl_link = get_download_link(
        url= 'https://data.london.gov.uk/dataset/london-fire-brigade-incident-records',
        link_text= 'LFB Incident data - last three years',
        driver=driver
        )
    mobilisations_dl_link = get_download_link(
        url= 'https://data.london.gov.uk/dataset/london-fire-brigade-mobilisation-records',
        link_text= 'LFB Mobilisation data - last three years',
        driver=driver
        )
    inc = pd.read_excel(incidents_dl_link)
    mob = pd.read_excel(mobilisations_dl_link)
    if os.path.exists(incidents_dl_link) and os.path.exists(mobilisations_dl_link):
        os.remove(incidents_dl_link)
        os.remove(mobilisations_dl_link)
    driver.close()

    return inc, mob

def get_traffic():
    '''
    get traffic data from tomtom
    '''
    # initialize driver
    driver = get_driver()
    driver.get('https://www.tomtom.com/traffic-index/london-traffic/')
    driver.find_element(By.CLASS_NAME, 'CookieBar__button').click()
    live_traffic = driver.find_elements(By.CLASS_NAME, 'live-number')
    congestion_now = live_traffic[0].text
    congestion_now = int(congestion_now.replace('%', ''))/100
    elt = driver.find_elements(By.TAG_NAME, 'li')
    congestion_data_year_3, congestion_data_year_percentages_3 = get_data_tabs(12, driver, elt, 0)
    congestion_data_year_2, congestion_data_year_percentages_2 = get_data_tabs(13, driver, elt, 1)
    congestion_data_year_1, congestion_data_year_percentages_1 = get_data_tabs(14, driver, elt, 2)
    historical_congestion_data = pd.DataFrame()
    week_day = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday"
    }
    for year, data in zip(
        [congestion_data_year_3, congestion_data_year_2, congestion_data_year_1],
        [congestion_data_year_percentages_3, congestion_data_year_percentages_2, congestion_data_year_percentages_1]):
        congestion_data = pd.DataFrame()
        congestion_data['congestion'] = [int(x.replace('%', ''))/100 for x in data]
        congestion_data['hour'] = list(range(24))*7
        congestion_data['day_nb'] = [i for i in range(1,8) for x in range(24)]
        congestion_data['day'] = congestion_data['day_nb'].map(week_day)
        congestion_data['year'] = year
        historical_congestion_data = pd.concat([historical_congestion_data, congestion_data]).reset_index(drop=True)
    driver.close()

    return historical_congestion_data

def get_weather():
    '''
    get weather data from openweather
    '''
    'A completer'

def extract(path_to_data= "../data"):
    '''
    read data from original data folder (../data by default)
    '''
    
    # convert xlsx datasets to csv (xlsx from https://data.london.gov.uk/)
    # Xlsx2csv(incidents_file+'.xlsx').convert((incidents_file+'.csv'))
    # Xlsx2csv(mobilisations_file+'.xlsx').convert((mobilisations_file+'.csv'))
    inc, mob = get_data_london()
    holidays = get_holidays()
    traffic = get_traffic()
    stations = get_stations()
    # create dataframes from csv
    # inc = pd.read_csv(os.path.join(path_to_data, incidents_file+'.csv')) # scraping
    # mob = pd.read_csv(os.path.join(path_to_data, mobilisations_file+'.csv')) # scraping

    # create dataframes for other files
    #station_pos=pd.read_csv(os.path.join(path_to_data, stations_file))
    meteo = pd.read_csv(os.path.join(path_to_data, weather_file)) # api
    # holidays=pd.read_csv(os.path.join(path_to_data, school_holidays_file), sep=';') # bdd
    #traffic = pd.read_csv(os.path.join(path_to_data, traffic_file), sep=';') # scraping

    return inc, mob, stations, meteo, holidays, traffic


def merge_datasets(incidents, mobilisations):
    '''
    Merge incidents datasets and mobilisations dataset
    '''

    data = mobilisations.merge(right = incidents, on = 'IncidentNumber', how = 'left')

    return data
