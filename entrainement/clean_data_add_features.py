import pandas as pd
import numpy as np
from xlsx2csv import Xlsx2csv                   # to convert xlsx to csv
from convertbng.cutil import convert_lonlat     # to convert gps data
from workalendar.europe.united_kingdom import UnitedKingdom
from datetime import date # utile pour jours travaillés
from time import time


# original files
incidents_file = '../data/LFB Incident data Last 3 years'
mobilisations_file = '../data/LFB Mobilisation data Last 3 years'
stations_file = '../data/pos station.csv'                                # only once (no change except if new stations built)
school_holidays_file = '../data/holidays.csv'                            # to be updated when new calendar available
weather_file = '../data/Weather London.csv'                              # to be updated (get past month data, once a month ?)
traffic_file = '../data/london_congestion.csv'                           # to be updated each year


def extract():
    
    # convert xlsx datasets to csv (xlsx from https://data.london.gov.uk/)
    # Xlsx2csv(incidents_file+'.xlsx').convert((incidents_file+'.csv'))
    # Xlsx2csv(mobilisations_file+'.xlsx').convert((mobilisations_file+'.csv'))
    
    # create dataframes from csv
    inc = pd.read_csv(incidents_file+'.csv')
    mob = pd.read_csv(mobilisations_file+'.csv')

    # create dataframes for other files
    station_pos=pd.read_csv(stations_file)
    meteo = pd.read_csv(weather_file)
    holidays=pd.read_csv(school_holidays_file, sep=';')
    traffic = pd.read_csv(traffic_file, sep=';')

    return inc, mob, station_pos, meteo, holidays, traffic


def convert_gps(data):
    '''
    Convert GPS data from incidents dataframe from OSGB 1936 (British National Grid) to WGS 84
    '''

    gps_conv = convert_lonlat(data['Easting_rounded'].to_list(), data['Northing_rounded'].to_list())
    
    # create new columns for GPS converted
    data['Lat'] = gps_conv[1]
    data['Lon'] = gps_conv[0]

    return data


def create_appliance(data):
    '''
    Create appliance (vehicle type) in mobilisations dataframe
    '''

    data['Appliance'] = (data['Resource_Code'].apply(lambda x : x[-1:])).map({'2' : 'Pump Ladder', '1' : 'Pump Dual Ladder'})

    return data


def merge_datasets(incidents, mobilisations):
    '''
    Merge incidents datasets and mobilisations dataset
    '''

    lfb = mobilisations.merge(right = incidents, on = 'IncidentNumber', how = 'left')

    return lfb


def remove_variables(data):
    '''
    Remove useless variables
    '''

    remove_col = [
        'ResourceMobilisationId',
        'PerformanceReporting',
        'DateAndTimeReturned',
        'PlusCode_Code',
        'PlusCode_Description',
        'DelayCodeId',
        'Postcode_full',
        'Postcode_district',
        'UPRN',
        'USRN',
        'IncGeo_BoroughCode',
        'IncGeo_BoroughName',
        'ProperCase',
        'IncGeo_WardCode',
        'IncGeo_WardName',
        'IncGeo_WardNameNew',
        'Easting_m',
        'Northing_m',
        'Easting_rounded',
        'Northing_rounded',
        'Latitude',
        'Longitude',
        'FRS',
        'FirstPumpArriving_AttendanceTime',
        'FirstPumpArriving_DeployedFromStation',
        'SecondPumpArriving_AttendanceTime',
        'SecondPumpArriving_DeployedFromStation',
        'PumpHoursRoundUp',
        'Notional Cost (£)',
    ]

    data = data.drop(remove_col, axis = 1)

    if "NumCalls" in data.columns:
        data = data.drop("NumCalls", axis = 1)

    return data


def missing_date_of_call(data):
    '''
    Remove incidents that do not have any Date of call
    '''

    inc_nan_list = list(data[data['DateOfCall'].isna()]['IncidentNumber'].unique())
    data = data.drop(axis=0, index=data[data['IncidentNumber'].isin(inc_nan_list)].index)
    
    return data


def convert_date_and_time(data):
    '''
    Converts 4 variables to datetime format
        - DateAndTimeMobile
        - DateAndTimeMobilised
        - DateAndTimeLeft
        - DateAndTimeArrived
    '''
    
    data['DateAndTimeMobile'] = pd.to_datetime(data['DateAndTimeMobile'], format="%d/%m/%Y %H:%M:%S")
    data['DateAndTimeMobilised'] = pd.to_datetime(data['DateAndTimeMobilised'], format="%d/%m/%Y %H:%M:%S")
    data['DateAndTimeLeft'] = pd.to_datetime(data['DateAndTimeLeft'], format="%d/%m/%Y %H:%M:%S")
    data['DateAndTimeArrived'] = pd.to_datetime(data['DateAndTimeArrived'], format="%d/%m/%Y %H:%M:%S")

    return data


