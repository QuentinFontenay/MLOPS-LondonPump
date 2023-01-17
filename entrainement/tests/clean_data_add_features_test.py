import os
import sys

# définir où trouver le package 'clean_data_add_features' (utilisé pour les fixtures)
# dans "/entrainement/clean_data_add_features/"
sys.path.append(os.path.split(os.getcwd())[0]+"/clean_data_add_features/")



# importer toutes les fixtures du test
from clean_data_add_features_test_fixtures import *


# Contrôle préalable : vérifier taille inc = 9441 incidents et taille mob = 13951 véhicules
def test_datasets_size(inc, mob):
    assert(len(inc) == 9441)
    assert(len(mob) == 13951)


# Etape convert_gps : vérifier que convert_gps a bien créé les colonnes ['Lat'] et ['Lon']
def test_convert_gps(inc_convert_gps):
    assert(('Lat' in inc_convert_gps.columns) == True)
    assert(('Lon' in inc_convert_gps.columns) == True)


# Etape create_appliance : vérifier que create_appliance a créé la variable 'Appliance'
def test_create_appliance(mob_create_appliance):
    assert(('Appliance' in mob_create_appliance.columns) == True)


# Etape merge_datasets : vérifier cohérence de taille du df
def test_merge_datasets(lfb, mob_create_appliance, inc_convert_gps):
    # nb enregistrement doit être le même que liste des véhicules (mob)
    assert(lfb.shape[0] == mob_create_appliance.shape[0])
    # nb variables = la somme des 2 tables -1 (variable commune pour la fusion)
    assert(lfb.shape[1] == inc_convert_gps.shape[1] + mob_create_appliance.shape[1] - 1)


# Etape remove_variables : vérifier nb de variables après suppression des variables
def test_remove_variables(df_remove_variables):
    assert(df_remove_variables.shape[1] == 33)


# Etape missing_date_of_call : vérifier absence de NaN
def test_missing_date_of_call(df_missing_date_of_call):
    assert(df_missing_date_of_call['DateOfCall'].isna().sum() == 0)


# Etape convert_date_and_time : vérifier bonne conversion
def test_convert_date_and_time(df_convert_date_and_time):
    assert(str(df_convert_date_and_time['DateAndTimeMobile'].dtypes) == "datetime64[ns]")
    assert(str(df_convert_date_and_time['DateAndTimeMobilised'].dtypes) == "datetime64[ns]")
    assert(str(df_convert_date_and_time['DateAndTimeLeft'].dtypes) == "datetime64[ns]")
    assert(str(df_convert_date_and_time['DateAndTimeArrived'].dtypes) == "datetime64[ns]")


# Etape missing_tournout_time_seconds : vérifier absence de NaN
def test_missing_tournout_time_seconds(df_missing_tournout_time_seconds):
    assert(df_missing_tournout_time_seconds['TurnoutTimeSeconds'].isna().sum() == 0)


# Etape missing_travel_time : vérifier plus de NaN sur variable TravelTimeSeconds
def test_missing_travel_time(df_missing_travel_time):
    assert(df_missing_travel_time['TravelTimeSeconds'].isna().sum() == 0)


# Etape missing_deployed_from_station : vérifier plus de NaN sur variable DeployedFromStation_Name
def test_missing_deployed_from_station(df_missing_deployed_from_station):
    assert(df_missing_deployed_from_station['DeployedFromStation_Name'].isna().sum() == 0)
    assert(df_missing_deployed_from_station['DeployedFromStation_Code'].isna().sum() == 0)
    assert(df_missing_deployed_from_station['DeployedFromStation_Name'].iloc[0] == "Hornsey")
    assert(df_missing_deployed_from_station['DeployedFromStation_Code'].iloc[0] == "A32")


# Etape missing_deployed_from_location : vérifier plus de NaN sur variable DeployedFromLocation
def test_missing_deployed_from_location(df_missing_deployed_from_location):
    assert(df_missing_deployed_from_location['DeployedFromLocation'].isna().sum() ==0)


