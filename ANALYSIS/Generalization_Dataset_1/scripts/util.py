# Adapted from Johri (2025), by Rani Gera (2025)
# Importing libraries
import os        
import numpy  as np  
import pandas as pd

# Directories
PROJECT_DIRECTORY          = '..'
TRIAL_INFO                 = os.path.join(PROJECT_DIRECTORY,     'trial-info')   # Storing the subject-wise trial-information
CSV_DIRECTORY              = os.path.join(PROJECT_DIRECTORY,     'csvs')         # all the behavioral variable information

def get_str_subid(subid):
    """Generate the RO1 ID for a given subject ID."""
    if isinstance(subid, str):
        try:
            subid = int(subid.split('-')[1])  # Extract integer from string
        except (IndexError, ValueError):
            raise ValueError("Invalid subject ID format. Expected format: 'prefix-<number>'")
    return f'R01_{subid:04d}'

# Get the trial information for the participant
def get_trial_info(subid):
    return os.path.join(TRIAL_INFO, get_str_subid(int(subid)) + '-trial_info.csv')

# Get the bug-type
def get_bug(subid):
    if subid > 112: 
        return 'slowMouseNoBug'
    else: 
        df = pd.read_csv(os.path.join(CSV_DIRECTORY, 'choiceTestDevaluationRatio.csv'))
        return df[df['participant'] == 'sub-'+str(subid)]['Bug'].iat[0]

# estimating the devaluation ratio for the subid
def Estimate_devaluation_ratio(subid):
    df = pd.read_csv(get_trial_info(subid))
    temp = df[df['phase'] == 'training'].loc[0]
    if 'silver' in temp['coin_img']:
        if 'left' in temp['corrResp']:
            silver_response = 'left'
            gold_response   = 'right'
        else:
            silver_response = 'right'
            gold_response   = 'left'
    else:
        if 'left' in temp['corrResp']:
            silver_response = 'right'
            gold_response   = 'left'
        else:
            silver_response = 'left'
            gold_response   = 'right'
    if temp['devalued_coin'] == 'silver':
        correct = gold_response
    else:
        correct = silver_response
    temp = df[df['event'] == 'choice_resp']['resp']
    return (temp[temp == correct].size)/temp.shape[0]

# Get the devaluation ratio for the subid
def get_devaluation_ratio(subid):
    if get_bug(subid) == 'slowMouseNoBug': return Estimate_devaluation_ratio(subid) # if there is no-bug, estimate from the trial-information
    # else, get from the csv file
    df = pd.read_csv(os.path.join(CSV_DIRECTORY, 'choiceTest_devaluationRatio_updatedParticipantList.csv'))
    for index, row in df.iterrows():
        if subid == int(row['ID'].split('-')[1].replace('t', '').replace('_', '')):
            return float(row['devaluation_ratio'])

# Get the training block
def get_block(subid, runid, blockid):
    df = pd.read_csv(get_trial_info(subid))         # getting the trial-information
    df = df[df['run'] == runid - 1].reset_index()   # getting the information for the run
    temp = df[df['event'].isin(['training_period_start', 'ITI_start'])] # getting the training-blocks
    curr = 1    # current block
    skip = False    
    start = None
    for index, row in temp.iterrows():
        if skip and start is None: 
            skip=False
            continue 
        else:
            if start is None: 
                skip = True
            else:
                return df.iloc[start:index+1]
        if curr == blockid:
            start = index
        else: 
            curr += 1
