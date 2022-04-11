#You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
#todo make funvtions that allow for easy transfer of csv's to psql table
#works just need to install 'pip install psycopg2'
#python3.10 -m pip install --upgrade setuptools
#python3.10 -m Apps.Collection.src.data_base_helper
#sudo -u postgres -i
#CREATE USER max WITH PASSWORD 'password';

#will be company centric tables

import psycopg2
import csv
import os
import re

#returns a connection type object
def connect_to_database(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432"):
        conn = psycopg2.connect(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432")
        print(f"connection: {conn}\n")
        conn.autocommit = True
        cursor = conn.cursor()
        return conn

#returns void
def csv_to_sql(conn, csv_file_path):
    
    cursor = conn.cursor()
    directory = os.path.abspath(csv_file_path)

    table_name = re.sub("[^a-zA-Z]+", "", directory.split('/')[-6])
    print(f"table name : {table_name} \n")
    #grabs the last folder in the csv file path
    #sql_command = f'CREATE TABLE {os.path.abspath(csv_file_path)}('
    sql_command = f'CREATE TABLE {table_name}('
    
    with open(csv_file_path) as file:
        file_at = csv.reader(file)
        for line in file_at:
            headers = line
            print(f"headers: {headers}\n\n")
            break


    for column in headers:
        #varchar does not pad and is the most versitile. could be changed in future to save space
        sql_command = sql_command + f" {column} varchar(99),"
    
    sql_command = sql_command.rstrip(sql_command[-1])
    sql_command = sql_command + f");"
    
    try:
        print(f"attempting to run: {sql_command} \n")
        cursor.execute(sql_command)
        print(f"Table : {os.path.basename(csv_file_path)} created succesfully.\n")
        
    except:
        print("failed")

    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    conn = connect_to_database()
    csv_to_sql(conn, '/home/max/MntStn/Apps/Collection/src/resources/companies/ACME,_LLC/filings/13f-hr-filing/2022/1/13f-hr-data.csv')