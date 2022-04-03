#You are connected to database "central_db" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
#todo make funvtions that allow for easy transfer of csv's to psql table
#works just need to install 'pip install psycopg2-binary'
#python3.10 -m pip install --upgrade setuptools
import psycopg2



conn = psycopg2.connect("dbname=central_db user=postgres password=postgres")

print(conn)
def csv_to_file(filename, path):
    pass