def missing_tournout_time_seconds(data):
    '''
    Estimates missing TurnoutTimeSeconds
    With average % usually noticed (in average, Turnout times represents xx % from AttendanceTime)
    '''

    # list of index where TurnoutTimeSeconds is NaN
    index_mobile_nan = list(data[data['DateAndTimeMobile'].isna()].index)

    # average TurnoutTimeSeconds for pumps without NaNs
    turnout_avg = data[data.notna()]['TurnoutTimeSeconds'].mean()
    # average AttendanceTimeSeconds for pumps without NaNs
    attendance_avg = data[data.notna()]['AttendanceTimeSeconds'].mean()

    # % of TurnoutTime vs AttendanceTimeSeconds for pumps without NaNs
    turnout_prop = turnout_avg/attendance_avg

    # loop to fill missing TurnoutTimeSeconds
    for i in index_mobile_nan:
        # fill missing TurnoutTimeSeconds
        data['TurnoutTimeSeconds'].loc[i] = np.round(data['AttendanceTimeSeconds'].loc[i] * turnout_prop , 0)
        # recalculate TravelTimeSeconds (= AttendanceTimeSeconds - TurnoutTimeSeconds)
        data['TravelTimeSeconds'][i] = data['AttendanceTimeSeconds'][i] - data['TurnoutTimeSeconds'][i]
        # recalculate DateAndTimeMobile = DateAndTimeMobilised + TurnoutTimeSeconds
        data['DateAndTimeMobile'][i] = pd.to_datetime(data['DateAndTimeMobilised'][i]) + pd.to_timedelta(data['TurnoutTimeSeconds'][i], unit = 's')

    return data


def missing_travel_time(data):
    '''
    Fill missing values in TravelTimeSeconds
    3 different cases depending on DateAndTimeMobile and DateAndTimeArrived data :
    
    if DateAndTimeMobile > DateAndTimeArrived : assumption = data have been swapped => correction
    if DateAndTimeMobile = DateAndTimeArrived : set TurnoutTime to 0 (some already exist)
    if DateAndTimeMobile < DateAndTimeArrived : no way to correct the data => remove the incidents concerned
    '''

    # index of records concerned (DateAndTimeMobile > DateAndTimeArrived)
    index_travel_nan_gt_arrived = list(data[(data['TravelTimeSeconds'].isna()) & (data['DateAndTimeMobile'] > data['DateAndTimeArrived'])].index)
    # loop to fill the NaNs
    for i in index_travel_nan_gt_arrived:
        # swap DateAndTimeMobile & DateAndTimeArrived
        data['DateAndTimeMobile'].loc[i], data['DateAndTimeArrived'].loc[i] = data['DateAndTimeArrived'].loc[i], data['DateAndTimeMobile'].loc[i]
        # swap TurnoutTimeSeconds & AttendanceTimeSeconds
        data['TurnoutTimeSeconds'].loc[i], data['AttendanceTimeSeconds'].loc[i] = data['AttendanceTimeSeconds'].loc[i], data['TurnoutTimeSeconds'].loc[i]
        # recalculate TravelTimeSeconds
        data['TravelTimeSeconds'][i] = data['AttendanceTimeSeconds'][i] - data['TurnoutTimeSeconds'][i]

    # index of records concerned (DateAndTimeMobile = DateAndTimeArrived)
    index_travel_nan_eq_arrived = list(data[(data['TravelTimeSeconds'].isna()) & (data['DateAndTimeMobile'] == data['DateAndTimeArrived'])].index)
    # set TurnoutTime to zero
    data['TurnoutTimeSeconds'] = data['TurnoutTimeSeconds'].fillna(0)
     
    # index of records concerned (DateAndTimeMobile < DateAndTimeArrived)
    index_travel_nan_lt_arrived = list(data[(data['TravelTimeSeconds'].isna()) & (data['DateAndTimeMobile'] < data['DateAndTimeArrived'])].index)
    # List of incidents
    inc_mob_eq_arrived = data.loc[index_travel_nan_eq_arrived]['IncidentNumber'].unique()
    # remove records corresponding to these incidents
    data = data.drop(axis = 0, index = data[data['IncidentNumber'].isin(inc_mob_eq_arrived)].index)

    return data


