import sqlite3
from aifc import Error
import pandas as pd

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
        print("ERROR")

    return con

"""
def smallMoleculeAndTargets(db_file, HGNC, type):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, HGNC FROM Drug NATURAL INNER JOIN Interaction WHERE HGNC = ? and type = ?", (HGNC, type)):
        print(row)
    con.close()
"""

def smallMoleculeAndTargets(db_file, HGNC, type):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    #Kan dette gjøres om til en spørring?
    drugList = []
    for row in cursor.execute("SELECT Drug.drugID FROM Drug NATURAL INNER JOIN Interaction WHERE HGNC = ? and type = ?", (HGNC, type)):
        s = str(row)
        drugList.append(s.strip("'(,)"))
    for i in drugList:
        for r in cursor.execute("SELECT drugName, Drug.drugID, actionType, HGNC FROM Drug NATURAL INNER JOIN Interaction WHERE Drug.drugID = ?", (i, )):
            print(r)
    con.close()
"""
def twoTargets(db_file, targetOne, targetTwo):
#Drugs that target two genes of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, HGNC FROM Drug NATURAL INNER JOIN Interaction WHERE HGNC = ? INTERSECT SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol = ?", (targetOne, targetTwo)):
        print(row)
    con.close()
"""

def twoTargets(db_file, targetOne, targetTwo):
#Drugs that target two genes of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, HGNC FROM Drug NATURAL INNER JOIN Interaction WHERE HGNC IN (SELECT drugID FROM Interaction WHERE GeneCardsSymbol IN (?,?))", (targetOne, targetTwo)):
        print(row)
    con.close()

"""
def drug(db_file, drugName):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT * FROM Drug WHERE drugName = ? and type = 'Small molecule'", (drugName, )):
        print(row)
    con.close()
"""

def drug(db_file, file_name, drugName):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    cursor.execute("SELECT * FROM Drug WHERE drugName = ? and type = 'Small molecule'", (drugName, ))
    df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "drugName", "type"])
    drugPanel(file_name, df)
    con.close()

"""
def drugPanel(fileName, query):
    with open(fileName, 'w') as f:
        f.write("#Name\tEffect\tTarget") # Retrieve all targets for a given compound.
        for row in query:
            print(row)
            print(type(row))
            drugId = row["drugID"]
            targetList = []
            for r in cursor.execute("SELECT drugID, actionType, HGNC FROM Interaction WHERE drugID = ?", drugId):
                aType = row["actionType"]
                targetList.append(row["HGNC"])
            targetList.clear()
            f.write(drugId + "\t" + aType + "\t" + targetList + "\t".join(targetList) + "\n")
    f.close()
"""

def drugPanel(fileName, df):
    with open(fileName, 'w') as f:
        f.write("#Name\tTarget" + "\n") # Retrieve all targets for a given compound.
        for ind in df.index:
            drugId = df["drugID"][ind]
            targetList = []
            cursor.execute("SELECT drugID, actionType, HGNC FROM Interaction WHERE drugID = ?", (drugId, ))
            df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "actionType", "HGNC"])
            for i in df2.index:
                aType = df2["actionType"][i]
                if aType == "Inhibitor":
                    aT = "inhibits"
                targetList.append(df2["HGNC"][i])
            f.write(drugId + "\t" + aT + "\t" + "\t".join(targetList) + "\n")
            targetList.clear()
    f.close()

#smallMoleculeAndTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'Small molecule')
#twoTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'CSF1R')
drug('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db','drug.txt','VATALANIB')