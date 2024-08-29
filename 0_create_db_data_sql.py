import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()

## connect to sqlite
connection = sqlite3.connect(os.getenv('DB_NAME'))

## Create a cursor object to insert record, create table, retrive and other functionality
cursor = connection.cursor()

## Create the table
table_info = """
Create table PERSON_DETAILS(
    NAME VARCHAR(25),
    TECH VARCHAR(25),
    POSITION VARCHAR(25),
    YEARS_OF_EXPERIENCE INT);
"""


cursor.execute(table_info)


# INSERT SOME MORE RECORDS


cursor.execute(
    """Insert Into PERSON_DETAILS values('Steffy Khristi', 'Python Developer', 'Sofware Engineer', '3')"""
)
cursor.execute(
    """Insert Into PERSON_DETAILS values('Stella Khristi', '3D Artist', 'Sofware Engineer', '3')"""
)
cursor.execute(
    """Insert Into PERSON_DETAILS values('Max Khristi', 'Full Stack Developer', 'Jr. Sofware Engineer', '1')"""
)

# DISPLAY ALL THE REDORDS

print(" The inserted records are: ")

data = cursor.execute("""Select * From PERSON_DETAILS""")

for row in data:
    print("----->", row)


# AFTER ALL OPRATIONS CLOSE THE CONNECTION

connection.commit()
connection.close()
