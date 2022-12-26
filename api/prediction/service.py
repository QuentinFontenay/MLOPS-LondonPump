from joblib import load
import pandas as pd

def load_file():
    reg_saved_files = '../public/'
    reg_scaler = load(reg_saved_files + 'reg_scaler.pkl')

    # les colonnes des variables de base du modèle (avant dichotomisation) + leurs formats
    reg_df_columns = load(reg_saved_files + 'reg_df_columns.pkl')

    # les colonnes après dichotomisation = le format sur lequel le modèle sauvegardé "sait faire des prédictions"
    reg_data_dummies_columns = load(reg_saved_files + 'reg_data_dummies_columns.pkl')

    model = load(reg_saved_files + 'passiveAggressiveRegressor.joblib')

    return reg_scaler, reg_df_columns, reg_data_dummies_columns, model

def predict_time_pumps(params):
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
    # if data['Station_Code_of_ressource'][0] in topslowest_code:
    #     risk_underestimated = 'oui'
    # else :
    #     risk_underestimated = 'non'

    # calcul de la prédiction
    predict_time = model.predict(data_ml)
    
    return int(predict_time)
