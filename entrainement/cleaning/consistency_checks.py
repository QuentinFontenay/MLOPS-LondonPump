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

