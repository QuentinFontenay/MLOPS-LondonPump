import pandas as pd


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
    remove incidents from the first (300 by default) lines
    '''
    
    inc_suppr = data[:lines]['IncidentNumber'].unique().tolist()
    data = data[-data['IncidentNumber'].isin(inc_suppr)]

    return data

