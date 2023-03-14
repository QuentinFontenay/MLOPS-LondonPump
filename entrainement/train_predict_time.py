from joblib import dump, load
from cleaning_data import cleaned_data
from training.train_test import train_test_split_index, train_test_split_incident
from training.preprocess_model_time import remove_datetime_var, remove_variables, reg_var_type, \
    target_features, features_dummies, normalize_numerical
from training.top_stations_over_600 import top_station_600
from training.training_model_time import training_model, pred_scores_model
from utils.helpers import path_file
from utils.mongodb import connect_to_mongo
import pandas as pd
from datetime import datetime
import os

# get dataset
df = cleaned_data()

# keep copy of full dataset
df_full = df.copy()

# preprocessing
tts_index_test, tts_index_train = train_test_split_index(df, test_size=0.2)
df = remove_datetime_var(df)
df = remove_variables(df)
df = reg_var_type(df)
target, features = target_features(df)
features = features_dummies(features)
X_train, X_test, y_train, y_test = train_test_split_incident(target, features, tts_index_test, tts_index_train)
X_train, X_test, scaler_features = normalize_numerical(X_train, X_test)
topslowest, topslowest_code = top_station_600(df_full, X_train)
db = connect_to_mongo()
stations = list(db.stations.find({}, { "code": 1, "name": 1, "_id": 0 }))
stations = [station for station in stations if station['code'] in topslowest_code]
risk_stations = { "created_at": datetime.utcnow(), "stations": stations }
db.riskStations.insert_one(risk_stations)
# train and evaluate the model
best_param_C, mae_train, mae_test = training_model(X_train, y_train, X_test, y_test)
model, pred_train, pred_test, metrics = pred_scores_model(best_param_C, X_train, y_train, X_test, y_test)


# model trained ID : aaaammjjhhmmss
model_train_time = str(datetime.now())[:-7].replace('-', '').replace(' ','').replace(':', '')

# save 'Mean AE test' to scores file
scores = load(path_file() + '/archives/scores_models_mae.pkl')
scores[model_train_time] = metrics['Mean AE test']
dump(scores, path_file() + '/archives/scores_models_mae.pkl')

# ensure 'last_run' is empty before saving last training files
for file in os.listdir(path_file() + '/last_run/'):
    os.remove(path_file() + '/last_run/' + file)

# save last training files (model + usEful files) to last_run directory
last_run_path = path_file() + '/last_run/' + model_train_time + '_'                                         # location + datehour_ at the beginning of the file saved
dump(model, last_run_path + 'PassiveAggressiveRegressor_mlops.joblib')                                      # modele
dump(scaler_features, last_run_path + 'reg_scaler.pkl')                                                     # standard scaler
dump(list(df.drop('AttendanceTimeSeconds', axis = 1)), last_run_path + 'reg_df_columns.pkl')                # column list
dump(dict(df.drop('AttendanceTimeSeconds', axis=1).dtypes), last_run_path + 'reg_df_columns_format.pkl')    # columns format
dump(features.columns, last_run_path + 'reg_data_dummies_columns.pkl')                                      # features columns after get_dummies
