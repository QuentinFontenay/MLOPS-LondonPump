
import pytest
import pandas as pd
import numpy as np
import os

# importer les fonctions à tester (dans package 'clean_data_add_features' : voir paramétrage dans le fichier de test)
from consistency_checks import num_pumps_attending, num_stations_pump_attending, speed_over_60
from create_variables import create_appliance, create_mobilised_rank, incident_type_category
from data_removal import remove_dartford, remove_unused
from external_variables import add_holidays, add_traffic, add_weather
from gps_distance import convert_gps, distance_calc
from missing_values import missing_travel_time, missing_special_service, missing_deployed_from_location, \
    missing_date_and_time_left, missing_date_of_call, missing_delay_description, \
    missing_deployed_from_station, missing_tournout_time_seconds
from pumps_count import total_pumps_out, pumps_available, rows_delete
from read_merge_datasets import extract, merge_datasets
from variables_format import convert_date_and_time, datetime_variables, format_rename_columns, remove_variables


# emplacement des données originales du projet
data_loc_tests = "../../data"


# fixtures des variables de base

@pytest.fixture
def station_pos():
    _, _, station_pos, _, _, _ = extract(path_to_data = data_loc_tests)
    return station_pos

@pytest.fixture
def weather():
    _, _, _, weather, _, _ = extract(path_to_data = data_loc_tests)
    return weather

@pytest.fixture
def holidays():
    _, _, _, _, holidays, _ = extract(path_to_data = data_loc_tests)
    return holidays

@pytest.fixture
def traffic():
    _, _, _, _, _, traffic = extract(path_to_data = data_loc_tests)
    return traffic

@pytest.fixture
def inc():
    inc = pd.read_csv(os.path.join(data_loc_tests, "test_clean_data_add_features_inc.csv"), index_col=0)
    # création anomalie pour tests ultérieurs de fonctions num_pumps_attending & num_stations_pump_attending
    inc['NumPumpsAttending'].loc[165558] = 250              # sur incident 101105-01082019 => vs 2
    inc['NumStationsWithPumpsAttending'].loc[165558] = 100  # sur incident 101105-01082019 => vs 2
    return inc

@pytest.fixture
def mob():
    mob = pd.read_csv(os.path.join(data_loc_tests, "test_clean_data_add_features_mob.csv"), index_col=0)
    # Création 2 NaN pour test ultérieur fonction missing_deployed_from_station
    mob[['DeployedFromStation_Name','DeployedFromStation_Code' ]].iloc[0] == np.nan
    return mob


# Création des fixtures des étapes de nettoyage et enrichissement des données

@pytest.fixture
def inc_convert_gps(inc):
    return convert_gps(inc)

@pytest.fixture
def mob_create_appliance(mob):
    return create_appliance(mob)

@pytest.fixture
def lfb(inc_convert_gps, mob_create_appliance):
    return merge_datasets(incidents= inc_convert_gps, mobilisations= mob_create_appliance)

@pytest.fixture
def df_remove_variables(lfb):
    return remove_variables(lfb)

@pytest.fixture
def df_missing_date_of_call(df_remove_variables):
    return missing_date_of_call(df_remove_variables)

@pytest.fixture
def df_convert_date_and_time(df_missing_date_of_call):
    return convert_date_and_time(df_missing_date_of_call)

@pytest.fixture
def df_missing_tournout_time_seconds(df_convert_date_and_time):
    return missing_tournout_time_seconds(df_convert_date_and_time)

@pytest.fixture
def df_missing_travel_time(df_missing_tournout_time_seconds):
    return missing_travel_time(df_missing_tournout_time_seconds)

@pytest.fixture
def df_missing_deployed_from_station(df_missing_travel_time):
    return missing_deployed_from_station(df_missing_travel_time)

@pytest.fixture
def df_missing_deployed_from_location(df_missing_deployed_from_station):
    return missing_deployed_from_location(df_missing_deployed_from_station)

@pytest.fixture
def df_missing_special_service(df_missing_deployed_from_location):
    return missing_special_service(df_missing_deployed_from_location)

@pytest.fixture
def df_missing_delay_description(df_missing_special_service):
    return missing_delay_description(df_missing_special_service)

@pytest.fixture
def df_format_rename_columns(df_missing_delay_description):
    return format_rename_columns(df_missing_delay_description)

@pytest.fixture
def df_num_pumps_attending(df_format_rename_columns):
    return num_pumps_attending(df_format_rename_columns)

@pytest.fixture
def df_num_stations_pump_attending(df_num_pumps_attending):
    return num_stations_pump_attending(df_num_pumps_attending)

@pytest.fixture
def df_missing_date_and_time_left(df_num_stations_pump_attending):
    return missing_date_and_time_left(df_num_stations_pump_attending)

@pytest.fixture
def df_remove_dartford(df_missing_date_and_time_left):
    return remove_dartford(df_missing_date_and_time_left)

@pytest.fixture
def df_create_mobilised_rank(df_remove_dartford):
    return create_mobilised_rank(df_remove_dartford)

@pytest.fixture
def df_incident_type_category(df_create_mobilised_rank):
    return incident_type_category(df_create_mobilised_rank)

@pytest.fixture
def df_distance_calc(df_incident_type_category, station_pos):
    return distance_calc(data= df_incident_type_category, station_pos= station_pos)

@pytest.fixture
def df_total_pumps_out(df_distance_calc):
    return total_pumps_out(df_distance_calc)

@pytest.fixture
def df_pumps_available(df_total_pumps_out):
    return pumps_available(df_total_pumps_out)

@pytest.fixture
def df_rows_delete(df_pumps_available):
    return rows_delete(df_pumps_available)

@pytest.fixture
def df_remove_unused(df_rows_delete):
    return remove_unused(df_rows_delete)

@pytest.fixture
def df_speed_over_60(df_remove_unused):
    return speed_over_60(df_remove_unused)

@pytest.fixture
def df_datetime_variables(df_speed_over_60):
    return datetime_variables(df_speed_over_60)

@pytest.fixture
def df_add_weather(df_datetime_variables, weather):
    return add_weather(df_datetime_variables, weather)

@pytest.fixture
def df_add_holidays(df_add_weather, holidays):
    return add_holidays(df_add_weather, holidays)

@pytest.fixture
def df_add_traffic(df_add_holidays, traffic):
    return add_traffic(df_add_holidays, traffic)

