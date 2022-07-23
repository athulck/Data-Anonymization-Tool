
"""# Anonymization parameters #"""
k = 45           # K-anonymity
l = 2           # L-closeness
t = 0           # T-diversity
epsilon = 0.5   # Epsilon for Differential Privacy
delta = 0.001   # Delta for Differential Privacy


# Just to color the outputs
class Colors:
    """ ANSI color codes """
    BLACK           = "\033[0;30m"
    RED             = "\033[0;31m"
    GREEN           = "\033[0;32m"
    BROWN           = "\033[0;33m"
    BLUE            = "\033[0;34m"
    PURPLE          = "\033[0;35m"
    CYAN            = "\033[0;36m"
    LIGHT_GRAY      = "\033[0;37m"
    DARK_GRAY       = "\033[1;30m"
    LIGHT_RED       = "\033[1;31m"
    LIGHT_GREEN     = "\033[1;32m"
    YELLOW          = "\033[1;33m"
    LIGHT_BLUE      = "\033[1;34m"
    LIGHT_PURPLE    = "\033[1;35m"
    LIGHT_CYAN      = "\033[1;36m"
    LIGHT_WHITE     = "\033[1;37m"
    BOLD            = "\033[1m"
    FAINT           = "\033[2m"
    ITALIC          = "\033[3m"
    UNDERLINE       = "\033[4m"
    BLINK           = "\033[5m"
    NEGATIVE        = "\033[7m"
    CROSSED         = "\033[9m"
    END             = "\033[0m"




#
# Load Dataset
# ------------

import numpy as np
import pandas as pd


# Load the dataset into memory
dataset_path = "adult.sample.csv" #input("Input Dataset Path: ") 
df = pd.read_csv(dataset_path, sep=",", engine="python");

print(" Total number of rows in dataset: ", len(df))


# Check if the dataset is parsed properly
print (df.head())

stepCheck = input ("\nQ> Is your dataset parsed properly? (y/n): ")
if (stepCheck == "n" or stepCheck == "N"):
    print("[Error] Dataset parsing is wrong!")
    exit(0) 

#Data Preprocessing
df.dropna(axis=0, inplace=True)
print(" Total number of rows after pre-processing: ", len(df))




# 
# Collect Attribute Details
# -------------------------

attributes = dict()
for col in df.columns:
    print ("\nAttribute : '%s'" % col)

    while True:
        print ("\n\t1. Identifier\n\t2. Quasi-identifier\n\t3. Sensitive\n\t4. Insensitive")
        ch = int(input ("Q> Please select the attribute type: "))
        if ch not in [1, 2, 3, 4]:
            print("[Error] Please enter a value 1,2,3 or 4!")
        else:
            break
    
    attributes[col] = {
        'dataType': df[col].dtype, 
        'attributeType': ["Identifier", "Quasi-identifier", "Sensitive", "Insensitive"][ch-1]
    }
    
    if (df[col].dtype.name == "object"):
        df[col] = df[col].astype("category")



# Making a copy of the dataset for the DP stats calculation
OrigDF = df.copy()



# Some datastructures for computational easiness
qi_index = list()
feature_columns = list()
sensitive_column = list()

for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        feature_columns.append(attribute)
        qi_index.append(list(OrigDF.columns).index(attribute))
    elif attributes[attribute]['attributeType'] == "Sensitive":
        sensitive_column.append(attribute)

feature_columns =  feature_columns if (len(feature_columns) > 0) else None
sensitive_column = sensitive_column[0] if (len(sensitive_column) > 0) else None



# 
# Predict Parameter Ranges
# ------------------------

from algorithms.param_predictor import ParamPredictor

res = (ParamPredictor()).predict(df, qi_index, sensitive_column)
print(f" - The nominal value for k is : {res['k']}")
print(f" - The l value should be within the range : [{res['l'][0]}, {res['l'][1]}]")
print(f" - The t value should be within the range : [{res['t']:.2f}, {0.0})")





# ----------------------------------------------------------- Anonymization ------------------------------------------------------- #

#
# Supress direct identifiers with '*'
# -----------------------------------

for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Identifier":
        df[attribute] = '*'



