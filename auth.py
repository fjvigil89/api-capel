import mariadb
from pymongo import MongoClient

def mongoDBConnection():
    client = MongoClient("mongodb+srv://apicapel:lwwb9e3nxK4wJOGH@apicapel.scttl.mongodb.net/?retryWrites=true&w=majority")
    #URI: mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority
    db = client["ApiCapel"]
    users_collection = db["systemUsers"]

def mariaDBConnection():
    connection = None
    try:
        connection = mariadb.connect(
        user="api-capel",
        password="fm?p!3qLVMO#D5px",
        host="b2b-capel-app.c6tid4wxmmxn.us-east-1.rds.amazonaws.com",
        database="b2b-api"
        )

        #print("MariaDB Database connection successful")
    except mariadb.Error as err:
        print(f"Error: '{err}'")

    return connection

def mariaDBConnectionII():
    connection = None
    try:
        connection = mariadb.connect(
        user="api-capel",
        password="fm?p!3qLVMO#D5px",
        host="b2b-capel-app.c6tid4wxmmxn.us-east-1.rds.amazonaws.com",
        database="b2b-api"
        )

        #print("MariaDB Database connection successful")
    except mariadb.Error as err:
        print(f"Error: '{err}'")

    return connection
