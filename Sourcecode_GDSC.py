from aifc import Error
import sqlite3
from unittest import skip
import pandas as pd


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

#Write drugs to database
def insertDrugs(db_file, gdsc_file, drugName):
    """Write drugID, drug name, and type to drug table from tsv file collected from the Genomics of Drug Sensitivity in Cancer (GDSC).
    :param db_file: database db_file, gdsc_file: tsv file from GDSC representing the compounds, drugName: columnname for drug name in gdsc file. 
    :return: database with updated drug table"""
    
    a = 0

    create_connection(db_file)
    with open(gdsc_file, "r") as gdsc_file:
        df = pd.read_csv(gdsc_file, delimiter="\t")
        for ind in df.index:
            name = str(df[drugName][ind]).upper()
            drugID = str([k for k, v in drug_dict.items() if name in v]).strip("[']")
            # Verify whether name is in the list of values for each key
            if any(name in sublist for sublist in smallMolecule_dict.values()): # Retrive chembl ID from name + synonyms (get key from value where value is in a list)
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Small molecule'))
            elif any(name in sublist for sublist in protein_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Protein'))
            elif any(name in sublist for sublist in unknown_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Unknown'))
            elif any(name in sublist for sublist in cell_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Cell'))
            elif any(name in sublist for sublist in antibody_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Antibody'))
            elif any(name in sublist for sublist in oligonucleotide_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Oligonucleotide'))
            elif any(name in sublist for sublist in enzyme_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Enzyme'))
            elif any(name in sublist for sublist in oligosaccharide_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Oligosaccharide'))
            elif any(name in sublist for sublist in gene_dict.values()):
                cursor.execute("INSERT OR REPLACE INTO Drug VALUES (?, ?, ?)", (drugID, name, 'Gene'))
            else:
                a += 1
            con.commit()
    
    print(a, " drugs were not included.")
    con.close()

def chemblID_dict(drug_file, drugId, Synonyms):
    """Write a dictionary with drugIDs from ChEMBL as key and compound synonyms as value.
    :param db_file: drug_file: tsv file from ChEMBL representing the compounds, retrieved from https://www.ebi.ac.uk/chembl/g/#browse/compounds, drugId: column name for drug ID, Synonyms: column name for synonyms.
    :return: dictionary with drugIDs from ChEMBL as key and compound synonyms as value"""
    drug_dict = {}

    with open(drug_file, "r") as drug_file:
        df = pd.read_csv(drug_file, delimiter="\t")
        for ind in df.index:
            drugID = df[drugId][ind]
            synonyms = df[Synonyms][ind]
            synonyms = str(synonyms)
            synonyms_list = synonyms.split("|")
            drug_dict[drugID] = synonyms_list

    return drug_dict

drug_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_drug.tsv", "Parent Molecule", "Synonyms")
smallMolecule_dict = chemblID_dict("/Users/kristinelippestad/Dokumenter/Master/chembl_smallmolecule.tsv", "Parent Molecule", "Synonyms")
protein_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_protein.tsv", "Parent Molecule", "Synonyms")
unknown_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_unknown.tsv", "Parent Molecule", "Synonyms")
cell_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_cell.tsv", "Parent Molecule", "Synonyms")
antibody_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_antibody.tsv", "Parent Molecule", "Synonyms")
oligonucleotide_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_oligonucleotide.tsv", "Parent Molecule", "Synonyms")
enzyme_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_enzyme.tsv", "Parent Molecule", "Synonyms")
oligosaccharide_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_oligosaccharide.tsv", "Parent Molecule", "Synonyms")
gene_dict = chemblID_dict("/Users/kristinelippestad/Downloads/chembl_gene.tsv", "Parent Molecule", "Synonyms")


def insertGeneInputsIntoGene(db_file, gdsc_file, target, geneName):
    """Write GeneCardsSymbol, and geneName to Gene table from tsv file collected from the Open Target Platform
    :param db_file: database db_file, OTP_file: tsv file from Open Target Platform
    :return: database with updated gene table"""

    create_connection(db_file)
    with open(gdsc_file, "r") as gdsc_file:
        df = pd.read_csv(gdsc_file, delimiter="\t")
        for ind in df.index:
            targets = df[target][ind]
            target_list = targets.split(", ")
            for t in target_list:
                symbol = t #fikse dette
                uniprotID = None 
                name = df[name][ind] #Fikse dette
                cursor.execute("INSERT OR REPLACE INTO Gene VALUES (?, ?, ?)", (symbol, uniprotID, name))
                con.commit()
    con.close()

def targetList(gdsc_file, path, target):
    target_list = []
    with open(gdsc_file, "r") as gdsc_file:
        df = pd.read_csv(gdsc_file, delimiter="\t")
        for ind in df.index:
            t = str(df[target][ind])
            substring = ", "
            if substring in t:
                targets = t.split(", ")
                t_add = list(set(target_list) - set(targets))
                if t_add != "": 
                    target_list.extend(t_add)
            else:
                if t not in target_list: 
                    target_list.append(t)
    
    with open(path, "w") as f:
        for item in set(target_list):
            #write each item to new line
            f.write("%s\n" % item)
        f.close()
    
    return(set(target_list))

    # write this list to a text file where the elements are separated with blankspaces that can be uploaded in uniprot

targetList("/Users/kristinelippestad/Downloads/gdsc_druglist.tsv", "/Users/kristinelippestad/Dokumenter/Master/targets.txt", " Targets")


def insertCellLines(db_file, gdsc_file, clo_file, name, tissue, tissueSubType, cloId, cloName, tcga):
    """Write CLO, cell line name, tissue type, tissue sub-type and diseaseID to CellLine table.
    :param db_file: database db_file, gdsc_file: tsv file collected from the Genomics of Drug Sensitivity in Cancer (GDSC) representing the cell lines, clo_file: Cell Line Ontology (CLO) csv file downloaded from https://bioportal.bioontology.org/ontologies/CLO, 
                    name: column name for cell line name in gdsc_file, tissue: column name for tissue in gdsc_file, tissueSubType: column name for tissue subtype in gdsc_file, cloId: column name for CLO id, cloName: column name for cell line name in clo file, tcga: column name tcga classification in gdsc file. 
    :return: database with updated cellLine table"""
    create_connection(db_file)
    with open(gdsc_file, "r") as gdscFile:
        df = pd.read_csv(gdscFile, delimiter="\t")
        clo_dict = cloDict(clo_file, cloId, cloName)
        dis_dict = disease_dict(gdsc_file, tcga)
        for ind in df.index:
            cellLineName = df[name][ind]
            tissueName = str(df[tissue][ind]).replace("_", " ")
            tissueSubtypeName = str(df[tissueSubType][ind]).replace("_", " ")
            clo = str([k for k, v in clo_dict.items() if cellLineName in v]).strip("[']")
            diseaseID = dis_dict.get((df[tcga][ind]), None)
            if clo.find("', '"):
                clo_list = clo.split("', '")
                for i in clo_list:
                    cursor.execute("INSERT OR REPLACE INTO CellLine VALUES (?, ?, ?, ?, ?)", (i, cellLineName, tissueSubtypeName, tissueName, diseaseID))
            elif clo == "": # Check this again
                s = " ".join(["Type in the correct clo for ", cellLineName, " (on the formate: CLO_0001199): "])
                id = input(s)
                if id == "":
                    continue
                else:
                    cursor.execute("INSERT OR REPLACE INTO CellLine VALUES (?, ?, ?, ?, ?)", (id, cellLineName, tissueSubtypeName, tissueName, diseaseID))
            else: 
                cursor.execute("INSERT OR REPLACE INTO CellLine VALUES (?, ?, ?, ?, ?)", (clo, cellLineName, tissueSubtypeName, tissueName, diseaseID))
            con.commit()
    con.close()

def cloDict(clo_file, cloId, name):
    """Make a dictionary with name of cell line ontology id as keys and cell line synonyms as values. 
    :param clo: clo_file: Cell Line Ontology (CLO) csv file downloaded from https://bioportal.bioontology.org/ontologies/CLO, cloId: column name for CLO id, cloName: column name for cell line name in clo file
    :return: dictionary with cell line ontology id as key and cell line synonyms as value. 
    """
    clo_dict = {}

    with open(clo_file, "r") as clo_file:
        df = pd.read_csv(clo_file, delimiter=",")
        for ind in df.index:
            cloID = str(df[cloId][ind]).strip("http://purl.obolibrary.org/obo/")
            Name = str(df[name][ind]).split("|")
            clo_dict[cloID] = Name

    return clo_dict

def disease_dict(gdsc_file, TCGA):
    tcga_list = []
    disease_dict = {}
    with open(gdsc_file, "r") as gdsc_f:
        df = pd.read_csv(gdsc_f, delimiter="\t")
        for ind in df.index:
            tcga = str(df[TCGA][ind])
            if tcga not in tcga_list:
                tcga_list.append(tcga)
    print(tcga_list)

    disease_dict["PRAD"] = "EFO_0000673" 
    disease_dict["STAD"] = "EFO_0000503" 
    disease_dict["GBM"] = "EFO_0000519"
    disease_dict["SKCM"] = "EFO_0000389"
    disease_dict["BLCA"] = "EFO_0006544"
    disease_dict["UNCLASSIFIED"] = None
    disease_dict["KIRC"] = "EFO_0000349"
    disease_dict["THCA"] = "EFO_0002892"
    disease_dict["DLBC"] = "EFO_0000403"
    disease_dict["LUAD"] = "EFO_0000571"
    disease_dict["ALL"] = "EFO_0000220"
    disease_dict["MM"] = "EFO_0001378"
    disease_dict["UCEC"] = "EFO_1000238"
    disease_dict["BRCA"] = "EFO_1000307"
    disease_dict["PAAD"] = "EFO_1000044"
    disease_dict["HNSC"] = "EFO_0000181"
    disease_dict["NB"] = "EFO_0000621"
    disease_dict["nan"] = None
    disease_dict["LCML"] = "EFO_0000339"
    disease_dict["CESC"] = "EFO_0001061" #EFO for cervical carcinoma which is a carcinoma arising from either the exocervical squamous epithelium or the endocervical glandular epithelium
    disease_dict["LCML"] = "EFO_0000339"
    disease_dict["COREAD"] = "EFO_0000365" #Colon adenocarcinoma and rectum adenocarcinoma (COREAD) is given EFO for colorectal cancer, which starts in the colon or the rectum. 
    disease_dict["LIHC"] = "EFO_0000182"
    disease_dict["LAML"] = "EFO_0000222"
    disease_dict["SCLC"] = "EFO_0000702"
    disease_dict["ESCA"] = "EFO_0002916"
    disease_dict["OV"] = "EFO_1000043"
    disease_dict["MB"] = "EFO_0002939"
    disease_dict["LGG"] = "MONDO_0005499"
    disease_dict["LUSC"] = "EFO_0000708"
    disease_dict["CLL"] = "EFO_0000095"
    disease_dict["MESO"] = "EFO_0000588"
    disease_dict["OTHER"] = None
    disease_dict["ACC"] = "EFO_1000796"

    disease_list = list(disease_dict.keys())
    if set(disease_list) == set(tcga_list):
        print("All TCGA classifications are included in the dictionary")
    else:
        notIncluded = list(set(tcga_list).difference(disease_list))
        print(notIncluded, "are not included in the dictionary.")

    return disease_dict

def insertSensitivity(db_file, gdsc_dataset, clo_file, drug_file, cloId, cloName, drugId, Synonyms, cl_name, drugName, ic50, AUC, dataset):
    """Write CLO, drug ID, IC50, AUC, and source into Sensitivity table.
    :param db_file: database db_file, gdsc_file: tsv file collected from the Genomics of Drug Sensitivity in Cancer (GDSC) representing the cell lines, clo_file: Cell Line Ontology (CLO) csv file downloaded from https://bioportal.bioontology.org/ontologies/CLO, drug_file: tsv file from ChEMBL representing the compounds, retrieved from https://www.ebi.ac.uk/chembl/g/#browse/compounds, 
                    cloId: column name for CLO id, cloName: column name for cell line name in clo file, drugId: column name for drug ID in drug file, Synonyms: column name for synonyms in drug file, cl_name: column name for cell line in gdsc_dataset, drugName: column name for drug name in gdsc_dataset, ic50: column name for IC50 in gdsc_dataset, AUC: column name for AUC in gdsc_dataset, dataset: column name for datasets in gdsc_dataset.
    :return: database with updated Sensitivity table"""
    
    create_connection(db_file)
    
    with open(gdsc_dataset, "r") as gdsc_dataset:
        df = pd.read_csv(gdsc_dataset, delimiter=",")
        clo_dict = cloDict(clo_file, cloId, cloName)
        drugID_dict = chemblID_dict(drug_file, drugId, Synonyms)
        for ind in df.index:
            cellLineName = df[cl_name][ind]
            drugname = str(df[drugName][ind]).upper()
            clo = str([k for k, v in clo_dict.items() if cellLineName in v]).strip("[']")
            drugID = str([k for k, v in drugID_dict.items() if drugname in v]).strip("[']")
            ic = df[ic50][ind]
            auc = df[AUC][ind]
            source = df[dataset][ind]
            if clo != "" and drugID != "": 
                substring = "', '"
                if substring in clo:
                    clo_list = clo.split("', '")
                    for i in clo_list:
                        cursor.execute("INSERT OR REPLACE INTO Sensitivity VALUES (?, ?, ?, ?, ?)", (i, drugID, ic, auc, source))
                else: 
                    cursor.execute("INSERT OR REPLACE INTO Sensitivity VALUES (?, ?, ?, ?, ?)", (clo, drugID, ic, auc, source))
            else:
                continue
            con.commit()
    con.close()

insertDrugs("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Downloads/gdsc_druglist.tsv", " Name")
insertCellLines("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Downloads/gdsc_cellLines.tsv", "/Users/kristinelippestad/Downloads/CLO.csv", "Cell line Name", " Tissue", "Tissue sub-type", "Class ID", "Synonyms", " TCGA Classfication")
insertSensitivity("/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db", "/Users/kristinelippestad/Downloads/GDSC2_fitted_dose_response.csv", "/Users/kristinelippestad/Downloads/CLO.csv", "/Users/kristinelippestad/Downloads/chembl_drug.tsv", "Class ID", "Synonyms", "Parent Molecule", "Synonyms", "CELL_LINE_NAME", "DRUG_NAME", "LN_IC50", "AUC", "DATASET")