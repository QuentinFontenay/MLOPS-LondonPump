import pandas as pd
from workalendar.europe.united_kingdom import UnitedKingdom
from datetime import date


def add_weather(data, weather):
    '''
    add weather data to main dataframe
    '''

    # create temporaty date variable in main dataframe
    data['date'] = data['DateAndTimeMobilised'].dt.strftime('%Y-%m-%d %H')

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


def add_holidays(data, holidays):
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
    holidays=holidays[['date']]
    holidays.date=pd.to_datetime(holidays.date)
    holidays.rename(columns={'date':'DateAndTimeMobilised'},inplace=True)
    holidays['school_holidays']=1
    data=data.merge(holidays, how = 'left', on = 'DateAndTimeMobilised')
    data.school_holidays=data.school_holidays.fillna(0)
    data.school_holidays=data.school_holidays.astype('object')

    return data


def add_traffic(data, traffic):
    '''
    add traffic density to main dataframe
    '''

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

