import pytest
from datetime import datetime

# importer les fonctions à tester
from cleaning.consistency_checks import num_pumps_attending, num_stations_pump_attending, speed_over_60
from cleaning.create_variables import create_appliance, create_mobilised_rank, incident_type_category
from cleaning.data_removal import remove_dartford, remove_unused
from cleaning.external_variables import add_holidays, add_traffic, add_weather
from cleaning.gps_distance import convert_gps, distance_calc
from cleaning.missing_values import missing_travel_time, missing_special_service, missing_deployed_from_location, \
    missing_date_and_time_left, missing_date_of_call, missing_delay_description, \
    missing_deployed_from_station, missing_tournout_time_seconds
from cleaning.pumps_count import total_pumps_out, pumps_available, rows_delete
from cleaning.read_merge_datasets import extract, merge_datasets
from cleaning.variables_format import convert_date_and_time, datetime_variables, format_rename_columns, remove_variables


# définition des données de base
inc, mob, station_pos, weather, holidays, traffic = extract()
# ne garder que le mois de mai N-1 (vs date du jour) pour réaliser les tests
test_period = '05' + str(datetime.now().year - 1)
inc = inc[inc['IncidentNumber'].apply(lambda x: x[-6:]) == test_period]
mob = mob[mob['IncidentNumber'].apply(lambda x: x[-6:]) == test_period]


# Création des fixtures des étapes de nettoyage et enrichissement des données

@pytest.fixture
def inc_convert_gps(inc=inc):
    return convert_gps(inc)

@pytest.fixture
def mob_create_appliance(mob=mob):
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
def df_distance_calc(df_incident_type_category, station_pos=station_pos):
    return distance_calc(data= df_incident_type_category, station_pos=station_pos)

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
def df_add_weather(df_datetime_variables, weather=weather):
    return add_weather(df_datetime_variables, weather=weather)

@pytest.fixture
def df_add_holidays(df_add_weather, holidays=holidays):
    return add_holidays(df_add_weather, holidays=holidays)

@pytest.fixture
def df_add_traffic(df_add_holidays, traffic=traffic):
    return add_traffic(df_add_holidays, traffic=traffic)