# Etape missing_special_service : vérifier plus de NaN sur variable SpecialServiceType
def test_missing_special_service(df_missing_special_service):
    assert(df_missing_special_service['SpecialServiceType'].isna().sum() == 0)


# Etape missing_delay_description : vérifier plus de NaN sur variable DelayCode_Description
def test_missing_delay_description(df_missing_delay_description):
    assert(df_missing_delay_description['DelayCode_Description'].isna().sum() == 0)


# Etape format_rename_columns : vérifier nom de colonnes + formats
def test_format_rename_columns(df_format_rename_columns):
    assert(('Latitude' in df_format_rename_columns.columns) == True)
    assert(('Longitude' in df_format_rename_columns.columns) == True)
    assert(str(df_format_rename_columns['DateOfCall'].dtypes) == "datetime64[ns]")
    assert(str(df_format_rename_columns['TurnoutTimeSeconds'].dtypes) == "int64")
    assert(str(df_format_rename_columns['TravelTimeSeconds'].dtypes) == "int64")
    assert(str(df_format_rename_columns['CalYear_y'].dtypes) == "int64")
    assert(str(df_format_rename_columns['HourOfCall_y'].dtypes) == "int64")
    assert(str(df_format_rename_columns['NumStationsWithPumpsAttending'].dtypes) == "int64")
    assert(str(df_format_rename_columns['NumPumpsAttending'].dtypes) == "int64")
    assert(str(df_format_rename_columns['PumpCount'].dtypes) == "int64")


# Etape num_pumps_attending : vérifier mise à jour de la colonne NumPumpsAttending
def test_num_pumps_attending(df_num_pumps_attending):
    # contrôle de l'incident 101105-01082019 (lignes d'index 0 et 1)
    assert(df_num_pumps_attending['NumPumpsAttending'].iloc[0] == 2)
    assert(df_num_pumps_attending['NumPumpsAttending'].iloc[1] == 2)


# Etape num_stations_pump_attending : vérifier mise à jour de NumStationsWithPumpsAttending
def test_num_stations_pump_attending(df_num_stations_pump_attending):
    # contrôle de l'incident 101105-01082019 (lignes d'index 0 et 1)
    assert(df_num_stations_pump_attending['NumStationsWithPumpsAttending'].iloc[0] == 2)
    assert(df_num_stations_pump_attending['NumStationsWithPumpsAttending'].iloc[1] == 2)


# Etape missing_date_and_time_left : vérifier plus de NaN sur variable DateAndTimeLeft
def test_missing_date_and_time_left(df_missing_date_and_time_left):
    assert(df_missing_date_and_time_left['DateAndTimeLeft'].isna().sum() == 0)


# Etape remove_dartford : s'assurer qu'on a bien supprimé les véhicules mobilisés depuis la caserne de Dartford
def test_remove_dartford(df_remove_dartford):
    assert((len(df_remove_dartford[df_remove_dartford['DeployedFromStation_Name'] == "Dartford"])) == 0)


# Etape create_mobilised_rank : vérifier création de la variable Mobilised_Rank
def test_create_mobilised_rank(df_create_mobilised_rank):
    assert(('Mobilised_Rank' in df_create_mobilised_rank.columns) == True)


# Etape incident_type_category : vérifier création 3 variables sur les types / catégories d'incidents + suppression 3 variables sources
def test_incident_type_category(df_incident_type_category):
    assert(('IncidentType' in df_incident_type_category.columns) == True)
    # 5 grandes modalités définies
    assert(len(df_incident_type_category['IncidentType'].unique()) <= 5)
    assert(('IncidentCategory' in df_incident_type_category.columns) == True)
    assert(('FalseAlarm' in df_incident_type_category.columns) == True)
    assert(('IncidentGroup' in df_incident_type_category.columns) == False)
    assert(('StopCodeDescription' in df_incident_type_category.columns) == False)
    assert(('SpecialServiceType' in df_incident_type_category.columns) == False)


