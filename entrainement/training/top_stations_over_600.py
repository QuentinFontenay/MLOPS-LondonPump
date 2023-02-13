import pandas as pd
from scipy import stats

def top_station_600(data, X_train):
    '''
    Generate list of top stations (from train set) that show the highest density of attendance time over 600 seconds
    so these station are added to a 'warning list' showing a risk of attendance time predicted by the model
    to be under evaluated.

    Input :
        data    : full dataset (raw data, features and target)
        X_train : X_train (features) that will be used to get indexes

    Output :
        topslowest      : stations names list
        topslowest_code : stations codes list
    '''

    # build a full train set with raw data (no standardization or get gummies applied) (features + target)
    train_full = data.loc[X_train.index]
    
    # Create a table of stations
    station_list = train_full.groupby(by = ['DeployedFromStation_Code', 'DeployedFromStation_Name']).count().reset_index()[['DeployedFromStation_Code', 'DeployedFromStation_Name']]
    station_list = station_list.rename({'DeployedFromStation_Code' : 'Station_code', 'DeployedFromStation_Name' : 'Station_name'}, axis = 1)
    # print(station_list.duplicated().sum(), 'doublons dans la table des stations') # for testing !!

    # probability density for attendance times between 600 and 1600 seconds

    # variable initialization
    kde_stations_over_600 = pd.DataFrame()
    kde600_stations = []
    kde600_values = []
    density_threshold = 0.1        # if density >= threshold, then the station must be in this 'warning' list

    # for each station, calculate probability density to have attendance time in range [600,1600]
    for station in train_full['DeployedFromStation_Name'].unique().tolist():                                                # for each station
        data_kde = train_full[train_full['DeployedFromStation_Name'] == station]['AttendanceTimeSeconds'].astype("double")  # create attendance time table
        kde = stats.gaussian_kde(data_kde)              # Kernel density estimation = probability density function estimation
        kde_sum = kde.integrate_box_1d(600,1600)        # density between [600, 1600]
        kde600_values.append(kde_sum)                   # store calculated density
        kde600_stations.append(station)                 # store station name

    # gather the results (data for all stations) in a dataframe
    kde_stations_over_600['station'] = kde600_stations
    kde_stations_over_600['pct_over_600'] = kde600_values

    # keep only top stations (density percentage >= threshold defined above)
    top_over_600 = kde_stations_over_600[kde_stations_over_600['pct_over_600'] >= density_threshold].sort_values('pct_over_600', ascending=False)


    # create lists of stations (names list and codes list)
    topslowest = top_over_600['station'].to_list()
    topslowest_code = topslowest.copy()
    topslowest_code = station_list[station_list['Station_name'].isin(topslowest)]['Station_code'].to_list()

    return topslowest, topslowest_code
