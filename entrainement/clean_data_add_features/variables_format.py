import pandas as pd


def remove_variables(data):
    '''
    Keep only useful variables
    '''

    keep_columns = [
        'IncidentNumber',
        'CalYear_x',
        'HourOfCall_x',
        'Resource_Code',
        'DateAndTimeMobilised',
        'DateAndTimeMobile',
        'DateAndTimeArrived',
        'TurnoutTimeSeconds',
        'TravelTimeSeconds',
        'AttendanceTimeSeconds',
        'DateAndTimeLeft',
        'DeployedFromStation_Code',
        'DeployedFromStation_Name',
        'DeployedFromLocation',
        'PumpOrder',
        'DelayCode_Description',
        'Appliance',
        'DateOfCall',
        'CalYear_y',
        'TimeOfCall',
        'HourOfCall_y',
        'IncidentGroup',
        'StopCodeDescription',
        'SpecialServiceType',
        'PropertyCategory',
        'PropertyType',
        'AddressQualifier',
        'IncidentStationGround',
        'NumStationsWithPumpsAttending',
        'NumPumpsAttending',
        'PumpCount',
        'Lat',
        'Lon'
    ]

    data = data[keep_columns]

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