#
# Generalizing quasi-identifiers with k-anonymity
# -----------------------------------------------

from algorithms.anonymizer import Anonymizer


# Check if there are any quasi-identifiers
quasi = False
for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        quasi = True


assert quasi, "No Quasi-identifier found! At least 1 quasi-identifier is required."

anon = Anonymizer(df, attributes)
anonymizedDF = anon.anonymize(k, l, t)


#
# Insenstitive attributes are left unchanged
# ------------------------------------------
# No code required for this :)


#
# Differentially private statistical attributes of the dataset 
# ------------------------------------------------------------
"""
from diffPriv.stats import DPStats

dp = DPStats(epsilon, delta)

DP_out = pd.DataFrame(columns=['Property', 'Value'])

for attribute in attributes:
    
    # Stats for numbers only
    if attributes[attribute]['dataType'] not in [np.dtype('int64'), np.dtype('float64')]:
        continue

    if not attributes[attribute]['attributeType'] == 'Identifier':
        # try: 
            DP_out.loc[len(DP_out.index)] = [attribute, '']
            DP_out.loc[len(DP_out.index)] = ['Mean', dp.BoundedMean(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Sum', dp.BoundedSum(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Standard Deviation', dp.BoundedStandardDeviation(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Variance', dp.BoundedVariance(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Min', dp.Min(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Max', dp.Max(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Median', dp.Median(OrigDF[attribute])]
            DP_out.loc[len(DP_out.index)] = ['Count', dp.Count(OrigDF[attribute])]
        # except:
            # continue

"""

# Utility Measure
from utility.DiscernMetric import DM
from utility.CavgMetric import CAVG
from utility.GenILossMetric import GenILoss

qi_index = list()
for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        qi_index.append(list(OrigDF.columns).index(attribute))




print("\n --------- Utility Metrices --------- \n")
# Discernibility Metric
raw_dm = DM(OrigDF, qi_index, k)
raw_dm_score = raw_dm.compute_score()

anon_dm = DM(anonymizedDF, qi_index, k)
anon_dm_score = anon_dm.compute_score()

print(f"DM score (lower is better): \n  BEFORE: {raw_dm_score} || AFTER: {anon_dm_score} || {raw_dm_score > anon_dm_score}")

# Average Equivalence Class
raw_cavg = CAVG(OrigDF, qi_index, k)
raw_cavg_score = raw_cavg.compute_score()

anon_cavg = CAVG(anonymizedDF, qi_index, k)
anon_cavg_score = anon_cavg.compute_score()

import math
print(f"CAVG score (near 1 is better): \n  BEFORE: {raw_cavg_score:.3f} || AFTER: {anon_cavg_score:.3f} || {math.fabs(1-raw_cavg_score) > math.fabs(1-anon_cavg_score)}")

# Gen I Loss Metric
GILoss = GenILoss(OrigDF, feature_columns)
geniloss_score = GILoss.calculate(anonymizedDF)

print(f"GenILoss: [0: No transformation, 1: Full supression] \n Value: {geniloss_score}")



#
# Exporting data
# --------------

# anonymizedDF.to_csv(export_path+'.csv', index=False)
ch = input("Do you want to export the anonymized dataset (y/n): ")
if not (ch == 'y' or ch == ''):
    exit(0)


export_path = "AnonymizedData"
print("\nExporting anonymized dataset ... ")


# Create a Pandas Excel writer object using XlsxWriter as the engine.
writer = pd.ExcelWriter(export_path + '.xlsx')


qi_index = list()
for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        qi_index.append(list(OrigDF.columns).index(attribute))


def paint_bg(v, color):
    ret = [f"background-color: {color[0]};" for i in v]
    return ret

anonymizedDF = anonymizedDF.style.hide_index().apply(paint_bg, color=['gainsboro', 'ivory'], axis=1) 


# Write a dataframe to the worksheet.
anonymizedDF.to_excel(writer, sheet_name ='Data', index=False)
# DP_out.to_excel(writer, sheet_name ='Stats', index=False)

# print(DP_out)

# Close the Pandas Excel writer object and output the Excel file.
writer.save()