def missing_deployed_from_station(data):
    '''
    Fill missing values in DeployedFromStation_Code and Name
    '''
        
    # index of records concerned
    index_station_nan = list(data[data['DeployedFromStation_Code'].isna()].index)

    # create a dataframe of stations
    station_list = data.groupby(by = ['DeployedFromStation_Code', 'DeployedFromStation_Name']).count().reset_index()[['DeployedFromStation_Code', 'DeployedFromStation_Name']]
    station_list = station_list.rename({'DeployedFromStation_Code' : 'Station_code', 'DeployedFromStation_Name' : 'Station_name'}, axis = 1)

    # loop to compute new values for DeployedFromStation_Code & Name
    for i in index_station_nan:
        station_depl_code = data['Resource_Code'][i][0:3]          # find station_Code
        data['DeployedFromStation_Code'][i] = station_depl_code    # replace Station_code NaN with the correct one
        data['DeployedFromLocation'][i] = 'Home Station'           # fill Deployed from location for consistency
        # find Station_Name and fill DeployedFromStation_Name with correct value
        station_depl_name = list(station_list[station_list['Station_code'] == station_depl_code]['Station_name'])[0]
        data['DeployedFromStation_Name'][i] = station_depl_name
    
    return data


def missing_deployed_from_location(data):
    '''
    Fill missing values in DeployedFromLocation 
    '''

    # index of concerned records
    index_deployed_nan = list(data[data['DeployedFromLocation'].isna()].index)

    # loop to fill DeployedFromLocation
    for i in index_deployed_nan:
        if data['DeployedFromStation_Code'][i] == data['Resource_Code'][i][0:3]:
            data['DeployedFromLocation'][i] = "Home Station"
        else:
            data['DeployedFromLocation'][i] = "Other Station"

        return data


def missing_special_service(data):
    '''
    Fill missing values in SpecialServiceType for 'Use of Special Operations Room' modality
    Other values are not Special Service => replace NaN by "Not Special Service"
    '''
    
    # find and correct 'Use of Special Operations Room' records
    index_serv_type_nan = list(data[data['StopCodeDescription'] == "Use of Special Operations Room"].index)
    for i in index_serv_type_nan:
        data['SpecialServiceType'][i] = "Use of Special Operations Room"

    # Other NaNs to be replaced by "Not Special Service"
    data['SpecialServiceType'] = data['SpecialServiceType'].fillna("Not Special Service")

    return data


def missing_delay_description(data):
    '''
    NaN in DelayCode_Description correspond to pumps showing no delay
    => Replace NaN by "No delay"
    '''
    
    data['DelayCode_Description'] = data['DelayCode_Description'].fillna("No delay")

    return data


def format_rename_columns(data):
    '''
    Change columns formats and names
    '''

    # rename columns
    col_rename = {'Lat' : 'Latitude',
                  'Lon' : 'Longitude'}
    data = data.rename(col_rename, axis = 1)

    # DateOfCall format
    # intermediary dataframe for next steps (keeping initial values for DateOfCall & TimeOfCall)
    df_date_call = pd.DataFrame()
    df_date_call['DateOfCall'] = data['DateOfCall']
    df_date_call['TimeOfCall'] = data['TimeOfCall']
    # split DateOfCall (dd mm yyyy)
    df_date_call['day'] = data['DateOfCall'].apply(lambda x: x[:2]).astype(int)
    df_date_call['month'] = data['DateOfCall'].apply(lambda x: x[3:6])
    df_date_call['year'] = data['DateOfCall'].apply(lambda x: x[-4:]).astype(int)
    # convert months in numbers instead of text (3 letters)
    repl = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec']
    val = range(1,13)
    df_date_call['month'] = df_date_call['month'].replace(to_replace = repl, value=val).astype(int)
    # calculate new DateOfCall @ datetime format + copy to dataset
    df_date_call['date'] = pd.to_datetime((df_date_call['month'].astype(str)+'-'
                                            +df_date_call['day'].astype(str)+'-'
                                            +df_date_call['year'].astype(str)+' '
                                            +df_date_call['TimeOfCall'].astype(str)))
    data['DateOfCall'] = df_date_call['date']

    # other columns format
    col_format = {'TurnoutTimeSeconds' : 'int',
                  'TravelTimeSeconds' : 'int',
                  'CalYear_y' : 'int',
                  'HourOfCall_y' : 'int',
                  'NumStationsWithPumpsAttending' : 'int',
                  'NumPumpsAttending' : 'int',
                  'PumpCount' : 'int',
                  }
    data = data.astype(col_format)

    return data


