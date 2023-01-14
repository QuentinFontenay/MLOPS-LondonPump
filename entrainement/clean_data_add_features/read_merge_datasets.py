import pandas as pd
import os

# initial data location (if main clean file in /entrainement/clean_data_add_features/)
# data_loc = "../../data/"

# initial data location (if main clean file in /entrainement/)
data_loc = "../data/"

# original files => see later how (database / scrap)
incidents_file = 'LFB Incident data Last 3 years'
mobilisations_file = 'LFB Mobilisation data Last 3 years'
stations_file = 'pos station.csv'                                # only once (no change except if new stations built)
school_holidays_file = 'holidays.csv'                            # to be updated when new calendar available
weather_file = 'Weather London.csv'                              # to be updated (get past month data, once a month ?)
traffic_file = 'london_congestion.csv'


def extract(path_to_data = data_loc):
    '''
    read data from original data folder (../data by default)
    '''
    
    # convert xlsx datasets to csv (xlsx from https://data.london.gov.uk/)
    # Xlsx2csv(incidents_file+'.xlsx').convert((incidents_file+'.csv'))
    # Xlsx2csv(mobilisations_file+'.xlsx').convert((mobilisations_file+'.csv'))
    
    # create dataframes from csv
    inc = pd.read_csv(os.path.join(data_loc, incidents_file+'.csv'))
    mob = pd.read_csv(os.path.join(data_loc, mobilisations_file+'.csv'))

    # create dataframes for other files
    station_pos=pd.read_csv(os.path.join(data_loc, stations_file))
    meteo = pd.read_csv(os.path.join(data_loc, weather_file))
    holidays=pd.read_csv(os.path.join(data_loc, school_holidays_file), sep=';')
    traffic = pd.read_csv(os.path.join(data_loc, traffic_file), sep=';')

    return inc, mob, station_pos, meteo, holidays, traffic


def merge_datasets(incidents, mobilisations):
    '''
    Merge incidents datasets and mobilisations dataset
    '''

    data = mobilisations.merge(right = incidents, on = 'IncidentNumber', how = 'left')

    return data