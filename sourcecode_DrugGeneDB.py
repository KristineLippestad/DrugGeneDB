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
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated disease table"""

    create_connection(db_file)
    diseaseID_List = []
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(OTP_file, None) #skip the headers
        for row in tsv_file:
            diseaseID = row[0]
            name = row[1]
            #If statement could have been replaced with INSERT OR REPLACE to make the code more readable, but it gives a considerable longer run time.
            if diseaseID not in diseaseID_List:
                diseaseID_List.append(diseaseID)
                cursor.execute("INSERT INTO Disease VALUES (?, ?)", (diseaseID, name))
                con.commit()
    con.close()

#Write drugs to database
def insertDrugInputsIntoDrug(db_file, OTP_file):
    """Write diseaseId, diseaseName, type and mechanism of action to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated disease table"""

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

#Write genes to database
def insertGeneInputsIntoDrug(db_file, OTP_file):
    """Write GeneCardsSymbol, and geneName to Gene table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated gene table"""

    create_connection(db_file)
    geneCardsSymbol_List = []
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            geneCardsSymbol = row[7]
            uniprotID = None
            geneName = row[8]

            if geneCardsSymbol not in geneCardsSymbol_List:
                geneCardsSymbol_List.append(geneCardsSymbol)
                cursor.execute("INSERT INTO Gene VALUES (?, ?, ?)", (geneCardsSymbol, uniprotID, geneName))
                con.commit()
    con.close()


#Write gene associations to database
def insertGeneAssociationInputsIntoGeneAssociation(db_file, OTP_file):
    """Write geneCardsSymbol and diseaseID  to GeneAssociation table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated GeneAsssociation table"""

    create_connection(db_file)

    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            geneCardsSymbol = row[7]
            diseaseID = row[0]
            cursor.execute("INSERT OR REPLACE INTO GeneAssociation VALUES (?, ?)", (geneCardsSymbol, diseaseID))
            con.commit()
    con.close()

#Write interactions to database
def insertInteractionInputsIntoInteraction(db_file, OTP_file):
    """Write GeneCardsSymbol, drugID, actionType and source to Interaction table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated Interaction table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            geneCardsSymbol = row[7]
            drugID = row[2]
            actionType = row[6]
            source = "https://platform.opentargets.org/disease/EFO_0000311"

            cursor.execute("INSERT OR REPLACE INTO Interaction VALUES (?, ?, ?, ?)", (geneCardsSymbol, drugID, actionType, source))
            con.commit()
    con.close()

#Write indicated for to database
def insertIndicatedForInputsIntoDrug(db_file, OTP_file):
    """Write diseaseID, drugID, and phase to IndicatedFor table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated IndicatedFor table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        tsv_file = csv.reader(OTP_file, delimiter="\t")
        next(tsv_file, None) #skip the headers
        for row in tsv_file:
            diseaseID = row[0]
            drugID = row[2]
            phase = row[9]

            cursor.execute("INSERT OR REPLACE INTO IndicatedFor VALUES (?, ?, ?)", (diseaseID, drugID, phase))
            con.commit()
    con.close()


#create_connection("/Users/kristinelippestad/Dokumenter/Master/testDB/TestDrugGeneDB.db")
#con.close()

print("hei")