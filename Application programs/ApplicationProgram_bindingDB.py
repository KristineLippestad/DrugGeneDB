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

def insertBindingAffinity(db_file, binding_dataset, drugId, smiles, inChiKey, upId, Kd, Ki, IC50, pH, Temperature, Organism, Source):
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
            Smiles = df[smiles][ind]
            InChiKey = df[inChiKey][ind]
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
            cursor.execute("SELECT DrugID FROM Drug WHERE DrugID = ? OR Smiles = ? OR InChiKey = ?", (dID, Smiles, InChiKey))
            row = cursor.fetchone()
            if row != None:
                dID = row[0]
            print(dID)
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
                    print(f'HGNC: {hgnc}, drug id: {dID}, binding reaction id: {bindingReactionID}')
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

insertBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "ChEMBL ID of Ligand", "Ligand SMILES", "Ligand InChI Key", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")

insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C7H7N5O2/c1-11-6(13)4-5(10-7(11)14)12(2)9-3-8-4/h3H,1-2H3", "CHEMBL578512", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C29H29N7O2/c1-20-17-24(11-12-25(20)34-29-31-15-13-26(35-29)22-8-5-14-30-19-22)33-28(38)21-7-4-9-23(18-21)32-27(37)10-6-16-36(2)3/h4-15,17-19H,16H2,1-3H3,(H,32,37)(H,33,38)(H,31,34,35)/b10-6+", "CHEMBL2216824", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C19H23F2N5O2/c1-10(2)5-6-26-11(3)18(28)25(4)15-9-22-19(24-17(15)26)23-12-7-13(20)16(27)14(21)8-12/h7-11,27H,5-6H2,1-4H3,(H,22,23,24)", "CHEMBL573107", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C17H18N6/c18-7-5-15(12-3-1-2-4-12)23-10-13(9-22-23)16-14-6-8-19-17(14)21-11-20-16/h6,8-12,15H,1-5H2,(H,19,20,21)/t15-/m1/s1", "CHEMBL1789941", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C20H21N3O2/c1-12-6-5-7-14(21-12)18-17(22-19(23-18)20(2,3)4)13-8-9-15-16(10-13)25-11-24-15/h5-10H,11H2,1-4H3,(H,22,23)", "CHEMBL1824446", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C23H17FN6O/c1-25-22(31)18-6-5-16(11-19(18)24)21-13-28-23-27-12-17(30(23)29-21)10-14-4-7-20-15(9-14)3-2-8-26-20/h2-9,11-13H,10H2,1H3,(H,25,31)", "CHEMBL3188267", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C23H20F3N5O2S2/c1-23(2,3)21-30-18(19(34-21)16-10-11-28-22(27)29-16)12-6-4-9-15(17(12)26)31-35(32,33)20-13(24)7-5-8-14(20)25/h4-11,31H,1-3H3,(H2,27,28,29)", "CHEMBL2028663", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C26H23FIN5O4/c1-13-22-21(23(31(3)24(13)35)30-20-10-7-15(28)11-19(20)27)25(36)33(17-8-9-17)26(37)32(22)18-6-4-5-16(12-18)29-14(2)34/h4-7,10-12,17,30H,8-9H2,1-3H3,(H,29,34)", "CHEMBL2103875", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C31H34F2N6O2/c1-38-8-10-39(11-9-38)25-3-4-26(29(19-25)34-24-6-12-41-13-7-24)31(40)35-30-27-17-20(2-5-28(27)36-37-30)14-21-15-22(32)18-23(33)16-21/h2-5,15-19,24,34H,6-14H2,1H3,(H2,35,36,37,40)", "CHEMBL1983268", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C13H18Cl2N2O2/c14-5-7-17(8-6-15)11-3-1-10(2-4-11)9-12(16)13(18)19/h1-4,12H,5-9,16H2,(H,18,19)/t12-/m0/s1", "CHEMBL852", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C24H23FN4O3/c25-20-8-5-15(14-21-17-3-1-2-4-18(17)22(30)27-26-21)13-19(20)24(32)29-11-9-28(10-12-29)23(31)16-6-7-16/h1-5,8,13,16H,6-7,9-12,14H2,(H,27,30)", "CHEMBL521686", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")
insertByInChIBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Dokumenter/Master/BindingDB_All_02.02.2023.tsv", "InChI=1S/C23H18ClF2N3O3S/c1-2-9-33(31,32)29-19-8-7-18(25)20(21(19)26)22(30)17-12-28-23-16(17)10-14(11-27-23)13-3-5-15(24)6-4-13/h3-8,10-12,29H,2,9H2,1H3,(H,27,28)", "CHEMBL1229517", "UniProt (SwissProt) Primary ID of Target Chain", "Kd (nM)",  "Ki (nM)", "IC50 (nM)", "pH", "Temp (C)", "Target Source Organism According to Curator or DataSource", "Curation/DataSource")

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
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL4522930", "IKBKB", "doi:10.1042/BJ20101701", ic50_min = 380, ic50_max = 380,  pH = 7.5, temp = 30, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL4522930", "IGF1", "doi:10.1042/BJ20101701", ic50_min = 7600, ic50_max = 7600,  pH = 7.5, temp = 30, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL1568415", "MYC", "doi.org/10.1016/j.chembiol.2008.09.011", Kd_min = 4600, Kd_max = 6400, temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL1568415", "MYC", "doi.org/10.1371/journal.pone.0097285", Kd_min = 31600, Kd_max = 47800, temp = 25, Organism = "Homo sapiens")
insertSingleBindingAffinity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "CHEMBL1568415", "MYCN", "doi.org/10.1371/journal.pone.0097285", Kd_min = 31300, Kd_max = 52500, temp = 25, Organism = "Homo sapiens")





