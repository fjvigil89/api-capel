import mariadb

def mariaDBConnection():
    connection = None
    try:
        connection = mariadb.connect(
        user="api-capel",
        password="fm?p!3qLVMO#D5px",
        host="b2b-capel-app.c6tid4wxmmxn.us-east-1.rds.amazonaws.com",
        #database="b2b-api"
        )

        #print("MariaDB Database connection successful")
    except mariadb.Error as err:
        print(f"Error: '{err}'")

    return connection
