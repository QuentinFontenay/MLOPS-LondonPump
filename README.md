# Sujet

Ce projet a été mené dans le cadre de la formation MLOps dispensée par DataScientest.

Il est la continuation du projet "London Pump.PY", développé lors du cursus Data Scientist (travail de groupe, promo Oct21 continu).

Sur la thématique du temps de réponse d’un véhicule de la Brigade des Pompiers de Londres (LFB), ce projet avait été mené selon 3 axes d'analyse, visant par des techniques de Machine Learning, à prédire  pour un incident signalé aux pompiers :

 1. le <u>nombre de véhicules de secours</u> à envoyer (par une classification de 1 à 5) ;
 2. si ces véhicules sont susceptibles d'<u>arriver en plus ou moins de 360 secondes</u>, par une classification binaire (la valeur de 360 secondes constituant l'objectif premier la la LFB) ;
 3. le <u>temps</u> mis par chacun des véhicules, pour arriver sur les lieux de l'incident, <u>exprimé en secondes</u> (régression).

*<u>Note</u> : le temps de réponse étant défini ici comme la différence entre la mobilisation du véhicule et son arrivée sur les lieux de l’incident.*

Pour la poursuite de ce projet dans un contexte MLOps (implémentation du cycle de vie de ce modèle en production), nous nous sommes limités au dernier axe d'analyse (prédiction du temps d'arrivée des véhicules sur les lieux de l'incident). Bien évidemment les 2 autres axes pourront venir compléter ultérieurement ces travaux.

L'idée ici sera :

  * de mettre en place une API d'estimation du temps d'arrivée sur les lieux, d'un véhicule envoyé. On peut imaginer cet outil à destination du centre recevant les appels (annonce du temps à l'interlocuteur, recherche d'autres ressources, etc...) ;
  * d'effectuer un nouvel entrainement du modèle lorsque des données plus récentes seront disponibles ;
  * et enfin de remplacer le modèle utilisé par l'API par le nouveau, s'il s'avère plus performant.

A noter que lors de l'entraînement du modèle, on identifie également une liste de casernes qui présentent habituellement des temps de réponses élevés. Le modèle ne sait les prédire correctement (ces temps sont généralement sous-estimés). Cette information est ensuite intégrée à l'API, laquelle retournera donc au final les informations suivantes :

  * le temps de réponse estimé (en secondes) ;
  * et l'indication du potentiel risque que ce temps soit sous-estimé (True / False).


# Jeu de données et sources d'informations

