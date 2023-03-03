import pandas as pd
from aifc import Error
import sqlite3

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

def insertDataToDrug(db_file, chembl_file, drugId, smiles, inChiKey):
    """Write smile and InChi Key to drug table from tsv file collected from ChEMBL.
    :param db_file: database db_file, chembl_file: tsv file from ChEMBL, drugId: column name for drug id in ChEMBL, smiles: column name for smiles in ChEMBL_file, 
    inChiKey: column name for smiles in ChEMBL_file, 
    :return: database with updated Drug table"""

    create_connection(db_file)
    with open(chembl_file, "r") as chembl_file:
        df = pd.read_csv(chembl_file, delimiter="\t")
        for ind in df.index:
            drugID = df[drugId][ind]
            Smiles = df[smiles][ind]
            InChiKey = df[inChiKey][ind]
            cursor.execute("UPDATE Drug SET Smiles = ?, InChiKey = ? WHERE DrugID = ?", (Smiles, InChiKey, drugID))
            con.commit()
            
    con.close()

insertDataToDrug('/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db', '/Users/kristinelippestad/Dokumenter/Master/ChEMBL_drug_file.tsv', 'ChEMBL ID', 'Smiles', 'Inchi Key')