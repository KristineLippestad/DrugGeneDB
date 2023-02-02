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

def insertByInChIBindingAffinity(db_file, binding_dataset, InChi, drugId, upId, Kd, Ki, IC50, pH, Temperature, Organism, Source):

    create_connection(db_file)
    cursor.execute("SELECT UniProtID, HGNC FROM Gene;")
    gene_dict = {}
    dtp_dict = {}
    for (UniProtID, HGNC) in cursor:
        gene_dict[UniProtID] = HGNC

    with open(binding_dataset, "r") as binding_dataset:
        df = pd.read_csv(binding_dataset, delimiter="\t", error_bad_lines=False)
        
        for ind in df.index:
            inChi = df["Ligand InChI"][ind]
            if str(inChi) == InChi: 
                dID = drugId
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
        df = pd.read_csv(binding_dataset, delimiter="\t", error_bad_lines=False)
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

def insertSingleBindingAffinity(db_file, drugID, hgnc, Source, Kd_min = None, Kd_max = None, Ki_min = None, Ki_max = None, ic50_min = None, ic50_max = None, pH = None, temp = None, Organism = None):
    create_connection(db_file)
    cursor.execute("SELECT * FROM Drug WHERE DrugID = ?", (drugID, ))
    row1 = cursor.fetchone()
    cursor.execute("SELECT * FROM Gene WHERE HGNC = ?", (hgnc, ))        
    row2 = cursor.fetchone()
    bindingReaction = hgnc + "_" + drugID + "_" 
    a = 1
    if (row1 != None and row2 != None):
        cursor.execute("SELECT BindingReactionID FROM MeasuredFor WHERE BindingReactionID LIKE ?", (bindingReaction + '%', ))
        df = pd.DataFrame(cursor.fetchall(), columns=["binReaID"])

        if df.empty:
            bindingReactionID = bindingReaction + "1" 
        
        else:
            for ind in df.index:
                s = (str(df["binReaID"][ind])).split("_")
                nr = int(s[-1])
                if nr > a:
                    a = nr
                bindingReactionID = bindingReaction + str(a + 1)

        cursor.execute("INSERT OR REPLACE INTO MeasuredFor VALUES (?, ?, ?)", (hgnc, drugID, bindingReactionID))
        cursor.execute("INSERT OR REPLACE INTO BindingAffinity VALUES (?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?)", (bindingReactionID, Kd_min, Kd_max, Ki_min, Ki_max, ic50_min, ic50_max, pH, temp, Organism, Source))
    
    else:
        print("Drug or target dosen't exist in the database")

    con.commit()
    con.close()

insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C7H7N5O2/c1-11-6(13)4-5(10-7(11)14)12(2)9-3-8-4/h3H,1-2H3", "CHEMBL578512", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C29H29N7O2/c1-20-17-24(11-12-25(20)34-29-31-15-13-26(35-29)22-8-5-14-30-19-22)33-28(38)21-7-4-9-23(18-21)32-27(37)10-6-16-36(2)3/h4-15,17-19H,16H2,1-3H3,(H,32,37)(H,33,38)(H,31,34,35)/b10-6+", "CHEMBL2216824", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C19H23F2N5O2/c1-10(2)5-6-26-11(3)18(28)25(4)15-9-22-19(24-17(15)26)23-12-7-13(20)16(27)14(21)8-12/h7-11,27H,5-6H2,1-4H3,(H,22,23,24)", "CHEMBL573107", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")


insertBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "ChEMBL ID of Ligand", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")

insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "BRAF", "doi:10.1038/nbt1358", Kd_min = 2900, Kd_max = 2900,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "CLK1", "doi:10.1038/nbt1358", Kd_min = 3900, Kd_max = 3900,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "DAPK1", "doi:10.1038/nbt1358", Kd_min = 2400, Kd_max = 2400,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "DAPK2", "doi:10.1038/nbt1358", Kd_min = 2700, Kd_max = 2700,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "DAPK3", "doi:10.1038/nbt1358", Kd_min = 840, Kd_max = 840,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "LIMK2", "doi:10.1038/nbt1358", Kd_min = 3500, Kd_max = 3500,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "CDC42BPA", "doi:10.1038/nbt1358", Kd_min = 1800, Kd_max = 1800,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "MYLK", "doi:10.1038/nbt1358", Kd_min = 1500, Kd_max = 1500,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "PIK3CA", "doi:10.1038/nbt1358", Kd_min = 1.5, Kd_max = 1.5,  temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL573339", "RAF1", "doi:10.1038/nbt1358", Kd_min = 3700, Kd_max = 3700,  temp = 25, Organism = "Homo sapiens")

 




