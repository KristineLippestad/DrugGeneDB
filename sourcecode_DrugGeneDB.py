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


#Write diseases to databse
def insertDiseaseInputsIntoDisease(db_file, OTP_file):
    """Write diseaseId and diseaseName to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, EFO_file: tsv file from Open Target Platform
    :return: dabase with updated disease table"""

    create_connection(db_file)
    EFO_List = []
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(OTP_file, None) #skip the headers
        for row in tsv_file:
            EFO = row[0]
            name = row[1]
            if EFO not in EFO_List:
                EFO_List.append(EFO)
                cursor.execute("INSERT INTO Disease VALUES (?, ?)", (EFO, name))
                con.commit()
    con.close()

#Write drugs to database
def insertDrugInputsIntoDrug(db_file, OTP_file):
    """Write diseaseId, diseaseName, type and mechanism of action to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, EFO_file: tsv file from Open Target Platform
    :return: dabase with updated disease table"""

    create_connection(db_file)
    drugID_List = []
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            drugID = row[2]
            drugName = row[3]
            moleculeType = row[4]
            MOA = row[5]

            if drugID not in drugID_List:
                drugID_List.append(drugID)
                cursor.execute("INSERT INTO Drug VALUES (?, ?, ?, ?)", (drugID, drugName, moleculeType, MOA))
                con.commit()
    con.close()
