import numpy as np
import pyproj

def convert_gps(data):
    '''
    Convert GPS data from incidents dataframe from OSGB 1936 (British National Grid) to WGS 84
    '''
    transformer = pyproj.Transformer.from_crs("epsg:27700", "epsg:4326")
    for index, row in data.iterrows():
        data.loc[index,'Lat'], data.loc[index,'Lon'] = transformer.transform(row['Easting_rounded'], row['Northing_rounded'])

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

