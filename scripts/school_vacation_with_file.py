from pymongo import mongo_client
import os
import sys
import argparse
import csv
from datetime import datetime
from dotenv import load_dotenv
import csv
import json

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
new_array = []
if args.file != None:
    school_vacation = connect_to_mongo()
    year_vacation = list(school_vacation.find({}, { 'year': 1 }))
    file = open(args.file)
    row_count = len(file.readlines())
    with open(args.file, 'r') as file:
        csvreader = csv.reader(file)
        old_year = 0
        array = []
        for index, row in enumerate(csvreader):
            if index != 0:
                datetime_object = datetime.strptime(row[0], '%d/%m/%Y')
                if any(obj['year'] == datetime_object.year for obj in year_vacation) == False:
                    if datetime_object.year > old_year or row_count == index + 1:
                        if len(array) > 0:
                            if row_count == index + 1:
                                array.append(datetime_object)
                            object = { "year": old_year, "dates": array }
                            new_array.append(object)
                            school_vacation.insert_one(object)
                            print("Inserted year= %s" % old_year)
                            result = school_vacation.delete_one({"year": old_year - 3})
                            if (result.deleted_count == 1):
                                print("Deleted year= %s" % (old_year - 3))
                            array = []
                        old_year = datetime_object.year
                    if datetime_object.year == old_year:
                        array.append(datetime_object)
    with open('schoolVacations.json', 'w') as f:
        for index, row in enumerate(new_array):
            del row['_id']
            for index, date in enumerate(row['dates']):
                row['dates'][index] = { "$date": { "$numberLong": str(round((date.timestamp() + 3600) * 1000)) } }
        json.dump(new_array, f, indent=4)
else:
    print("Please provide a file with holidays")
    sys.exit(2)