# def n_pump(pump_per_inc, incident):
#     '''
#     returns the number of pumps attending an incident
#     '''
#     return pump_per_inc.loc[incident]['nb_pump']


def num_pumps_attending(data):
    '''
    Calculate how many pumps attending to the incident
    (variable that exists, but too many inconsistencies)
    '''

    # counting number of pumps per IncidentNumber
    pump_per_inc = data.groupby(by='IncidentNumber').agg({'PumpOrder' : 'count'}).rename({'PumpOrder' : 'nb_pump'}, axis = 1)

    def n_pump(incident):
        '''
        returns the number of pumps attending an incident
        '''
        return pump_per_inc.loc[incident]['nb_pump']

    # intermediary dataframe to keep historical data and store new values
    df_count_pump_values = data[['IncidentNumber', 'NumPumpsAttending', 'PumpCount', 'PumpOrder']]

    # calculate corrected values
    df_count_pump_values['nb_pump_calc'] = df_count_pump_values['IncidentNumber'].apply(n_pump)

    # copy new values to main dataframe ('NumPumpsAttending')
    data['NumPumpsAttending'] = df_count_pump_values['nb_pump_calc']

    # remove 'PumpCount'
    data = data.drop('PumpCount', axis = 1)

    return data


def num_stations_pump_attending(data):
    '''
    Calculate how many stations have pumps attending an incident
    '''
    
    # intermediary dataframe : count nb of stations who have pumps attending an incident
    num_station_attending = data[['IncidentNumber', 'Resource_Code']]
    num_station_attending['Resource_Code'] = num_station_attending['Resource_Code'].apply(lambda x: x[0:3])
    num_station_attending = num_station_attending.groupby(by='IncidentNumber').agg({'Resource_Code' : 'nunique'}).rename({'Resource_Code' : 'num_stations_attending'}, axis = 1)

    def n_stations(incident):
        '''
        returns nb of stations with pump attending to an incident
        '''
        return num_station_attending.loc[incident]['num_stations_attending']

    # keep historical data and store calculation
    df_count_stations_pump = data[['IncidentNumber', 'NumStationsWithPumpsAttending']]

    # calculate nb of stations with pumps attending and copy results to 'NumStationsWithPumpsAttending' variable
    df_count_stations_pump['num_stations_attending_calc'] = df_count_stations_pump['IncidentNumber'].apply(n_stations)
    data['NumStationsWithPumpsAttending'] = df_count_stations_pump['num_stations_attending_calc']

    return data


def missing_date_and_time_left(data):
    '''
    Fill DateAndTimeLeft variable when mmissing, with some estimates
    '''
    # index of concerned records
    index_time_left_corr = list(data[data['DateAndTimeLeft'].isna()].index)

    # Copy some data in an intermediary dataframe
    df_date_left = data[data['DateAndTimeLeft'].isna()][['IncidentNumber', 'IncidentGroup', 'SpecialServiceType', 'DateAndTimeLeft', 'DateAndTimeArrived', 'NumPumpsAttending']]

    #### build table for average time spent on incident, by incident type and nb of pumps attending
    # get all lignes where DateAndTimeLeft is not NaN
    df_time_left = data[data['DateAndTimeLeft'].notna()][['IncidentNumber', 'IncidentGroup', 'SpecialServiceType', 'DateAndTimeLeft', 'DateAndTimeArrived', 'NumPumpsAttending']]
    # calculate time on site
    df_time_left['SecondsOnSite'] = (df_time_left['DateAndTimeLeft'] - df_time_left['DateAndTimeArrived']).dt.total_seconds()
    # calculate average time on site, by incident type and Special service type
    df_time_left_mean = df_time_left.groupby(by = ['IncidentGroup', 'SpecialServiceType', 'NumPumpsAttending']).agg({'SecondsOnSite' : 'mean'}).round(0).reset_index().rename({'SecondsOnSite' : 'time_left_mean'}, axis = 1)

    # create new variable to store estimated time on site
    df_date_left['SecondsOnSite_estimated'] = np.nan

    # loop to fill "SecondsOnSite_estimated" variable
    for i in index_time_left_corr:
       look_inc = data['IncidentGroup'][i]
       look_sstype = data['SpecialServiceType'][i]
       look_n_pumps = data['NumPumpsAttending'][i]
       df_date_left['SecondsOnSite_estimated'][i] = df_time_left_mean[(df_time_left_mean['IncidentGroup'] == look_inc) &
                                                                      (df_time_left_mean['SpecialServiceType'] == look_sstype) &
                                                                      (df_time_left_mean['NumPumpsAttending'] == look_n_pumps)]['time_left_mean']

    # Calculate DateAndTimeLeft estimated and copy it to main dataset
    df_date_left['DateAndTimeLeft'] = pd.to_datetime(df_date_left['DateAndTimeArrived']) + pd.to_timedelta(df_date_left['SecondsOnSite_estimated'], unit = 's')
    for i in index_time_left_corr:
       data['DateAndTimeLeft'][i] = df_date_left['DateAndTimeLeft'][i]

    return data


