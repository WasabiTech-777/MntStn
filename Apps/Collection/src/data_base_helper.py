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
    #grabs the last folder in the csv file path
    sql_command = f'CREATE TABLE FFFFF '
    
    with open(csv_file_path) as file:
        file_at = csv.reader(file)
        for line in file_at:
            headers = line
            print(f"headers: {headers}\n\n")
            break


    for column in headers:
        #varchar does not pad and is the most versitile. could be changed in future to save space
        
        sql_command = sql_command + f" varchar(99) {column},"
    
    
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
    



class sql_parser:
    #dynamically create an aray with csv headers and fill in table dynamicly
    def __init__(self, csv_file_path):
        with open(csv_file_path) as file:
            file_at = csv.reader(file)
            self.headers = file_at[0].split(",")





#      def __init__(self, nameOfIssuer, cusip, value, shares, sshPrnamtType,
#                 putCall, investmentDiscretion, otherManager,
#                 soleVotingAuthority, sharedVotingAuthority, noneVotingAuthority):
        
        
        
#         self.nameOfIssuer = nameOfIssuer
#         self.cusip = cusip
#         self.value = value
#         self.shares = shares
#         self.sshPrnamtType = sshPrnamtType
#         self.putCall = putCall
#         self.investmentDiscretion = investmentDiscretion
#         self.otherManager = otherManager
#         self.soleVotingAuthority = soleVotingAuthority
#         self.sharedVotingAuthority = sharedVotingAuthority
#         self.noneVotingAuthority = noneVotingAuthority
# 
        
    def connect_to_database(self):
        conn = psycopg2.connect(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432")
        print(conn)
        conn.autocommit = True
        cursor = conn.cursor()
        return conn

        
    def csv_to_psql_company_table_generator(self):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        #args
        #csv
        #companyInfoTuple = (companyName, companyFiling, qtr, yr)
        #newPath
        
        #newPath = f"{os.path.dirname(__file__)}/resources/companies/{companyInfoTuple[0]}/filings/13f-hr-filing/{companyInfoTuple[3]}/{companyInfoTuple[2]}/13f-hr-data.csv"
        #create table = 

        sql_command = f"CREATE TABLE {self.nameOfIssuer}(company_name varchar(63),\
            cusip int, value int, shares int, sshPrnamtType varchar(30), putCall varchar(16) ,\
            investmentDiscretion varchar(12), otherManager varchar(99), soleVotingAuthority int,\
            sharedVotingAuthority int, noneVotingAuthority int);"
        
        try:
            cursor.execute(sql_command)
        
        except:
            print("failed")
            
        finally:
            print(f"Table : {self.nameOfIssuer} created succesfully.")
    
        conn.commit()
        conn.close()
        
    
    def store_csv_to_table(self, file_location):
        conn = self.connect_to_database()
        cursor = conn.cursor()
        f = open(file_location, 'r')
        cursor.copy_from(f, f'{self.nameOfIssuer}', sep=',')
        cursor.execute(f"select * from {self.nameOfIssuer};")
        cursor.fetchall()
        conn.commit()
        conn.close()
        
