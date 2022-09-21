from aifc import Error
import sqlite3
import pandas as pd
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
        print("ERROR")

    return con

#Write diseases to databse
def insertDiseaseInputsIntoDisease(db_file, OTP_file, diseaseId, diseaseName):
    """Write diseaseId and diseaseName to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated disease table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            diseaseID = df[diseaseId][ind]
            name = df[diseaseName][ind]
            cursor.execute("INSERT OR REPLACE INTO Disease VALUES (?, ?)", (diseaseID, name))
            con.commit()
    con.close()

#Write drugs to database
def insertDrugInputsIntoDrug(db_file, OTP_file, drugId, drugName, type):
    """Write diseaseId, diseaseName, type and mechanism of action to Disease table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated disease table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            drugID = df[drugId][ind]
            name = df[drugName][ind]
            moleculeType = df[type][ind]
            cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, moleculeType))
            con.commit()
    con.close()

#Write genes to database
def insertGeneInputsIntoGene(db_file, OTP_file, geneCardSymbol, geneName):
    """Write GeneCardsSymbol, and geneName to Gene table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated gene table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            symbol = df[geneCardSymbol][ind]
            uniprotID = None
            name = df[geneName][ind]
            cursor.execute("INSERT OR REPLACE INTO Gene VALUES (?, ?, ?)", (symbol, uniprotID, name))
            con.commit()
    con.close()


#Write gene associations to database
def insertGeneAssociationInputsIntoGeneAssociation(db_file, OTP_file, geneCardSymbol, diseaseId):
    """Write geneCardsSymbol and diseaseID  to GeneAssociation table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated GeneAsssociation table"""

    create_connection(db_file)

    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            symbol = df[geneCardSymbol][ind]
            diseaseID = df[diseaseId][ind]
            cursor.execute("INSERT OR REPLACE INTO GeneAssociation VALUES (?, ?)", (symbol, diseaseID))
            con.commit()
    con.close()

#Write interactions to database
def insertInteractionInputsIntoInteraction(db_file, OTP_file, geneCardSymbol, drugId, mechanismOfAction, actionType, phase):
    """Write GeneCardsSymbol, drugID, actionType and source to Interaction table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated Interaction table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            symbol = df[geneCardSymbol][ind]
            drugID = df[drugId][ind]
            MOA = df[mechanismOfAction][ind]
            actType = df[actionType][ind]
            Phase = df[phase][ind]
            source = "https://platform.opentargets.org/disease/EFO_0000311"

            cursor.execute("INSERT OR REPLACE INTO Interaction VALUES (?, ?, ?, ?, ?, ?)", (symbol, drugID, MOA, actType, Phase, source))
            con.commit()
    con.close()

#Write indicated for to database
def insertIndicatedForInputsIntoIndicatedFor(db_file, OTP_file, diseaseId, drugId):
    """Write diseaseID, drugID, and phase to IndicatedFor table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated IndicatedFor table"""

    create_connection(db_file)
    with open(OTP_file, "r") as OTP_file:
        df = pd.read_csv(OTP_file, delimiter="\t")
        for ind in df.index:
            diseaseID = df[diseaseId][ind]
            drugID = df[drugId][ind]

            cursor.execute("INSERT OR REPLACE INTO IndicatedFor VALUES (?, ?)", (diseaseID, drugID))
            con.commit()
    con.close()


create_connection("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db")
#insertDiseaseInputsIntoDisease("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'diseaseId', 'diseaseName')
#insertDrugInputsIntoDrug("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'drugId', 'drugName', 'type')
#insertGeneInputsIntoGene("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'symbol', 'name')
#insertGeneAssociationInputsIntoGeneAssociation("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'symbol', 'diseaseId')
#insertInteractionInputsIntoInteraction("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'symbol', 'drugId', 'mechanismOfAction', 'actionType', 'phase')
#insertIndicatedForInputsIntoIndicatedFor("/Users/kristinelippestad/Dokumenter/Master/Test_DB.db", "/Users/kristinelippestad/Downloads/EFO_0000311-known-drugs.tsv", 'diseaseId', 'drugId')
#con.close()