Le coeur du projet repose sur des données accessibles sur le [London Datastore](https://data.london.gov.uk/), plus spécifiquement 2 fichiers excel regroupant sur les 3 dernières années :

  * les **<u>incidents</u>** sur lesquels la LFB est intervenue : [London Fire Brigade Incident Records](https://data.london.gov.uk/dataset/london-fire-brigade-incident-records)

  * les **<u>véhicules</u>** envoyés sur chacun des incidents : [London Fire Brigade Mobilisation Records](https://data.london.gov.uk/dataset/london-fire-brigade-mobilisation-records)


Ces données ont été complétées au cours du projet, par d'autres ressources concernant la ville de Londres :


|Nature                        |Sources                                                                                                                                                |Commentaire                                                                                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Traffic routier (taux de congestion)|[London traffic report - TomTom Traffic Index](https://www.tomtom.com/traffic-index/london-traffic/)                                                   |remplacé par [Waybackmachine - London traffic report - TomTom Traffic Index](https://web.archive.org/web/20221118182654/https://www.tomtom.com/traffic-index/london-traffic/) <sup>(1)</sup> |
|Dates des vacances scolaires        |[Barking and Dagenham School Holidays - PublicHolidays.co.uk](https://publicholidays.co.uk/school-holidays/england/barking-and-dagenham/)| quartier de Londres choisi arbitrairement
|Données météo                       |[Weather Data & Weather API - Visual Crossing](https://www.visualcrossing.com/)                                                                        |Utilisation de l'API pour retrouver les conditions météo historiques, heure par heure <sup>(2)</sup>                                                                                             |

*<u>Notes</u> :*

*(1) les données relatives au traffic routier du site TomTom, exploitées dans le modèle, ont cessé d'être disponibles peu de temps avant le rendu du projet. Cela nous obligé à trouver une solution alternative ; bien évidemment, cette solution ne saurait être satisfaisante pour une mise en production réelle, mais a été retenue ici car trop de conséquences par rapport à l'échéance à tenir.*

*(2) l'offre gratuite proposée par VisualCrossing n'est pas suffisante pour couvrir les besoins du projet. Toutefois, VisualCrossing propose un "Academic plan", que nous avons pu solliciter et obtenir pour cet exercice (voir conditions [ici](https://www.visualcrossing.com/resources/documentation/weather-data/academic-student-and-research-discounts-for-weather-data/)).*


# Les outils mis en oeuvre

Langage Python

Exploitation de containers Dockers (existants sur DockerHub + créés spécifiquement pour le projet).

A COMPLÉTER

# Schéma d'implémentation

![schéma définitif](lien/vers/Diagramme_projet.drawio.png)

# Exécution en local

prérequis : disposer de Docker

## Télécharger et paramétrer le projet en local

### Droits sur les dossiers locaux
S'assurer d'avoir les droits en écriture sur les dossiers et leur contenu :

  * data/modele
  * airflow/logs

### Paramétrer l'environnement

Créer fichier .env.production à la racine du projet, en remplaçant les xxxxx par vos valeurs

>`MONGO_INITDB_ROOT_USERNAME="xxxxx"`

>`MONGO_INITDB_ROOT_PASSWORD="xxxxx"`

>`MONGO_INITDB_DATABASE=london_fire`

>`MONGO_INITDB_HOST=mongodb:27017`

>`MONGO_LONDON_FIRE_USER="xxxxx"`

>`MONGO_LONDON_FIRE_PASSWORD="xxxxx"`

>`DATABASE_URL=mongodb://admintest:password1234@mongodb:27017/london_fire?retryWrites=true&w=majority&authSource=london_fire`

>`VISUAL_CROSSING_KEY=xxxxxxxxxxxxxxx`

>`ACCESS_TOKEN_EXPIRES_IN=12000`

>`REFRESH_TOKEN_EXPIRES_IN=60`

>`JWT_ALGORITHM=HS256`

>`JWT_SECRET_KEY=90c1489e9552277a271246a92595f393821544fd732f961aa954dc822def4088`

>`SELENIUM_HOST="http://selenium:4444"`

>`PYTHON_ENV=production`

>`AIRFLOW_USERNAME=xxxxx`

>`AIRFLOW_PASSWORD=xxxxx`

## Lancer le projet

Lancer les 2 lignes de commandes suivantes, pour lancer la construction des images du projet, puis lancer l'ensemble des containers :

>`docker-compose build`

>`docker-compose --env-file ./.env.production up`

S'assurer que les 5 containers du projet fonctionnent :
>`docker container ls`

Le projet lancera alors :

  * l'entrainement tous les 15 du mois à 2h ;
  * le DAG airflow (archivage et sélection du modèle) tous les 16 du mois à 00h.

## Tester manuellement le projet exécuté en local

### Utiliser l'API

Dans le navigateur, se rendre à l'adresse :

> `localhost:8000/docs`

Créer un utilisateur en utilisant l'endpoint :

> POST /register

Se connecter avec cet utilisateur :

> bouton Authorize

Faire une prédiction du temps d'intervention avec l'endpoint :

> POST /predict/time_pump


### Lancer manuellement un entrainement, puis un choix de meilleur modèle (via Airflow)

Se rendre dans le container de l'entrainement :

>`docker container exec -it mlops-londonpump_entrainement_model_1 /bin/sh`

Dans ce container, lancer le script d'entraînement (compter <u>environ 1 heure</u> pour cette étape) :

>`python /entrainement/train_predict_time.py`

Quand l'entrainement est terminé, Airflow dispose des fichiers nécessaires à son exécution, on peut donc lancer le DAG d'archivage et choix du modèle :

Dans le navigateur, ouvrir l'interface d'Airflow :

>`localhost:8080`

Renseigner les identifiant + mot de passe définis dans le fichier .env.production

Lancer le DAG : le nouveau modèle est archivé, et s'il est meilleur que le modèle passé, il se substitue à celui utilisé par l'API.


## Arrêter le projet

Commande :
>`docker-compose down`




# Autre ?

