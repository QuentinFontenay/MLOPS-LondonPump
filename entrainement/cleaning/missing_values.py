import pandas as pd
import numpy as np


def missing_date_of_call(data):
    '''
    Remove incidents that do not have any Date of call
    '''

    inc_nan_list = list(data[data['DateOfCall'].isna()]['IncidentNumber'].unique())

    if inc_nan_list:
        data = data.drop(axis=0, index=data[data['IncidentNumber'].isin(inc_nan_list)].index)
    
    return data


def missing_tournout_time_seconds(data):
    '''
    Estimates missing TurnoutTimeSeconds
    With average % usually noticed (in average, Turnout times represents xx % from AttendanceTime)
    '''

    # list of index where TurnoutTimeSeconds is NaN
    index_mobile_nan = list(data[data['DateAndTimeMobile'].isna()].index)

    if index_mobile_nan:

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
    
    # delete incidents still showing some NaN in TurnoutTimeSeconds
    inc_turnout_missing = list(data[data['TurnoutTimeSeconds'].isna()]['IncidentNumber'])
    if inc_turnout_missing:
        data = data[-data['IncidentNumber'].isin(inc_turnout_missing)]

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

    if index_travel_nan_gt_arrived:
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

    # delete incidents still showing some NaN in TravelTimeSeconds
    inc_traveltime_missing = list(data[data['TravelTimeSeconds'].isna()]['IncidentNumber'])
    if inc_traveltime_missing:
        data = data[-data['IncidentNumber'].isin(inc_traveltime_missing)]

    return data


def missing_deployed_from_station(data):
    '''
    Fill missing values in DeployedFromStation_Code and Name
    '''
        
    # index of records concerned
    index_station_nan = list(data[data['DeployedFromStation_Code'].isna()].index)

    if index_station_nan:

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

    if index_deployed_nan:

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
    
    if index_serv_type_nan:
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


def missing_date_and_time_left(data):
    '''
    Fill DateAndTimeLeft variable when mmissing, with some estimates
    '''
    # index of concerned records
    index_time_left_corr = list(data[data['DateAndTimeLeft'].isna()].index)

    if index_time_left_corr:

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