def remove_dartford(data):
    '''
    Remove Dartford station from dataset (not in London Fire Brigade)
    '''

    # incidents where Dartford is attending
    dartford_incident = list(data[data['DeployedFromStation_Name'] == 'Dartford']['IncidentNumber'])[0]
    
    # removing incidents
    data = data[data['IncidentNumber'] != dartford_incident]

    return data

def create_mobilised_rank(data):
    '''
    calculate a "rank" for each mobilisation time to identify for each pump, from which mobilisation wave they were.
    '''
    
    ## Création d'un tableau visant à lister les DateAndTimeMobilised uniques, de chaque incident
    # afin de leur attribuer un rang + compte des véhicules appelés (1ère vague de mobilisation, seconde, etc...)
    # exécution 6 minutes...

    # create new table (make a list of all unique DateAndTimeMobilised by incident)
    df_mob_rank = data[['IncidentNumber', 'DateAndTimeMobilised', 'AttendanceTimeSeconds']].groupby(by=['IncidentNumber', 'DateAndTimeMobilised']).count().reset_index()
    df_mob_rank = df_mob_rank.sort_values(by = ['IncidentNumber', 'DateAndTimeMobilised'])
    df_mob_rank = df_mob_rank.rename({'AttendanceTimeSeconds' : 'Nb_pumps_asked'}, axis = 1)

    # create a variable to identify the rank (default value = 1)
    df_mob_rank['Mobilised_Rank'] = 1

    # calculate the rank for each DateAndTimeMobilised
    for i in range(1,df_mob_rank.shape[0]):
        if df_mob_rank['IncidentNumber'].loc[i] != df_mob_rank['IncidentNumber'].loc[i-1]:
            df_mob_rank['Mobilised_Rank'].loc[i] = 1
        else:
            df_mob_rank['Mobilised_Rank'].loc[i] = df_mob_rank['Mobilised_Rank'].loc[i-1]+1

    # define multi-index (incident number + mobilisation data/time)
    df_mob_rank = df_mob_rank.set_index(['IncidentNumber', 'DateAndTimeMobilised'])

    ## create new column in main dataframe with the results
    data['Mobilised_Rank'] = 0
    # loop to get rank from rank table
    for i in data.index:
        # incident index in rank table
        inc_no = data['IncidentNumber'].loc[i]
        # DateAndTimeMobilised index in rank table
        mob_time = data['DateAndTimeMobilised'].loc[i]
        # copying rank found
        data['Mobilised_Rank'][i] = df_mob_rank['Mobilised_Rank'].loc[inc_no, mob_time]

    return data


