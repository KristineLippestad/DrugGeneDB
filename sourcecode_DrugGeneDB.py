import sqlite3

import csv

#Connect to the database
def create_connection(db_file):
    """Create a database connection to the SQLite database given by the db_file
    :param db_file: database db_file
    :return: Connection object or None"""

    global con
    global cursor

    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()
        print("Successfully connected to SQLite")
    except Error as e:
        print(e)

    return con

#Write disease to databse
def insertDiseaseInputsIntoDisease(db_file, EFO_file):
    """Write diseaseId and diseaseName to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, EFO_file: tsv file from Open Target Platform
    :return: dabase with updated disease table"""
      
    create_connection(db_file)
    EFO_List = []
    with open(EFO_file, "r") as EFO_file:
        tsv_file = csv.reader(EFO_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            EFO = row[0]
            name = row[1]
            if EFO not in EFO_List:
                EFO_List.append(EFO)
                cursor.execute("INSERT INTO Disease VALUES (?, ?)", (EFO, name))
                con.commit()
    con.close()


insertDiseaseInputsIntoDisease("/Users/kristinelippestad/Dokumenter/Master/testDB/TestDrugGeneDB.db", "/Users/kristinelippestad/downloads/EFO_0000311-known-drugs.tsv")
