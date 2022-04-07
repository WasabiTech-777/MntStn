#You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
#todo make funvtions that allow for easy transfer of csv's to psql table
#works just need to install 'pip install psycopg2'
#python3.10 -m pip install --upgrade setuptools
#python3.10 -m Apps.Collection.src.data_base_helper
#sudo -u postgres -i
#CREATE USER max WITH PASSWORD 'password';

#will be company centric tables

import psycopg2


conn = psycopg2.connect(database="dummy", user = "max", password = "password", host = "127.0.0.1", port = "5432")

print(conn)


conn.autocommit = True
cursor = conn.cursor()

#nameOfIssuer,cusip,value,shares,sshPrnamtType,putCall,investmentDiscretion,otherManager,soleVotingAuthority,sharedVotingAuthority,noneVotingAuthority
#ABBOTT LABS,002824100,8444,60000,SH,,SOLE,,60000,0,0

def sql_table_string_generator(nameOfIssuer,cusip,value,shares,sshPrnamtType,putCall,investmentDiscretion,
                               otherManager,soleVotingAuthority,sharedVotingAuthority,noneVotingAuthority):
    pass


#ARGENX SE,04016X101,9766,27889,SH,,DFND,1,2,3,4,27889,0,0
sql = '''CREATE TABLE TEMPTEST(company_name varchar(63),\
    filling_date varchar(30),\
    num1 int, num2 int, cmp_ticker varchar(30), varnum varchar(30) ,\
    cmp_ticker2 varchar(30), num11 int, num12 int, num13 int, num14 int,\
    num15 int, num16 int, num17 int);'''
  


#cursor.execute(sql)
f = open(r'Apps/Collection/src/resources/13F-HR-parsed-data.csv', 'r')
cursor.copy_from(f, 'temptest', sep=',')
cursor.execute("select * from temptest;")
cursor.fetchall()

  
  
conn.commit()
conn.close()




def csv_to_psql_data_table(csv_file, data_base="dummy", 
                           user="max", password = "password", 
                           host = "127.0.0.1", port = "5432"):
    pass

