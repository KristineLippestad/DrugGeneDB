from aifc import Error
import sqlite3
from typing import Type
from unittest import skip
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

def insertGeneInputsIntoGene(db_file, uniProt_file, entry, HGNC, proteinName, organism):
    """Write HGNC, UniProtID, name and organism to Gene table from tsv file collected from the UniProt.
    :param db_file: database db_file, uniProt_file: tsv file from UniProt, entry: volumn name for entry in uniProt_file, HGNC: column name for symbol in uniProt_file, geneName: column name for gene name in uniProt_file, organism: column name for organism in uniProt_file
    :return: database with updated gene table"""

    create_connection(db_file)
    with open(uniProt_file, "r") as uniProt_file:
        df = pd.read_csv(uniProt_file, delimiter="\t")
        for ind in df.index:
            symbol = str(df[HGNC][ind])
            uniprotID = df[entry][ind]
            name = df[proteinName][ind]
            org = (df[organism][ind]).replace(' (Human)', "")

            cursor.execute("INSERT OR REPLACE INTO Gene VALUES (?, ?, ?, ?)", (symbol, uniprotID, name, org))
            con.commit()
    con.close()

insertGeneInputsIntoGene("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/GeneFile.tsv", "Entry", "Gene Names (primary)", "Protein names", "Organism")


