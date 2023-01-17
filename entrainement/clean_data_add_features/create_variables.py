import numpy as np


def create_appliance(data):
    '''
    Create appliance (vehicle type) in mobilisations dataframe
    '''

    data['Appliance'] = (data['Resource_Code'].apply(lambda x : x[-1:])).map({'2' : 'Pump Ladder', '1' : 'Pump Dual Ladder'})

    return data


def create_mobilised_rank(data):
    '''
    calculate a "rank" for each mobilisation time to identify for each pump, from which mobilisation wave they were.
    '''
    
    ## Création d'un tableau visant à lister les DateAndTimeMobilised uniques, de chaque incident
    # afin de leur attribuer un rang + compte des véhicules appelés (1ère vague de mobilisation, seconde, etc...)
    # exécution 6 minutes...

    # create new table (make a list of all unique DateAndTimeMobilised by incident)
    df_mob_rank = data[['IncidentNumber', 'DateAndTimeMobilised', 'AttendanceTimeSeconds']].groupby(by=['IncidentNumber', 'DateAndTimeMobilised']).count().reset_index()
    df_mob_rank = df_mob_rank.sort_values(by = ['IncidentNumber', 'DateAndTimeMobilised'])
    df_mob_rank = df_mob_rank.rename({'AttendanceTimeSeconds' : 'Nb_pumps_asked'}, axis = 1)

    # create a variable to identify the rank (default value = 1)
    df_mob_rank['Mobilised_Rank'] = 1

    # calculate the rank for each DateAndTimeMobilised
    for i in range(1,df_mob_rank.shape[0]):
        if df_mob_rank['IncidentNumber'].loc[i] != df_mob_rank['IncidentNumber'].loc[i-1]:
            df_mob_rank['Mobilised_Rank'].loc[i] = 1
        else:
            df_mob_rank['Mobilised_Rank'].loc[i] = df_mob_rank['Mobilised_Rank'].loc[i-1]+1

    # define multi-index (incident number + mobilisation data/time)
    df_mob_rank = df_mob_rank.set_index(['IncidentNumber', 'DateAndTimeMobilised'])

    ## create new column in main dataframe with the results
    data['Mobilised_Rank'] = 0
    # loop to get rank from rank table
    for i in data.index:
        # incident index in rank table
        inc_no = data['IncidentNumber'].loc[i]
        # DateAndTimeMobilised index in rank table
        mob_time = data['DateAndTimeMobilised'].loc[i]
        # copying rank found
        data['Mobilised_Rank'][i] = df_mob_rank['Mobilised_Rank'].loc[inc_no, mob_time]

    return data


def incident_type_category(data):
    '''
    defining 5 major types of incidents and removing old variables ('IncidentGroup','StopCodeDescription', 'SpecialServiceType')
    '''

    # creating 'IncidentType' variable (5 major types of incidents)
    # Type d'Incident : Fire / Major Environmental Disasters / Domestic Incidents / Local Emergencies / Prior rrangements

    data['IncidentType'] = data['IncidentGroup']
    data['IncidentType'] = np.where(data['IncidentType'] == "False Alarm", data['StopCodeDescription'], data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "Special Service", data['SpecialServiceType'], data['IncidentType'])

    # Fire
    data['IncidentType'] = np.where(data['IncidentType'] == "False alarm - Good intent", "Fire", data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "False alarm - Malicious", "Fire", data['IncidentType'])
    data['IncidentType'] = np.where(data['IncidentType'] == "AFA", "Fire", data['IncidentType'])

    #  major environmental disasters e.g. flooding, hazardous material incidents or spills and leaks
    data['IncidentType'] = np.where((data['IncidentType'] == "Flooding") |
                            (data['IncidentType'] == "Hazardous Materials incident") |
                            (data['IncidentType'] == "Spills and Leaks (not RTC)"),
                            "Major Environmental Disasters", data['IncidentType'])

    #  domestic incidents e.g. persons locked in/out, lift releases, suicide/attempts
    data['IncidentType'] = np.where((data['IncidentType'] == "Suicide/attempts") |
                            (data['IncidentType'] == "Effecting entry/exit") |
                            (data['IncidentType'] == "Lift Release"),
                            "Domestic Incidents", data['IncidentType'])

    # local emergencies e.g. road traffic incidents, responding to medical emergencies,
    # rescue of persons and/or animals or making areas safe
    data['IncidentType'] = np.where((data['IncidentType'] == "Animal assistance incidents") | 
                            (data['IncidentType'] == "Medical Incident") | 
                            (data['IncidentType'] == "Removal of objects from people") |
                            (data['IncidentType'] == "Other rescue/release of persons") |
                            (data['IncidentType'] == "RTC")|
                            (data['IncidentType'] == "Other Transport incident") |
                            (data['IncidentType'] == "Evacuation (no fire)") |
                            (data['IncidentType'] == "Rescue or evacuation from water") |
                            (data['IncidentType'] == "Water Provision") |
                            (data['IncidentType'] == "Medical Incident - Co-responder") |
                            (data['IncidentType'] == "Making Safe (not RTC)") |
                            (data['IncidentType'] == "Water provision"),
                            "Local Emergencies", data['IncidentType'])

    #  prior arrangements to attend or assist other agencies, which may include 
    # some provision of advice or standing by to tackle emergency situations
    data['IncidentType'] = np.where((data['IncidentType'] == "Advice Only") |
                            (data['IncidentType'] == "No action (not false alarm)") |
                            (data['IncidentType'] == "Assist other agencies") |
                            (data['IncidentType'] == "Stand By"),
                            "Prior Arrangement", data['IncidentType'])

    # create a column gathering all sub categories : "IncidentCategory" (gathering "StopCodeDescription" & "SpecialServiceType")
    data['IncidentCategory'] = data['IncidentGroup']
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "Fire", data['StopCodeDescription'], data['IncidentCategory'])
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "False Alarm", data['StopCodeDescription'], data['IncidentCategory'])
    data['IncidentCategory'] = np.where(data['IncidentCategory'] == "Special Service", data['SpecialServiceType'], data['IncidentCategory'])

    # create a False Alarm column (0/1)
    data['FalseAlarm']= data['IncidentGroup']
    data['FalseAlarm'] = data['FalseAlarm'].replace(to_replace = ["Special Service", "Fire"], value = 0)
    data['FalseAlarm'] = data['FalseAlarm'].replace(to_replace = ["False Alarm"], value = 1)
    
    # remove useless columns "IncidentGroup","StopCodeDescription", "SpecialServiceType"
    data=data.drop(['IncidentGroup','StopCodeDescription', 'SpecialServiceType'], axis = 1)
    
    return data

