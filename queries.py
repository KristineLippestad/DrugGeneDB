import sqlite3
from aifc import Error

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
def smallMoleculeAndTargets(db_file, geneCardsSymbol, type):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol = ? and type = ?", (geneCardsSymbol, type)):
        print(row)
    con.close()
"""

def smallMoleculeAndTargets(db_file, geneCardsSymbol, type):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    #Kan dette gjøres om til en spørring?
    drugList = []
    for row in cursor.execute("SELECT Drug.drugID FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol = ? and type = ?", (geneCardsSymbol, type)):
        s = str(row)
        drugList.append(s.strip("'(,)"))
    for i in drugList:
        for r in cursor.execute("SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE Drug.drugID = ?", (i, )):
            print(r)
    con.close()
"""
def twoTargets(db_file, targetOne, targetTwo):
#Drugs that target two genes of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol = ? INTERSECT SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol = ?", (targetOne, targetTwo)):
        print(row)
    con.close()
"""

def twoTargets(db_file, targetOne, targetTwo):
#Drugs that target two genes of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT drugName, Drug.drugID, actionType, GeneCardsSymbol FROM Drug NATURAL INNER JOIN Interaction WHERE GeneCardsSymbol IN (SELECT drugID FROM Interaction WHERE GeneCardsSymbol IN (?,?))", (targetOne, targetTwo)):
        print(row)
    con.close()

def drug(db_file):
#Drugs that are small molecules and target a gene of interest.
    
    create_connection(db_file)
    for row in cursor.execute("SELECT type FROM Drug WHERE drugName = ?", ['AFATINIB']):
        print(row)
    con.close()

def drugPanel(fileName, results)
    with open(fileName, 'w') as f:
        f.write("#Name\tEffect\tTarget")
        for row in results:
            f.write("%s\t" % str(row))


#smallMoleculeAndTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'Small molecule')
twoTargets('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db', 'FLT4', 'CSF1R')
#drug('/Users/kristinelippestad/Dokumenter/Master/Test_DB.db')