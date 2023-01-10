import pandas as pd

# initial data location (if main clean file in /entrainement/clean_data_add_features/)
# data_loc = "../../data/"

# initial data location (if main clean file in /entrainement/)
data_loc = "../data/"

# original files => see later how (database / scrap)
incidents_file = data_loc + 'LFB Incident data Last 3 years'
mobilisations_file = data_loc + 'LFB Mobilisation data Last 3 years'
stations_file = data_loc + 'pos station.csv'                                # only once (no change except if new stations built)
school_holidays_file = data_loc + 'holidays.csv'                            # to be updated when new calendar available
weather_file = data_loc + 'Weather London.csv'                              # to be updated (get past month data, once a month ?)
traffic_file = data_loc + 'london_congestion.csv'  


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


def merge_datasets(incidents, mobilisations):
    '''
    Merge incidents datasets and mobilisations dataset
    '''

    data = mobilisations.merge(right = incidents, on = 'IncidentNumber', how = 'left')

    return data

