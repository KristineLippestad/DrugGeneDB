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

def twoTargets(db_file, targetOne, targetTwo):
#Drugs that target two genes of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, HGNC FROM Drug NATURAL INNER JOIN Interaction WHERE HGNC IN (SELECT drugID FROM Interaction WHERE GeneCardsSymbol IN (?,?))", (targetOne, targetTwo)):
        print(row)
    con.close()


def drug(db_file, file_name, drugName):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    cursor.execute("SELECT * FROM Drug WHERE drugName = ? and type = 'Small molecule'", (drugName, ))
    df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "drugName", "type"])
    print(df)
    drugPanel(file_name, df)
    con.close()

def drugPanel(fileName, df):
    with open(fileName, 'w') as f:
        f.write("#Name\tTarget" + "\n") # Retrieve all targets for a given compound.
        for ind in df.index:
            drugId = df["drugID"][ind]
            targetList = []
            cursor.execute("SELECT drugID, actionType, HGNC FROM Interaction WHERE drugID = ?", (drugId, ))
            df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "actionType", "HGNC"])
            print(df2)
            for i in df2.index:
                aType = df2["actionType"][i]
                if aType == "Inhibitor":
                    aT = "inhibits"
                targetList.append(df2["HGNC"][i])
            f.write(drugId + "\t" + aT + "\t" + "\t".join(targetList) + "\n")
            targetList.clear()
    f.close()

def targetProfile(db_file, file_name, id, limit):
    create_connection(db_file)
    cursor.execute("SELECT DISTINCT Interaction.drugID, actionType, Interaction.HGNC FROM ((Interaction INNER JOIN MeasuredFor ON Interaction.DrugID = MeasuredFor.DrugID) INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID) WHERE Interaction.DrugID = ? and  Kd_max < ?", (id, limit))
    df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "actionType", "HGNC"])
    drugPanelTP(file_name, df)
    con.close()

def drugPanelTP(fileName, df):
    with open(fileName, 'w') as f:
        f.write("#Name\tTarget" + "\n") # Retrieve all targets for a given compound.
        targetList = []
        try:
            for ind in df.index:
                drugId = df["drugID"][ind]
                aType = df["actionType"][ind]
                if aType == "Inhibitor":
                    aT = "inhibits"
                print(df["HGNC"][ind])
                targetList.append(df["HGNC"][ind])
            f.write(drugId + "\t" + aT + "\t" + "\t".join(targetList) + "\n")
        except:
            print("No interactions with binding affinity measured below the given limit value.") 
    f.close()


#smallMoleculeAndTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'Small molecule')
#twoTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'CSF1R')
#drug('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db','drugTests.txt','SUNITINIB')
targetProfile('/Users/kristinelippestad/Dokumenter/Master/DTP.db', '/Users/kristinelippestad/Dokumenter/Master/drugT4.txt', 'CHEMBL6', 10)