import pandas as pd
import os
from utils.mongodb import connect_to_mongo
from utils.selenium import get_driver, get_download_link, get_data_tabs
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from selenium.webdriver.common.by import By
import requests
import io
import time
import re

def update_holidays_db():
    # connect to mongo
    db = connect_to_mongo()
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
    year_vacation = list(db.schoolVacations.find({}, { 'year': 1 }))
    old_year = 0
    array = []
    for index, date_vacation in final_list.items():
        if any(obj['year'] == date_vacation.year for obj in year_vacation) == False:
            if date_vacation.year > old_year:
                if len(array) > 0:
                    object = { "year": old_year, "dates": array }
                    db.schoolVacations.insert_one(object)
                    print("Inserted year= %s" % old_year)
                    result = db.schoolVacations.delete_one({"year": old_year - 4})
                    if (result == 1):
                        print("Deleted year= %s" % (old_year - 4))
                    array = []
                old_year = date_vacation.year
            if date_vacation.year == old_year:
                array.append(date_vacation)


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
    driver.close()
    inc = pd.read_excel(incidents_dl_link)
    mob = pd.read_excel(mobilisations_dl_link)
    if os.path.exists(incidents_dl_link) and os.path.exists(mobilisations_dl_link):
        os.remove(incidents_dl_link)
        os.remove(mobilisations_dl_link)

    return inc, mob

def get_traffic():
    '''
    get traffic data from tomtom
    '''
    # initialize driver
    driver = get_driver()
    driver.get('https://web.archive.org/web/20221110181646/https://www.tomtom.com/traffic-index/london-traffic/')
    try:
        driver.find_element(By.CLASS_NAME, 'CookieBar__button--red').click()
    except:
        pass
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
    # duplicate last actual data for missing years until current year
    max_year = int(historical_congestion_data['year'].unique().max())
    while max_year < datetime.now().year:
        missing_year = max_year + 1
        missing_year_congestion = historical_congestion_data[historical_congestion_data['year'] == str(max_year)]
        missing_year_congestion['year'] = str(missing_year)
        historical_congestion_data = pd.concat([missing_year_congestion, historical_congestion_data]).reset_index(drop=True)
        max_year += 1

    return historical_congestion_data

def get_weather():
    '''
    get data from VisualCrossing API : https://www.visualcrossing.com/
    London weather data by hour (24 values for 1 day)
    For current year (until end of last month) + previous 3 years

    returns:
    dataframe ready to merge with main dataframe 
    '''

    api_key = os.getenv('VISUAL_CROSSING_KEY')

    # weather : get previous 3 years + current year
    date_min = f'{datetime(datetime.now().year - 3, 1, 1):%Y-%m-%d}'
    end_previous_month = datetime.now().replace(day=1) - timedelta(days=1)
    date_max = f'{end_previous_month:%Y-%m-%d}'

    y_min_input, m_min_input, d_min_input = int(date_min[:4]), date_min[5:7], date_min[8:]
    y_max_input, m_max_input, d_max_input = int(date_max[:4]), date_max[5:7], date_max[8:]
    
    # initialize result dataframe
    weather = pd.DataFrame()

    # loop to get the data year by year (api limitation = 10000 records by query)
    for year in range(y_min_input, y_max_input+1):

        # when on the first year of the period : check if other years coming after or not
        if year == y_min_input:
            # define the minimum date to be requested
            y_min, m_min, d_min = y_min_input, m_min_input, d_min_input
            # then look if we are in the last year of the period, to define end of period (date or year end)
            if year == y_max_input:
                y_max, m_max, d_max = year, m_max_input, d_max_input
            else:
                y_max, m_max, d_max = year, '12', '31'

        # when on other years
        else :
            # define the minimum date to be requested
            y_min, m_min, d_min = year, '01', '01'
            # then look if we are in the last year of the period, to define end of period (date or year end)
            if year == y_max_input:
                y_max, m_max, d_max = year, m_max_input, d_max_input
            else:
                y_max, m_max, d_max = year, '12', '31'
    
        # get data from api
        url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/LONDON/{y_min}-{m_min}-{d_min}/{y_max}-{m_max}-{d_max}\
?unitGroup=metric\
&include=hours\
&key={api_key}\
&contentType=csv'.format(
            y_min=y_min,
            m_min=m_min,
            d_min=d_min,
            y_max=y_max,
            m_max=m_max,
            d_max=d_max,
            api_key=api_key
)
        r = requests.get(url)
        # create a dataframe with only useful data 
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df['date'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H')
        df = df[['temp', 'precip', 'cloudcover', 'visibility', 'conditions', 'icon', 'date']]
        
        # add the dataframe to result dataframe
        weather = pd.concat([weather, df])

    # replace NaN in 'precip' by 0 (NaN means no precipitation)
    weather['precip'] = weather['precip'].fillna(0)
    # replace other NaN by previous valid data
    weather = weather.fillna(method='pad')
    # reset index
    weather = weather.reset_index(drop=True)
    
    return weather

def extract():
    '''
    read data from original data folder (../data by default)
    '''
    inc, mob = get_data_london()
    holidays = get_holidays()
    traffic = get_traffic()
    stations = get_stations()
    meteo = get_weather()

    return inc, mob, stations, meteo, holidays, traffic


def merge_datasets(incidents, mobilisations):
    '''
    Merge incidents datasets and mobilisations dataset
    '''
    data = mobilisations.merge(right = incidents, on = 'IncidentNumber', how = 'left')

    return data
