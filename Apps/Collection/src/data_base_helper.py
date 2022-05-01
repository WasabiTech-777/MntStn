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


def fill_in_table(conn, csv_file_path, delimeter = ","):
    cursor = conn.cursor()
    directory = os.path.abspath(csv_file_path)
    file_type = directory.split('/')[-1]
    
    if(file_type == "13f-hr-data.csv"):
        table_name = re.sub("[^a-zA-Z]+", "", directory.split('/')[-6])
        sql_command = f"COPY {table_name}\
            FROM '{csv_file_path}'\
            DELIMITER '{delimeter}'\
            CSV HEADER;"
        
        cursor.execute(sql_command)
        return


def delete_tables_all_13f(conn, csv_file_path):
    cursor = conn.cursor()
    directory = os.path.abspath(csv_file_path)
    file_type = directory.split('/')[-1]
    print(f"file type: {file_type} \n")

    if(file_type == "13f-hr-data.csv"):
        table_name = re.sub("[^a-zA-Z]+", "", directory.split('/')[-6])
        sql_command = f'CREATE TABLE {table_name}('

        try:
            sql_command = f"DROP TABLE IF EXISTS {table_name}"
            print(f"attempting to run: {sql_command} \n")
            cursor.execute(sql_command)
            print(f"Table : {table_name} Deleted succesfully.\n")

        except:
            print("failed")

        conn.commit()
    
    else:
        print(f"Not a 13f")
    

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
            cursor.execute(sql_command)
            print(f"Table : {table_name} created succesfully.\n")
            fill_in_table(conn, csv_file_path)
            print(f"Table : {table_name} filled succesfully.\n")

        except:
            print("failed")

        conn.commit()
    
    return


def get_list_of_files(dirName):
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
            allFiles = allFiles + get_list_of_files(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles


def delete_all_companies(conn, file_path):
    listOfFiles = get_list_of_files(file_path)
    for file_at in listOfFiles:
        delete_tables_all_13f(conn, file_at)
    
    return


def read_in_companies(conn, file_path):
    listOfFiles = get_list_of_files(file_path)
    for file_at in listOfFiles:
        csv_to_sql_table(conn, file_at)
    
    return
    


if __name__ == "__main__":
    conn = connect_to_database()
    read_in_companies(conn, '/home/max/MntStn/Apps/Collection/src/resources/companies')
    delete_all_companies(conn, '/home/max/MntStn/Apps/Collection/src/resources/companies')
    
    conn.close()
