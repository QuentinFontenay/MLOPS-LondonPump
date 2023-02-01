import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from sklearn.linear_model import PassiveAggressiveRegressor


def training_model(X_train, y_train, X_test, y_test):
    '''
    Performs a gridsearch using PassiveAgressiveRegressor model, to find best 'C' parameter to be used
    
    input :
        X_train
        y_train
        X_test
        y_test

    returns :
        best_param_C    : best 'C' parameter for the model
        mae_train       : Mean Absolute Error (nb of seconds) for this best model applied to train set
        mae_test        : Mean Absolute Error (nb of seconds) for this best model applied to test set
    
    '''

    # params = {'C' :[0.001, 0.0025]}
    params = {'C' :[0.001, 0.0025, 0.005, 0.008, 0.01]}

    grid = GridSearchCV(estimator = PassiveAggressiveRegressor(),
                        param_grid = params,
                        scoring = 'neg_mean_absolute_error',
                        verbose = 3,
                        cv = 3)

    grid.fit(X_train, y_train)
    mae_train = -grid.score(X_train, y_train)
    mae_test = -grid.score(X_test, y_test)
    best_param_C = grid.best_params_['C']

    return best_param_C, mae_train, mae_test


def pred_scores_model(best_param_C, X_train, y_train, X_test, y_test):
    '''
    Trains the model with best 'C' parameter, make prediction on train and test set, and calculate metrics

    input :
        best_param_C : 'C' best value coming from grid search for PassiveAggressiveRegressor model
        X_train
        y_train
        X_test
        y_test

    returns :
        model       : PassiveAggressiveRegressor model with 'C' provided in argument
        pred_train  : predictions on train set
        pred_test   : predictions on test set
        metrics     : 8 metrics for the model (dictionary)
    '''
  
    # initialize and train the model with parameters from gridsearch
    model = PassiveAggressiveRegressor(C = best_param_C)
    model.fit(X_train, y_train)

    # make predictions
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    
    # initialize metrics variable
    metrics = {}
    
    # evaluate and store model R²
    metrics['R² train'] = np.round(model.score(X_train, y_train),2)
    metrics['R² test'] = np.round(model.score(X_test, y_test),2)
    
    # evaluate and store model RMSE
    metrics['RMSE train'] = np.round(np.sqrt(mean_squared_error(y_train, pred_train)),0)
    metrics['RMSE test'] = np.round(np.sqrt(mean_squared_error(y_test, pred_test)),0)
    
    # evaluate and store model Mean AE
    metrics['Mean AE train'] = np.round(mean_absolute_error(y_train, pred_train),0)
    metrics['Mean AE test'] = np.round(mean_absolute_error(y_test, pred_test),0)
    
    # evaluate and store model Median AE
    metrics['Median AE train'] = np.round(median_absolute_error(y_train, pred_train),0)
    metrics['Median AE test'] = np.round(median_absolute_error(y_test, pred_test),0)
    
    # return the model, predictions (on train and test set), and metrics summary
    return model, pred_train, pred_test, metrics
