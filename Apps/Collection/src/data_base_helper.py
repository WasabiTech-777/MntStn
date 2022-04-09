#You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
#todo make funvtions that allow for easy transfer of csv's to psql table
#works just need to install 'pip install psycopg2'
#python3.10 -m pip install --upgrade setuptools
#python3.10 -m Apps.Collection.src.data_base_helper
#sudo -u postgres -i
#CREATE USER max WITH PASSWORD 'password';

#will be company centric tables

import psycopg2



class sql_parser:
    def __init__(self, nameOfIssuer, cusip, value, shares, sshPrnamtType,
                putCall, investmentDiscretion, otherManager,
                soleVotingAuthority, sharedVotingAuthority, noneVotingAuthority):
        
        self.nameOfIssuer = nameOfIssuer
        self.cusip = cusip
        self.value = value
        self.shares = shares
        self.sshPrnamtType = sshPrnamtType
        self.putCall = putCall
        self.investmentDiscretion = investmentDiscretion
        self.otherManager = otherManager
        self.soleVotingAuthority = soleVotingAuthority
        self.sharedVotingAuthority = sharedVotingAuthority
        self.noneVotingAuthority = noneVotingAuthority

        
    def connect_to_database(self):
        conn = psycopg2.connect(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432")
        print(conn)
        conn.autocommit = True
        cursor = conn.cursor()
        return conn

        
    def csv_to_psql_company_table_generator(self):
        conn = self.connect_to_database()
        cursor = conn.cursor()

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
        


  
print("afasdfasd")


def csv_to_psql_data_table(csv_file, data_base="dummy", 
                           user="max", password = "password", 
                           host = "127.0.0.1", port = "5432"):
    pass

