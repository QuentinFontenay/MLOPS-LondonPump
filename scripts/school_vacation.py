from pymongo import mongo_client
import os
import sys, getopt
import argparse
import pandas as pd
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def connect_to_mongo():
    client = mongo_client.MongoClient(
        os.environ.get('DATABASE_URL'), serverSelectionTimeoutMS=5000)

    try:
        conn = client.server_info()
        print(f'Connected to MongoDB {conn.get("version")}')
    except Exception:
        print("Unable to connect to the MongoDB server.")

    db = client[os.environ.get('MONGO_INITDB_DATABASE')]
    school_vacation = db.schoolVacations

    return school_vacation

argParser = argparse.ArgumentParser()
argParser.add_argument("-f", "--file", help="file with holidays")

args = argParser.parse_args()

if args.file != None:
    school_vacation = connect_to_mongo()
    year_vacation = list(school_vacation.find({}, { 'year': 1 }))
    with open(args.file, 'r') as file:
        csvreader = csv.reader(file)
        old_year = 0
        array = []
        for index, row in enumerate(csvreader):
            if index != 0:
                datetime_object = datetime.strptime(row[0], '%d/%m/%Y')
                if any(obj['year'] == datetime_object.year for obj in year_vacation) == False:
                    if datetime_object.year > old_year:
                        if len(array) > 0:
                            object = { "year": old_year, "dates": array }
                            school_vacation.insert_one(object)
                            print("Inserted year= %s" % old_year)
                            array = []
                        old_year = datetime_object.year
                    if datetime_object.year == old_year:
                        array.append(datetime_object)
else:
    print("No file specified")
    sys.exit(2)
