from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from joblib import load
import shutil
import os

model_path = '../../data/modele'

my_dag = DAG(
    dag_id='london_pump_py_model_selection',
    doc_md="""#### DAG du projet London Pump.Py
    
    Ce DAG permet de comparer le score du dernier modèle (nouvellement entraîné) par rapport au modèle utilisé par l'API.

    Les fichiers issus du dernier entraînement sont situés dans un dossier "last_run".
    
    Si le nouveau modèle est plus performant (une MAE moindre), alors :
    * ses fichiers viennent remplacer ceux utilisés par l'API (on en réalise une copie à utiliser comme "best model") ;
    * les fichiers originaux de ce nouveau modèle sont déplacés vers un dossier d'archives.
    
    En revanche, si les performances du nouveau modèle sont momins bonnes que le précédent, seul l'archivage de ce dernier entraînement est réalisé.

    Contenu / organisation des archives :
    * un fichier des scores pour tous les modèles entrainés ;
    * des sous-dossiers 'run_' suivis de date et heure, pour chacun des modèles archivés.
    """,
    description="Comparer les performances du modèle entraîné vs celui utilisé, et choisir le meilleur pour l'API",
    schedule_interval='00 00 16 * *',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0),
    },
    catchup = False
)


def check_last_run():
    # voir le contenu du dossier de dernier entrainement
    files_list = os.listdir(model_path + '/last_run/')
    nb_files = len(files_list)
    if nb_files == 5:
        # retrouver l'horodatage du modèle
        model_train_time = files_list[0][:14]
        print('OK : un modele a traiter, référencé :', model_train_time)
        return model_train_time, files_list
    elif nb_files == 0:
        print("ATTENTION : aucun modèle entrainé récemment n'est disponible dans le dossier 'last_run'.")
    else :
        print("ATTENTION : Nombre de fichier dans dossier 'last_run' non cohérent !")

def get_historical_scores():
    scores = load(model_path + '/archives/scores_models_mae.pkl')
    print("SCORES HISTORIQUES :")
    print(scores)
    return scores

def keep_best_model(model_train_time, scores, files_list):
    if scores[model_train_time] <= min(scores.values()):
        print('Le nouveau modèle entrainé est meilleur que les précédents.')
        for f in files_list:
            src = os.path.join(model_path, 'last_run', f)
            dst = os.path.join(model_path, f[15:])
            # supprimer le fichier de la version précédente du best model
            os.remove(dst)
            # copier le fichier du nouveau best model
            shutil.copy2(src, dst)
            print("COPIE REUSSIE :", src, "---- A ETE COPIE VERS ----> ", dst)
        print("OK : le modèle utilisé par l'API a été remplacé par le nouveau modèle.")
    else:
        print("AUCUN CHANGEMENT : le nouveau modèle entrainé est moins performant que celui utilisé par l'API.")
  

def archive_files(files_list, model_train_time):
    # créer dossier de destination des archives
    dst_path = os.path.join(model_path, 'archives', 'run_' + model_train_time)
    os.mkdir(dst_path, mode=0o777)    
    for f in files_list:
        src = os.path.join(model_path, 'last_run', f)
        dst = os.path.join(dst_path, f[15:])
        shutil.copy2(src, dst)
        os.remove(src)
        print("ARCHIVAGE REUSSI :", src, "---- A ETE ARCHIVE VERS ----> ", dst)
    print('Archivage terminé.')


task1 = PythonOperator(
    task_id='check_last_training_run',
    python_callable=check_last_run,
    dag=my_dag,
    doc_md="""#### Vérifier présence des fichiers d'entraînement

    Vérifier si le dossier 'last_run' contient effectivement les 5 fichiers qui sont générés lors d'un nouvel entraînement.
    """
)

task2 = PythonOperator(
    task_id='get_historical_training_scores',
    python_callable=get_historical_scores,
    dag=my_dag,
    doc_md="""#### Récupérer les scores

    Nous récupérons ici le dictionnaire regroupant les MAE de tous les modèles entraînés, pour pouvoir déterminer ensuite si le nouveau modèle est plus performant que les modèles passés.
    """
)

task3 = PythonOperator(
    task_id='check_best_model',
    python_callable=keep_best_model,
    op_kwargs= {
        'model_train_time': check_last_run()[0],
        'files_list': check_last_run()[1],
        'scores': get_historical_scores()
    },
    dag=my_dag,
    doc_md="""#### Le nouveau modèle est-il meilleur que les autres ?
    
    Dans cette tâche, on procède à l'analyse du score du nouveau modèle. Si ce score est le meilleur, alors on remplace le "best model" (= les 5 fichiers situés dans le dossier '/modele') par ceux de ce nouveau modèle.
    """
)

task4 = PythonOperator(
    task_id='archive_last_run_files',
    python_callable=archive_files,
    op_kwargs= {
        'files_list': check_last_run()[1],
        'model_train_time': check_last_run()[0]
    },
    dag=my_dag,
    doc_md="""#### Archivage

    Que le nouveau modèle soit le plus performant ou non, on archive ses fichiers d'entraînement (historisation), et on vide le dossier 'last_run' qui sera ainsi prêt à accueillir les fichiers du prochain entraînement.
    """
)


task1 >> task2
task2 >> task3
task3 >> task4
