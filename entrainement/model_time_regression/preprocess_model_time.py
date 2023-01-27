from sklearn.preprocessing import StandardScaler
import pandas as pd

def remove_datetime_var(data):
    '''
    remove datetime variables from dataset
    '''

    data = data.drop(data.select_dtypes("datetime").columns, axis = 1)
    
    return data


def remove_variables(data):
    '''
    keep only 20 variables used for the model (19 features + 1 target)
    '''

    data = data[
        ['AttendanceTimeSeconds', 'DeployedFromLocation', 'Appliance', 'PropertyCategory',
         'AddressQualifier', 'IncidentType', 'Distance', 'TotalOfPumpInLondon_Out',
         'Station_Code_of_ressource', 'IncidentStationGround_Code', 'PumpAvailable',
         'month', 'temp', 'precip', 'cloudcover', 'visibility','conditions',
         'workingday', 'school_holidays', 'congestion_rate'
        ]
    ]

    return data


def reg_var_type(data):
    '''
    Correction of data type for 4 variables
    so they can be properly used by ML model
        PumpAvailable, month, workingday, school_holidays
    '''

    # convert 'PumpAvailable' (considered as categorical) to string
    data['PumpAvailable'] = data['PumpAvailable'].astype(str)
    
    # convert 'month' to integer
    data['month'] = data['month'].astype('uint8')
    
    # convert 'workingday' and 'school_holidays' to integer (binary variables : 0/1)
    data['workingday'] = data['workingday'].astype('uint8')
    data['school_holidays'] = data['school_holidays'].astype('uint8')    

    return data


def target_features(data):
    '''
    split target (AttendanceTimeSeconds) and features

    returns : target, features
    '''

    target = data['AttendanceTimeSeconds']
    features = data.drop('AttendanceTimeSeconds', axis = 1)

    return target, features


def features_dummies(features):
    '''
    apply get_dummies to 'object' type variables
    '''
    features = pd.get_dummies(features)

    return features


def normalize_numerical(X_train, X_test):
    '''
    normalize numerical features, and save scaler to apply to new data

    input : X_train, X_test
    output : X_train_scaled, X_test_scaled, StandardScaler fitted on X_train
    '''

    # numerical variables
    # (should be : # distance, TotalOfPumpInLondon_Out, temp, precip, cloudcover, visibility, congestion_rate)
    num_var = list(X_train.select_dtypes(include = ['int64', 'float']).columns) # only int64 (we keep uint8 : binary features + months)

    # Create StandardScaler Object
    scaler_df = StandardScaler()

    # Fit scaler to X_train
    scaler_df.fit(X_train[num_var])

    # Apply scaler to train and test set
    X_train[num_var] = scaler_df.transform(X_train[num_var])
    X_test[num_var] = scaler_df.transform(X_test[num_var])

    return X_train, X_test, scaler_df
