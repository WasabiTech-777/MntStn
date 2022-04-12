# You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
# todo make funvtions that allow for easy transfer of csv's to psql table
# works just need to install 'pip install psycopg2'
# python3.10 -m pip install --upgrade setuptools
# python3.10 -m Apps.Collection.src.data_base_helper
# sudo -u postgres -i
# CREATE USER max WITH PASSWORD 'password';

# will be company centric tables
import psycopg2
import csv
import os
import re

# returns a connection type object


def connect_to_database(database="dummy", user="max", password="password", host="127.0.0.1", port="5432"):
    conn = psycopg2.connect(database="dummy", user="max",
                            password="password", host="127.0.0.1", port="5432")
    print(f"connection: {conn}\n")
    conn.autocommit = True
    cursor = conn.cursor()
    return conn


def csv_to_sql_table(conn, csv_file_path):

    cursor = conn.cursor()
    directory = os.path.abspath(csv_file_path)
    file_type = directory.split('/')[-1]
    print(f"file type: {file_type} \n")

    if(file_type == "13f-hr-data.csv"):

        table_name = re.sub("[^a-zA-Z]+", "", directory.split('/')[-6])
        sql_command = f'CREATE TABLE {table_name}('

        with open(csv_file_path) as file:
            file_at = csv.reader(file)
            for line in file_at:
                headers = line
                print(f"headers: {headers}\n\n")
                break

        for column in headers:
            # varchar does not pad and is the most versitile. could be changed in future to save space
            sql_command = sql_command + f" {column} varchar(99),"

        sql_command = sql_command.rstrip(sql_command[-1])
        sql_command = sql_command + f");"

        try:
            print(f"attempting to run: {sql_command} \n")
            #cursor.execute(sql_command)
            print(f"Table : {table_name} created succesfully.\n")
            sql_command = f"DROP TABLE IF EXISTS {table_name}"
            cursor.execute(sql_command)

        except:
            print("failed")

        conn.commit()
    
    return


def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles



def read_in_companies(conn, file_path):
    listOfFiles = getListOfFiles(file_path)
    for file_at in listOfFiles:
        csv_to_sql_table(conn, file_at)
    
    return
    


if __name__ == "__main__":
    conn = connect_to_database()
    read_in_companies(conn, '/home/max/MntStn/Apps/Collection/src/resources/companies')
    #csv_to_sql(conn, '/home/max/MntStn/Apps/Collection/src/resources/companies/ZEVIN_ASSET_MANAGEMENT_LLC/filings/13f-hr-filing/2022/1/13f-hr-data.csv')
    conn.close()
