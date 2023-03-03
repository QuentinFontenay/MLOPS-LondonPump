import numpy as np


def  train_test_split_index(data, test_size = 0.2):
    '''
    compute index of rows to be split between train and test set, based on incident number.

    input :
        data :      full cleaned dataset (dataframe)
        test_size : percentage of incidents to be allocated to test set

    returns :
        tts_index_test  : index of rows to be allocated to test set
        tts_index_train : index of rows to be allocated to train set

    '''

    # build sorted incidents list
    tts_inc_list = data['IncidentNumber'].unique().tolist()
    tts_inc_list.sort()

    # Total des véhicules et incidents pour juger de la répartition train / test
    # tts_nb_pump = df.shape[0]

    # size of incidents list to be allocated to test set
    tts_nb_inc = len(tts_inc_list)
    tts_test_size_nb = np.int64(tts_nb_inc * test_size)

    # list of incidents to be allocated to test set (select random sample of 'test_size_nb' elements from the list, without replacement)
    tts_inc_test_list = list(np.random.choice(tts_inc_list, tts_test_size_nb, replace= False))

    # save and returns the index (since IncidentNumber will be removed from variables later)
    tts_index_test = data[data['IncidentNumber'].isin(tts_inc_test_list)].index
    tts_index_train = data[~data['IncidentNumber'].isin(tts_inc_test_list)].index

    return tts_index_test, tts_index_train


def train_test_split_incident(target, features, tts_index_test, tts_index_train):
    '''
    split dataset into train and test set based on incident ref
    (so that all vehicles attending an incident are or in test, or in train, not both)

    input :
        target          : target variable (to be predicted by model)
        features        : features to predict target
        tts_index_test  : index of data to be allocated to test set
        tts_index_train : index of data to be allocated to train set
    
    returns :
        X_train, X_test, y_train, y_test
    
    '''

    X_train = features.loc[tts_index_train]
    X_test = features.loc[tts_index_test]
    y_train = target.loc[tts_index_train]
    y_test = target.loc[tts_index_test]

    return X_train, X_test, y_train, y_test