def incident_type_category(data):
    '''
    defining 5 major types of incidents and removing old variables ('IncidentGroup','StopCodeDescription', 'SpecialServiceType')
    '''

    # creating 'IncidentType' variable (5 major types of incidents)
    # Type d'Incident : Fire / Major Environmental Disasters / Domestic Incidents / Local Emergencies / Prior rrangements

    data['IncidentType'] = data['IncidentGroup']
    data['IncidentType'] = np.where(data['IncidentType'] == "False Alarm", data['StopCodeDescription'], data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "Special Service", data['SpecialServiceType'], data['IncidentType'])

    # Fire
    data['IncidentType'] = np.where(data['IncidentType'] == "False alarm - Good intent", "Fire", data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "False alarm - Malicious", "Fire", data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "AFA", "Fire", data['IncidentType'])

    #  major environmental disasters e.g. flooding, hazardous material incidents or spills and leaks
    data['IncidentType'] = np.where((data['IncidentType'] == "Flooding") |
                            (data['IncidentType'] == "Hazardous Materials incident") |
                            (data['IncidentType'] == "Spills and Leaks (not RTC)"),
                            "Major Environmental Disasters", data['IncidentType'])

    #  domestic incidents e.g. persons locked in/out, lift releases, suicide/attempts
    data['IncidentType'] = np.where((data['IncidentType'] == "Suicide/attempts") |
                            (data['IncidentType'] == "Effecting entry/exit") |
                            (data['IncidentType'] == "Lift Release"),
                            "Domestic Incidents", data['IncidentType'])

    # local emergencies e.g. road traffic incidents, responding to medical emergencies,
    # rescue of persons and/or animals or making areas safe
    data['IncidentType'] = np.where((data['IncidentType'] == "Animal assistance incidents") | 
                            (data['IncidentType'] == "Medical Incident") | 
                            (data['IncidentType'] == "Removal of objects from people") |
                            (data['IncidentType'] == "Other rescue/release of persons") |
                            (data['IncidentType'] == "RTC")|
                            (data['IncidentType'] == "Other Transport incident") |
                            (data['IncidentType'] == "Evacuation (no fire)") |
                            (data['IncidentType'] == "Rescue or evacuation from water") |
                            (data['IncidentType'] == "Water Provision") |
                            (data['IncidentType'] == "Medical Incident - Co-responder") |
                            (data['IncidentType'] == "Making Safe (not RTC)") |
                            (data['IncidentType'] == "Water provision"),
                            "Local Emergencies", data['IncidentType'])

    #  prior arrangements to attend or assist other agencies, which may include 
    # some provision of advice or standing by to tackle emergency situations
    data['IncidentType'] = np.where((data['IncidentType'] == "Advice Only") |
                            (data['IncidentType'] == "No action (not false alarm)") |
                            (data['IncidentType'] == "Assist other agencies") |
                            (data['IncidentType'] == "Stand By"),
                            "Prior Arrangement", data['IncidentType'])

    # create a column gathering all sub categories : "IncidentCategory" (gathering "StopCodeDescription" & "SpecialServiceType")
    data['IncidentCategory'] = data['IncidentGroup']
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "Fire", data['StopCodeDescription'], data['IncidentCategory'])
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "False Alarm", data['StopCodeDescription'], data['IncidentCategory'])
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "Special Service", data['SpecialServiceType'], data['IncidentCategory'])

    # create a False Alarm column (0/1)
    data['FalseAlarm']= data['IncidentGroup']
    data['FalseAlarm'] = data['FalseAlarm'].replace(to_replace = ["Special Service", "Fire"], value = 0)
    data['FalseAlarm'] = data['FalseAlarm'].replace(to_replace = ["False Alarm"], value = 1)
    
    # remove useless columns "IncidentGroup","StopCodeDescription", "SpecialServiceType"
    data=data.drop(['IncidentGroup','StopCodeDescription', 'SpecialServiceType'], axis = 1)
    
    return data


def distance(lat1,lon1,lat2,lon2):
    '''
    calculate euclidean distance between 2 points, from their latitude & longitude
    '''

    R = 6371e3
    φ1 = lat1 * np.pi/180
    φ2 = lat2 * np.pi/180
    Δφ = (lat2-lat1) * np.pi/180
    Δλ = (lon2-lon1) * np.pi/180
    a =np.sin(Δφ/2) * np.sin(Δφ/2) +np.cos(φ1) * np.cos(φ2) *np.sin(Δλ/2) * np.sin(Δλ/2);
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a));
    d = R * c

    return round(d/1000,3)


def distance_calc(data, station_pos):
    '''
    Calculate euclidean distance in km, between the incident and the pump's home station 
    '''

    # get station latitude and longitude
    station_pos=station_pos.rename(columns={'Station_Code':'DeployedFromStation_Code'})
    data=data.merge(right=station_pos,on='DeployedFromStation_Code')
    data.drop('Station_Name',axis=1,inplace=True)

    # create distance variable
    data['Distance']=distance(data.Latitude,data.Longitude,data.Station_Latitude,data.Station_Longitude)
    
    # remove GPS data no longer needed
    data.drop(['Longitude','Latitude','Station_Latitude','Station_Longitude'],1,inplace=True)

    return data


def total_pumps_out(data):
    '''
    Estimates how many pumps are currently still in operations at the time of the mobilisation request
    '''

    # sort data based on mobilisation data/time
    data=data.sort_values(by = 'DateAndTimeMobilised')
    data.reset_index(drop=True, inplace=True)

    # calculate how many pumps are out at the time of mobilisation
    data['TotalOfPumpInLondon_Out']=0
    for i in range (300,len(data)):
        prev_pump = data.loc[i-298:i-1]
        data['TotalOfPumpInLondon_Out'][i] = len(prev_pump[prev_pump['DateAndTimeLeft'] > data['DateAndTimeMobilised'][i]])

    return data


