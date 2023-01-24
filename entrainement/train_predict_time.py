
from clean_data_add_features_main import cleaned_data
from model_time_regression.train_test import train_test_split_index, train_test_split_incident
from model_time_regression.preprocess_model_time import remove_datetime_var, remove_variables, reg_var_type, \
    target_features, features_dummies, normalize_numerical
from model_time_regression.top_stations_over_600 import top_station_600
from model_time_regression.training_model_time import training_model, pred_scores_model

# get dataset
df = cleaned_data()

# import pandas as pd                           # pour tests seulement (récupérer fichiel en local)
# df = pd.read_pickle('../data/base_ml.pkl')

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

# train and evaluate the model
best_param_C, mae_train, mae_test = training_model(X_train, y_train, X_test, y_test)
model, pred_train, pred_test, metrics = pred_scores_model(best_param_C, X_train, y_train, X_test, y_test)

# # save files and model                    # pour tests en local uniquement
# from joblib import dump
# import pickle
# save_location = '../data/train_saves/'
# dump(model, save_location + 'model_reg_attendance_time.joblib')                                             # modele
# dump(scaler_features, save_location + 'reg_scaler.pkl')                                                     # standard scaler
# dump(list(df.drop('AttendanceTimeSeconds', axis = 1)), save_location + 'reg_df_columns.pkl')                # column list
# dump(dict(df.drop('AttendanceTimeSeconds', axis=1).dtypes), save_location + 'reg_df_columns_format.pkl')    # columns format
# dump(features.columns, save_location + 'reg_data_dummies_columns.pkl')                                      # features columns after get_dummies
# pd.DataFrame(topslowest_code).to_csv(save_location + 'topslowest_code.csv', sep=',', index=False)           # stations list (highest attendance time)
# with open(save_location + 'reg_scores.pkl', 'wb') as f:                                                     # metrics for the model
#     pickle.dump(metrics, f)
# # with open(save_location + 'reg_scores.pkl', 'rb') as f:
# #     metrics_restore = pickle.load(f)