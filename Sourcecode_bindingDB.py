from cmath import nan
import pandas as pd
from aifc import Error
import sqlite3
import math


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


def insertBindingAffinity(db_file, binding_dataset, drugId, upId, Kd, Ki, IC50, pH, Temperature, Organism, Source):
    create_connection(db_file)
    cursor.execute("SELECT UniProtID, HGNC FROM Gene;")
    gene_dict = {}
    dtp_dict = {}
    for (UniProtID, HGNC) in cursor:
        gene_dict[UniProtID] = HGNC
    with open(binding_dataset, "r") as binding_dataset:
        df = pd.read_csv(binding_dataset, delimiter="\t", on_bad_lines='skip')
        for ind in df.index:
            dID = df[drugId][ind]
            UniProtID = df[upId][ind]
            hgnc = gene_dict.get(UniProtID)
            kd = str(df[Kd][ind])
            if kd == "nan":
                kd = None
            ki = str(df[Ki][ind])
            if ki == "nan":
                ki = None
            ic50 = str(df[IC50][ind])
            if ic50 == "nan":
                ic50 = None
            ph = df[pH][ind]
            temp = str(df[Temperature][ind]).replace(" C", "")
            temp = float(temp)
            org = df[Organism][ind]
            source = str(df[Source][ind])
            cursor.execute("SELECT * FROM Interaction WHERE DrugID = ? and HGNC = ?", (dID, hgnc))
            row = cursor.fetchone()
            
            if row != None and (kd != None or ki != None or ic50 != None):
                print(row)
                dtp = hgnc + "_" + dID
                if dtp in dtp_dict.keys():
                    a = dtp_dict.get(dtp)
                    dtp_dict[dtp] = a + 1
                    bindingReactionID = hgnc + "_" + dID + "_" + str(a + 1)
                    cursor.execute("INSERT OR REPLACE INTO MeasuredFor VALUES (?, ?, ?)", (hgnc, dID, bindingReactionID))
                    cursor.execute("INSERT OR REPLACE INTO BindingAffinity VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (bindingReactionID, kd, ki, ic50, ph, temp, org, source))
                else:
                    
                    dtp_dict[dtp] = 1
                    bindingReactionID = hgnc + "_" + dID + "_1" 
                    print("hgnc: ", hgnc, type(hgnc))
                    print("dID: ", dID, type(dID)) 
                    print("BindingReactionID: ", bindingReactionID, type(bindingReactionID))
                    print("Kd: ", kd, type(kd))
                    print("Ki: ", ki, type(ki))
                    print("ic50: ", ic50, type(ic50))
                    print("ph: ", ph, type(ph))
                    print("temp: ", temp, type(temp))
                    print("org: ", org, type(org))
                    print("source: ", source, type(kd))
                    cursor.execute("INSERT OR REPLACE INTO MeasuredFor VALUES (?, ?, ?)", (hgnc, dID, bindingReactionID))
                    cursor.execute("INSERT OR REPLACE INTO BindingAffinity VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (bindingReactionID, kd, ki, ic50, ph, temp, org, source))
        con.commit()
    con.close()

insertBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DTP.db", "/Users/kristinelippestad/Downloads/BindingDB_All.tsv", "ChEMBL ID of Ligand", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")