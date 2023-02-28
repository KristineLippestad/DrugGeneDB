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


def targetProfileFromFile(drugPanelFile, HGNCtoNodeDict, fileName):
    targetProfiles = []
    with open(drugPanelFile, "r") as f:
        for line in f.readlines()[1:]:
            l = line.split("\t")
            drug = l[0]
            targets = l[2:]
            targets[-1] = targets[-1].replace("\n", "")
            print(drug)
            print(f'Targets : {targets}')
            for i in targets:
                if any(i in sublist for sublist in HGNCtoNodeDict.values()):
                    print(i)

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

#CASCADE 1.0
#print('10 nM')
#targetProfileFromFile("/Users/kristinelippestad/Downloads/dp_10nM.txt", cas1_dict, "filt_dp_10nM.txt")

#print('100 nM')
#targetProfileFromFile("/Users/kristinelippestad/Downloads/dp_100nM.txt", cas1_dict, "filt_dp_100nM.txt")

#print('1 uM')
#targetProfileFromFile("/Users/kristinelippestad/Downloads/dp_1uM.txt", cas1_dict, "filt_dp_1uM.txt")

#print('10 uM')
#targetProfileFromFile("/Users/kristinelippestad/Downloads/dp_10uM.txt", cas1_dict, "filt_dp_10uM.txt")

#CASCADE 2.0

print('10 nM')
targetProfileFromFile("/Users/kristinelippestad/Downloads/cas2.0_dp_10nM.txt", cas2_dict, "cas2.0_filt_dp_10nM.txt")

print('100 nM')
targetProfileFromFile("/Users/kristinelippestad/Downloads/cas2.0_dp_100nM.txt", cas2_dict, "cas2.0_filt_dp_100nM.txt")

print('1 uM')
targetProfileFromFile("/Users/kristinelippestad/Downloads/cas2.0_dp_1uM.txt", cas2_dict, "cas2.0_filt_dp_1uM.txt")

print('10 uM')
targetProfileFromFile("/Users/kristinelippestad/Downloads/cas2.0_dp_10uM.txt", cas2_dict, "cas2.0_filt_dp_10uM.txt")




