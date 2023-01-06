import numpy as np
from convertbng.cutil import convert_lonlat     # to convert gps data


def convert_gps(data):
    '''
    Convert GPS data from incidents dataframe from OSGB 1936 (British National Grid) to WGS 84
    '''

    gps_conv = convert_lonlat(data['Easting_rounded'].to_list(), data['Northing_rounded'].to_list())
    
    # create new columns for GPS converted
    data['Lat'] = gps_conv[1]
    data['Lon'] = gps_conv[0]

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

