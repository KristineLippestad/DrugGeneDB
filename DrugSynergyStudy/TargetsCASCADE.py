import pandas as pd
import csv

cas1_dict = pd.read_excel('/Users/kristinelippestad/Dokumenter/Master/CompleteProfile/pcbi.1004426.s005.xlsx').set_index('Node')['HGNC symbols'].to_dict()
del cas1_dict["Antisurvival"]
del cas1_dict["Prosurvival"]

#Create a list with all HGNC symbols for each node
for k, v in cas1_dict.items():
    if isinstance(v, str): 
        val = v.split(", ")
        cas1_dict.update({k: val})

cas2_dict = {}
with open("/Users/kristinelippestad/Dokumenter/Master/CompleteProfile/nodes_to_HGNC_CAS2.0.txt", 'r') as f:
    for line in f:
        key, value = line.strip().split("\t")
        cas2_dict[key] = value

del cas2_dict["Node"]

#Create a list with all HGNC symbols for each node
for k, v in cas2_dict.items():
    if isinstance(v, str): 
        val = v.split(", ")
        cas2_dict.update({k: val})

cas2_dict.update({"ACVR1": ["ACVR1B", "ACVR1C"]})

def targetProfileFromFile(drugPanelFile, HGNCtoNodeDict, fileName):
    targetProfiles = []
    with open(drugPanelFile, "r") as f:
        for line in f.readlines()[1:]:
            n = 0
            l = line.split("\t")
            drug = l[0]
            targets = l[2:]
            targets[-1] = targets[-1].replace("\n", "")
            print(drug)
            print(f'Targets : {targets}')
            for i in targets:
                if any(i in sublist for sublist in HGNCtoNodeDict.values()):
                    print(i)
                    n += 1

            p = percentage(n, len(targets))
            print(f'Percentage of targets that are precsented in the network model: {p}')

            targetProfile = set([key for ele in targets for key, val in HGNCtoNodeDict.items() if ele in val])
            if (len(targetProfile) == 0):
                targetProfiles.append(f'{drug}: None of the targets are present in the network')
            else:
                drugPanel(fileName, drug, targetProfile)

def drugPanel(fileName, drug, targets):
    #print(f'targets: {targets}')
    with open(fileName, 'a+') as f:
        f.seek(0)
        first_line = f.readline().rstrip('\n')
        if first_line != "#Name\tTarget":
            f.write("#Name\tTarget" + "\n") 
        try:
            f.write(drug + "\t" + "inhibits" + "\t" + "\t".join(sorted(targets)) + "\n")
        except:
            print(f'No interactions with binding affinity measured below the given limit for {drug}.')
    f.close()

def targetProfile(drugPanel, HGNCtoNodeDict):
    l = drugPanel.split(" inhibits ")
    drug = l[0]
    targets = l[1].split(", ")
    targetProfile= set([key for ele in targets for key, val in cas1_dict.items() if ele in val])

    print(f'{drug}: {targetProfile}')

def percentage(part, whole):
    return 100 * part/whole

"""   
#CASCADE 1.0
print('10 nM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/drugPanel_10nm_cas1.0", cas1_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/filt_dp_10nM_new.txt")

print('100 nM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/drugPanel_100nm_cas1.0", cas1_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/filt_dp_100nM_new.txt")

print('1 uM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/drugPanel_1um_cas1.0", cas1_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/filt_dp_1uM_new.txt")

print('10 uM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/drugPanel_10um_cas1.0", cas1_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels for cascade 1.0 - filt/filt_dp_10uM_new.txt")
"""

#CASCADE 2.0
print('10 nM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/drugPanel_10nM_cas2.0", cas2_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/delete-10")

print('100 nM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/drugPanel_100nM_cas2.0", cas2_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/delete-100")

print('1 uM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/drugPanel_1uM_cas2.0", cas2_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/delete1")

print('10 uM')
targetProfileFromFile("/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/drugPanel_10uM_cas2.0", cas2_dict, "/Users/kristinelippestad/Dokumenter/Master/Synergy study/Drug panels cascade 2.0 - filt/delete10")
