def remove_dartford(data):
    '''
    Remove Dartford station from dataset (not in London Fire Brigade)
    '''

    # incidents where Dartford is attending
    dartford_incident = list(data[data['DeployedFromStation_Name'] == 'Dartford']['IncidentNumber'])[0]
    
    # removing incidents
    data = data[data['IncidentNumber'] != dartford_incident]

    return data


def remove_unused(data):
    '''
    remove records and variables that will finally not be used
    '''

    # keep only mobilised rank 1
    data = data[data['Mobilised_Rank'] == 1]
    # remove DateAndTimeLeft
    data = data.drop('DateAndTimeLeft', axis= 1)

    return data

