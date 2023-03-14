from cleaning.consistency_checks import num_pumps_attending, num_stations_pump_attending, speed_over_60
from cleaning.create_variables import create_appliance, create_mobilised_rank, incident_type_category
from cleaning.data_removal import remove_dartford, remove_unused
from cleaning.external_variables import add_holidays, add_traffic, add_weather
from cleaning.gps_distance import convert_gps, distance_calc
from cleaning.missing_values import missing_travel_time, missing_special_service, missing_deployed_from_location, \
    missing_date_and_time_left, missing_date_of_call, missing_delay_description, \
    missing_deployed_from_station, missing_tournout_time_seconds
from cleaning.pumps_count import total_pumps_out, pumps_available, rows_delete
from cleaning.read_merge_datasets import extract, merge_datasets, update_holidays_db
from cleaning.variables_format import convert_date_and_time, datetime_variables, format_rename_columns, remove_variables


def cleaned_data():
    '''
    clean data and add features pipeline

    returns cleaned data with new variables
    '''
    update_holidays_db() # store new holidays known in db
    inc, mob, station_pos, weather, holidays, traffic = extract()
    inc = convert_gps(data= inc)
    mob = create_appliance(data= mob)
    lfb = merge_datasets(incidents= inc, mobilisations= mob)
    df = remove_variables(lfb)
    df = missing_date_of_call(df)
    df = convert_date_and_time(df)
    df = missing_tournout_time_seconds(df)
    df = missing_travel_time(df)
    df = missing_deployed_from_station(df)
    df = missing_deployed_from_location(df)
    df = missing_special_service(df)
    df = missing_delay_description(df)
    df = format_rename_columns(df)
    df = num_pumps_attending(df)
    df = num_stations_pump_attending(df)
    df = missing_date_and_time_left(df)
    df = remove_dartford(df)
    df = create_mobilised_rank(df)
    df = incident_type_category(df)
    df = distance_calc(data= df, station_pos= station_pos)
    df = total_pumps_out(df)
    df = pumps_available(df)
    df = rows_delete(df)
    df = remove_unused(df)
    df = speed_over_60(df)
    df = datetime_variables(df)
    df = add_weather(df, weather)
    df = add_holidays(df, holidays)
    df = add_traffic(df, traffic)
    
    return df
