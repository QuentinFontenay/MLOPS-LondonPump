from joblib import load
import pandas as pd
from utils.mongodb import Stations
from utils.helpers import path_file

def load_file():
    reg_scaler = load(path_file() + '/reg_scaler.pkl')
    # les colonnes des variables de base du modèle (avant dichotomisation) + leurs formats
    reg_df_columns = load(path_file() + '/reg_df_columns.pkl')

    # les colonnes après dichotomisation = le format sur lequel le modèle sauvegardé "sait faire des prédictions"
    reg_data_dummies_columns = load(path_file() + '/reg_data_dummies_columns.pkl')

    model = load(path_file() + '/passiveAggressiveRegressor_mlops.joblib')

    return reg_scaler, reg_df_columns, reg_data_dummies_columns, model

def predict_time_pumps(params):
    try:
        num_var = ['Distance', 'TotalOfPumpInLondon_Out', 'temp', 'precip', 'cloudcover', 'visibility', 'congestion_rate']
        reg_scaler, reg_df_columns, reg_data_dummies_columns, model = load_file()
        dataframe = pd.DataFrame([params])
        # S'assurer que les colonnes sont dans le même ordre que le df principal
        # ne semble pas nécessaire (à voir...)
        data = dataframe[reg_df_columns]
        # Créer df au format dichotomisé
        data_dum = pd.get_dummies(data)
        # Normalisation des variables numériques
        data_dum[num_var] = reg_scaler.transform(data_dum[num_var])
        # Création d'un df vide, avec les colonnes de base du modèle
        data_ml = pd.DataFrame(columns = reg_data_dummies_columns)
        # Reporter les valeurs de l'incident créé, dans le tableau au format du modèle
        data_ml = pd.concat([data_ml, data_dum])
        # Remplacer les valeurs manquantes par 0 (ce sont les variables qui doivent être à zéro suite à dichotomisation)
        data_ml = data_ml.fillna(0)

        # Voir si la caserne de provenance est dans la liste de celles qui ont un temps habituellement plus élevé que le modèle
        stations = list(Stations.find({}, { "code": 1, "_id": 0 }))
        if any(obj['code'] == data['Station_Code_of_ressource'][0] for obj in stations) == True:
            risk_underestimated = True
        else :
            risk_underestimated = False

        # calcul de la prédiction
        predict_time = model.predict(data_ml)
        return int(predict_time), risk_underestimated
    except Exception as e:
        print(e)
        return None, False