def pumps_available(data):
    '''
    Estimates how many pumps are available in the station the incident location depends on
    '''

    # create a table showing all mobilisations by pump (ressource code) and by station (Deployed From Location), only based on Home Station incidents
    camion = data[data['DeployedFromLocation']=="Home Station"].groupby(['DeployedFromStation_Name','DeployedFromLocation','Resource_Code']).size().reset_index()
    camion=pd.DataFrame(camion)

    # estimating nb of pumps per station (1 or 2)
    camion2=camion.groupby(['DeployedFromStation_Name'])['DeployedFromLocation'].size()
    camion2=pd.DataFrame(camion2)
    camion2 = camion2.reset_index()
    camion2.reset_index()
    camion2.rename(columns={'DeployedFromLocation': 'PumpByStation','DeployedFromStation_Name' : 'IncidentStationGround' }, inplace=True)

    # merging with the main dataframe
    data=data.merge(camion2, how = 'left', on = 'IncidentStationGround')

    # show in main dataframe the pumps' station codes
    data['Station_Code_of_ressource']=data['Resource_Code'].astype(str).str[0:3]

    code_station = data.groupby(['DeployedFromStation_Name','DeployedFromStation_Code']).size().reset_index()
    code_station=pd.DataFrame(code_station)
    code_station.columns=['IncidentStationGround','IncidentStationGround_Code','test']
    code_station = code_station.drop('test', axis = 1)

    data=data.merge(code_station, how = 'left', on = 'IncidentStationGround')

    # calculate how many pumps from the station are currently out 
    data['PumpOfIncidentStation_Out']=0
    for i in range (300,len(data)):
        available = data.loc[i-298:i-1]
        data['PumpOfIncidentStation_Out'][i] = len(
            available[
                (data['IncidentStationGround_Code'][i] == available['Station_Code_of_ressource'])
                &
                (data['DateAndTimeMobilised'][i] < available['DateAndTimeLeft'])
            ])


    # calculate how many pumps from the station are currently available
    data['PumpAvailable']=data['PumpByStation']-data['PumpOfIncidentStation_Out']

    # replace negativ numbers by zero
    data['PumpAvailable'] = data['PumpAvailable'].apply(lambda x: x if x>0 else 0)
    # data['PumpAvailable'] = data['PumpAvailable'].replace([-1], 0)

    return data


def rows_delete(data, lines=300):
    '''
    remove incidents from the firt (300 by default) lines
    '''
    
    inc_suppr = data[:lines]['IncidentNumber'].unique().tolist()
    data = data[-data['IncidentNumber'].isin(inc_suppr)]

    return data


def remove_unused(data):
    '''
    remove records and variables that will finally not be used
    '''

    # keep only mobilised rank 1
    data = data[data['Mobilised_Rank'] == 1]
    # remove DateAndTimeLeft
    data = data.drop('DateAndTimeLeft', axis= 1)

    return data


def speed_over_60(data):
    '''
    remove incidents who shows some pumps driving faster than an average of 60 km per hour.
    '''

    # calculate speed in km/h for each pump (temporary variable)
    data['speed_km_per_hour'] = 3600 * data['Distance']/data['TravelTimeSeconds']
    
    # list and remove all incidents with some speeds over 60 km/h
    liste_incidents_60 = data[data['speed_km_per_hour'] > 60]['IncidentNumber'].unique().tolist()
    data = data[-data['IncidentNumber'].isin(liste_incidents_60)]
    
    # remove temporary variable
    data = data.drop('speed_km_per_hour', axis=1)

    return data


def datetime_variables(data):
    '''
    remove / create datetime related variables
    '''

    # Remove all variables linked with Date of Call
    col_remove = ['CalYear_x',
                  'HourOfCall_x',
                  'DateOfCall',
                  'CalYear_y',
                  'TimeOfCall',
                  'HourOfCall_y']
    data = data.drop(col_remove, axis = 1)

    # create date/time variables based on DateAndTimeMobilised
    data['year'] = data['DateAndTimeMobilised'].dt.year
    data['month'] = data['DateAndTimeMobilised'].dt.month
    data['day'] = data['DateAndTimeMobilised'].dt.day
    data['weekday'] = data['DateAndTimeMobilised'].dt.day_name()
    data['hour'] = data['DateAndTimeMobilised'].dt.hour

    # remove useless datetime variables
    data = data.drop('DateAndTimeMobile', axis = 1)
    data = data.drop('DateAndTimeArrived', axis = 1)

    return data