# Etape distance_calc : vérifier création variable distance et suppression des variables sources
def test_distance_calc(df_distance_calc):
    assert(('Distance' in df_distance_calc.columns) == True)
    assert(('Longitude' in df_distance_calc.columns) == False)
    assert(('Latitude' in df_distance_calc.columns) == False)
    assert(('Station_Latitude' in df_distance_calc.columns) == False)
    assert(('Station_Longitude' in df_distance_calc.columns) == False)


# Etape total_pumps_out : vérifier création variable TotalOfPumpInLondon_Out
def test_total_pumps_out(df_total_pumps_out):
    assert(('TotalOfPumpInLondon_Out' in df_total_pumps_out.columns) == True)


# Etape pumps_available : vérifier création variable PumpAvailable
def test_pumps_available(df_pumps_available):
    assert(('PumpAvailable' in df_pumps_available.columns) == True)


# Etape rows_delete : vérifier qu'on supprime des lignes vs étape précédent
def test_rows_delete(df_rows_delete, df_pumps_available):
    assert (len(df_rows_delete) < len(df_pumps_available)) == True


# Etape remove_unused : vérifier qu'on ne conserve que les enregistrement mobilised rank = 1
#  et suppression variable DateAndTimeLeft
def test_remove_unused(df_remove_unused):
    # vérifier modalité unique dans Mobilised_Rank
    assert(len(df_remove_unused['Mobilised_Rank'].unique()) == 1)
    # vérifier valeur de la modalité unique dans Mobilised_Rank
    assert(df_remove_unused['Mobilised_Rank'].unique()[0] == 1)
    # vérifier suppression DateAndTimeLeft
    assert(('DateAndTimeLeft' in df_remove_unused.columns) == False)


# Etape speed_over_60 : vérifier que pas de vitesses moyennes > 60km/h et suppression var temporaire
def test_remove_unused(df_speed_over_60):
    assert(max(3600*df_speed_over_60['Distance']/df_speed_over_60['TravelTimeSeconds']) < 60)
    assert(('speed_km_per_hour' in df_speed_over_60.columns) == False)


# Etape datetime_variables : vérifier suppression 8 var & création 5 variables
def test_df_datetime_variables(df_datetime_variables):
    for var in ['CalYear_x','HourOfCall_x','DateOfCall' 'CalYear_y',
        'TimeOfCall', 'HourOfCall_y', 'DateAndTimeMobile', 'DateAndTimeArrived'] :
        assert((var in df_datetime_variables.columns) == False)
    for var in ['year', 'month', 'day', 'weekday', 'hour']:
        assert((var in df_datetime_variables.columns) == True)


# Etape add_weather : vérifier intégration de 6 variables
def test_add_weather(df_add_weather):
    for var in ['temp', 'precip', 'cloudcover', 'visibility', 'conditions', 'icon']:
        assert((var in df_add_weather.columns) == True)


# Etape add_holidays : vérifier intégration de 2 nouvelles variables
def test_add_weather(df_add_holidays):
    assert(('workingday' in df_add_holidays.columns) == True)
    assert(('school_holidays' in df_add_holidays.columns) == True)


# Etape add_traffic : vérifier intégration 1 nouvelle variable(comprise entre 0 et 1) & suppression var temporaire
def test_add_holidays(df_add_traffic):
    assert(('congestion_rate' in df_add_traffic.columns) == True)
    assert(((max(df_add_traffic['congestion_rate']) <= 1) & \
        (min(df_add_traffic['congestion_rate']) >= 0)) == True)
    assert(('congestion_key' in df_add_traffic.columns) == False)


# Dernier contrôle : vérifier qu'il n'y a plus aucun NaN à l'issue du traitement
def test_nan(df_add_traffic):
    assert((df_add_traffic.isna().sum().sum()) == 0)