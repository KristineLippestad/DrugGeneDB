from cmath import nan
import pandas as pd
from aifc import Error
import sqlite3

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
    """Write BindingReactionID, Kd_min, Kd_max, Ki_min, Ki_max, IC50_min, IC50_max, pH, Temperature, Organism and Source to BindingAffinity table.
    Write HGNC, DrugID, BindingReactionID to MeasuredFor table.
    :param db_file: database db_file, binding_dataset: tsv file collected from BindingDB, Download page ("BindingDB_All_2022m10.tsv.zip") representing the binding affinity measurments,
                    drugID: column name for ChEMBL ID in binding_dataset, upId: column name for UniProtID in binding_dataset, Kd: column name for Kd in binding_dataset, Ki: column name for Ki in binding_dataset, IC50: column name for IC50 in binding_dataset,
                    pH: column name for pH in binding_dataset, Temperature: column name for Tempterature in binding_dataset, Organism: column name for Organism in binding_dataset, Source: column name for source in binding_dataset
    :return: database with updated BindingAffinity and MeasuredFor table"""

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
                kd_min = kd
                kd_max = kd
            elif "<" in kd:
                kd_min = 0
                kd_max = kd[1:]
            elif ">" in kd:
                kd_min = kd[1:]
                kd_max = float('inf')
            else:
                kd_min = kd
                kd_max = kd
            ki = str(df[Ki][ind])
            if ki == "nan":
                ki = None
                ki_min = ki
                ki_max = ki
            elif "<" in ki:
                ki_min = 0
                ki_max = ki[1:]
            elif ">" in ki:
                ki_min = ki[1:]
                ki_max = float('inf')
            else:
                ki_min = ki
                ki_max = ki
            ic50 = str(df[IC50][ind])
            if ic50 == "nan":
                ic50 = None
                ic50_min = ic50
                ic50_max = ic50
            elif "<" in ic50:
                ic50_min = 0
                ic50_max = ic50[1:]
            elif ">" in ic50:
                ic50_min = ic50[1:]
                ic50_max = float('inf')
            else:
                ic50_min = ic50
                ic50_max = ic50
            ph = df[pH][ind]
            temp = str(df[Temperature][ind]).replace(" C", "")
            temp = float(temp)
            org = df[Organism][ind]
            source = df[Source][ind]
            #cursor.execute("SELECT * FROM Interaction WHERE DrugID = ? and HGNC = ?", (dID, hgnc))
            cursor.execute("SELECT * FROM Drug WHERE DrugID = ?", (dID, ))
            row = cursor.fetchone()
            cursor.execute("SELECT * FROM Gene WHERE HGNC = ?", (hgnc, ))
            r = cursor.fetchone()

            if (row != None and r != None) and (kd != None or ki != None or ic50 != None):
                dtp = hgnc + "_" + dID
                if dtp in dtp_dict.keys():
                    a = dtp_dict.get(dtp)
                    dtp_dict[dtp] = a + 1
                    bindingReactionID = hgnc + "_" + dID + "_" + str(a + 1)
                    cursor.execute("INSERT OR REPLACE INTO MeasuredFor VALUES (?, ?, ?)", (hgnc, dID, bindingReactionID))
                    cursor.execute("INSERT OR REPLACE INTO BindingAffinity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (bindingReactionID, kd_min, kd_max, ki_min, ki_max, ic50_min, ic50_max, ph, temp, org, source))
                else:  
                    dtp_dict[dtp] = 1
                    bindingReactionID = hgnc + "_" + dID + "_1" 
                    cursor.execute("INSERT OR REPLACE INTO MeasuredFor VALUES (?, ?, ?)", (hgnc, dID, bindingReactionID))
                    cursor.execute("INSERT OR REPLACE INTO BindingAffinity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (bindingReactionID, kd_min, kd_max, ki_min, ki_max, ic50_min, ic50_max, ph, temp, org, source))
        con.commit()
    con.close()

insertBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DTP.db", "/Users/kristinelippestad/Downloads/BindingDB_All.tsv", "ChEMBL ID of Ligand", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")