def add_weather(data, weather_file):
    '''
    add weather data to main dataframe
    '''

    # create temporaty date variable in main dataframe
    data['date'] = data['DateAndTimeMobilised'].dt.strftime('%Y-%m-%d %H')

    # read weather
    weather = pd.read_csv(weather_file)

    # wreate date column
    weather['date'] = pd.to_datetime(weather['datetime']).dt.strftime('%Y-%m-%d %H')
    
    # keep useful columns
    keep_columns = ['temp', 'precip', 'cloudcover', 'visibility', 'conditions', 'icon', 'date']
    weather = weather[keep_columns]
    
    # replace NaN values (only precip column concerned => 0)
    weather = weather.fillna(0)

    # merge weather date into main dataframe
    data = data.merge(weather, how= 'left', on= 'date')

    # fill NaN and remove date column
    data = data.fillna(0)
    data = data.drop('date', axis= 1)

    # remove incidents where weather conditions == 0
    list_incidents_null_weather = data[data['conditions'] ==0]['IncidentNumber'].unique().tolist()
    data = data[-data['IncidentNumber'].isin(list_incidents_null_weather)]

    return data


def add_holidays(data, school_holidays_file):
    '''
    add holidays data to main dataframe
    '''

    # convert DateAndTimeMobilised format
    data['DateAndTimeMobilised'] = pd.to_datetime(data['DateAndTimeMobilised']).dt.date
    data['DateAndTimeMobilised']=pd.to_datetime(data['DateAndTimeMobilised'])

    # get working day from UK calendar (True/False => 1/0)
    uni=UnitedKingdom()
    data['workingday'] = data['DateAndTimeMobilised'].apply(lambda x : str(int(uni.is_working_day(date(x.year, x.month, x.day)))))

    # get school holidays from external data and merge with main dataframe
    holidays=pd.read_csv(school_holidays_file, sep=';')
    holidays=holidays[['date']]
    holidays.date=pd.to_datetime(holidays.date)
    holidays.rename(columns={'date':'DateAndTimeMobilised'},inplace=True)
    holidays['school_holidays']=1
    data=data.merge(holidays, how = 'left', on = 'DateAndTimeMobilised')
    data.school_holidays=data.school_holidays.fillna(0)
    data.school_holidays=data.school_holidays.astype('object')

    return data


def add_traffic(data, traffic_file):
    '''
    add traffic density to main dataframe
    '''

    # read traffic file
    traffic = pd.read_csv(traffic_file, sep=';')

    # create common column in main dataframe and traffic data (temporary, for further merger)
    traffic['congestion_key'] = traffic['year'].astype(str)+traffic['day']+traffic['hour'].astype(str)
    data['congestion_key'] = data['year'].astype(str)+data['weekday']+data['hour'].astype(str)

    # remove useless columns from traffic, rename, and format change
    traffic = traffic.drop(['year', 'hour', 'day', 'day_nb'], axis=1)
    traffic = traffic.rename({'congestion' : 'congestion_rate'}, axis = 1)
    traffic['congestion_rate'] = traffic['congestion_rate'].str.replace(',', '.').astype(float)

    # merge traffic into main dataframe and remove temporary column
    data = data.merge(right = traffic, how = 'left', on = 'congestion_key')
    data = data.drop('congestion_key', axis = 1)

    return data


# clean data and add features pipeline
inc, mob, station_pos, meteo, holidays, traffic = extract()

inc = convert_gps(data= inc)
mob = create_appliance(data= mob)
lfb = merge_datasets(incidents= inc, mobilisations= mob)
df = remove_variables(lfb)
df = missing_date_of_call(df)
df = convert_date_and_time(df)
df = missing_tournout_time_seconds(df)
df = missing_travel_time(df)
df = missing_deployed_from_station(df)
df = missing_deployed_from_location(df)
df = missing_special_service(df)
df = missing_delay_description(df)
df = format_rename_columns(df)
df = num_pumps_attending(df)
df = num_stations_pump_attending(df)
df = missing_date_and_time_left(df)
df = remove_dartford(df)
df = create_mobilised_rank(df)
df = incident_type_category(df)
df = distance_calc(data= df, station_pos= station_pos)
df = total_pumps_out(df)
df = pumps_available(df)
df = rows_delete(df)
df = remove_unused(df)
df = speed_over_60(df)
df = datetime_variables(df)
df = add_weather(df, weather_file)
df = add_holidays(df, school_holidays_file)
df = add_traffic(df, traffic_file)

# save df to pkl
df.to_pickle("../data/base_ml.pkl")