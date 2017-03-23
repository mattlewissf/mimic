import os
import numpy as np
import pandas as pd
import random
import collections
import matplotlib.pyplot as plt
from sklearn import cross_validation
from sklearn.model_selection import KFold
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, roc_curve, auc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from mimic_package.connect.locations import features_dir, export_dir
from mimic_package.data_model.oreader_mapper import Patient
from mimic_package.connect.connect import connection_string
from mimic_package.data_model.configs import create_sqa_reader_config
from mimic_package.data_model.definitions import ethnicity_dict, ethnicity_values, marital_status_dict,\
    marital_values, check_against_charleston, charleston_values
from pandas.core.algorithms import isin
from sqlalchemy.util.langhelpers import NoneType
from types import NoneType


reader_config = create_sqa_reader_config(connection_string, limit_per=10000, n_tries=10)
reader = Patient.reader(reader_config)

""" 
Extraction helper methods.
""" 

# create persons for a test batch 
def create_test_batch(batch_size):
    persons = [] 
    counter = 0 # refactor? 
    for patient in reader:
        if counter <= batch_size:
            persons.append(patient.person)
            counter += 1
            print(counter)
        else:
            return persons


def grab_specific_persons(*args):
    person_collector = [] 
    for x in reader: 
        print(x.subject_id)
        if x.subject_id in args:
            person_collector.append(x.person)
            if len(args) == len(person_collector):
                return person_collector
            
            
def export_to_csv(df, name):
    path = '{0}/{1}.csv'.format(export_dir, name)
    df.to_csv(path, sep='\t', encoding='utf-8')
    

def assign_index_record(person): 
    sub_records = person.visit_occurances
    if len(sub_records) != 0: # if there are associated objects, else skip 
        sub_records_shape = np.shape(sub_records)[0]
        sub_records_sample = np.random.choice(sub_records_shape)
        index_record = sub_records[sub_records_sample]
        # baby check - need to refactor somewhere smarter
        if index_record.admission_type == 'NEWBORN':
            pass
        person.index_admission = index_record
        
def check_for_future_record(index_record, records, time_limit=30): # time_field is object attribute needed to look ahead
    """ takes a chosen index_record, looks forward to see if there is a record beyond it
        if so, returns it, else returns None - this needs to be updated when MIMIC support responds about study period 
    """
    # sort records by time
    records.sort(key= lambda x: x.visit_start_date, reverse=False)
    index_record_index = records.index(index_record) # finds the index of the index_record in the records? 
    if index_record.visit_occurance_id != records[-1].visit_occurance_id: # checks to make it isn't the last one
        next_future_record = records[index_record_index + 1]
        next_record_diff = next_future_record.visit_start_date - index_record.visit_start_date #hardcoded
        if next_record_diff.days >= time_limit: 
            return index_record
    else: 
        return None
        # compare aganst period generator (not built yet)


def get_person_index_age(person):
    try: 
        index_record_date = person.index_admission.visit_start_date
    except AttributeError: 
        print('boomp')
    person_dob = person.DOB
    person_age_at_index = index_record_date - person_dob
    person_age_at_index = format((person_age_at_index.total_seconds() / (365.25 * 86400)), '.2f') # convert to years 
    
    return float(person_age_at_index)

def get_index_admission_length(person):
    index_admission = person.index_admission
    index_admission_length = index_admission.visit_end_date - index_admission.visit_start_date 
    index_admission_length = format((index_admission_length.total_seconds() / 86400), '.2f')  # convert to days 
    return float(index_admission_length)

def get_person_gender(person):
    person_gender = person.gender
    if person_gender == "M":
        return 0
    if person_gender == "F": 
        return 1


def get_admission_rate(person):
    # backwards 12 months of admissions / from CMS doc 
    period_start = person.index_admission.visit_start_date - relativedelta(years=1)
    admissions_in_period = [admission for admission in person.visit_occurances if 
                            admission.visit_start_date > period_start and admission.visit_start_date < 
                            person.index_admission.visit_start_date]
    admission_rate = len(admissions_in_period) / 12.0 # set as admissions per month? fix this to correct standard
    return admission_rate

def get_readmit_30(person):
    ''' 
    Look more into other models for this, and what eassign_index_recordxists in the MIMIC record: 
    - death w/in 30 days (in)
    - certain types of admissions (ex) 
    - transfers (in) 
    - expected treatment re-admits (chemo / dialysis) (ex) 
    ''' 
    
    period_end = person.index_admission.visit_end_date + relativedelta(days=30)
    admissions_within_30_days = [admission for admission in person.visit_occurances 
                                 if admission.visit_start_date > person.index_admission.visit_end_date 
                                 and admission.visit_start_date < period_end]
    
    # explicitly return 1 for re-admission, 0 for none 
    if len(admissions_within_30_days) > 0: 
        return 1
    else: 
        return 0
    

def get_person_icd_codes(person, period=365): # hacky one year look back\
        
    '''
    goes through conditions assigned to patient (and not to specific admission)
    '''
    period_start = person.index_admission.visit_start_date - relativedelta(days=period)
    codes = [] 
    conditions = {}
    for condition in person.conditions:
        admission_id = str(condition.admission_id)
        if admission_id in conditions:  
            try:
                conditions[admission_id].append(condition.icd9_code)
            except AttributeError:
                print('what')
        else: 
            conditions[admission_id] = [condition.icd9_code]
            
    # this is terrible
        '''
    MIMIC store codes without decimal: 
    'The code field for the ICD-9-CM Principal and Other Diagnosis Codes is six characters in length, 
    with the decimal point implied between the third and fourth digit for all diagnosis codes other than the V codes. 
    The decimal is implied for V codes between the second and third digit.' - this is incorrect as seen in data... 
    '''
    codes = []
    for visit in person.visit_occurances: 
        if visit.visit_start_date > period_start <= person.index_admission.visit_start_date: 
            for raw_code in conditions[str(visit.visit_occurance_id)]:
                if raw_code is None:
                    print("none for visit code")
                    print(visit.visit_occurance_id)
                    return []
                
                if raw_code.isdigit():
                    code = '{0}.{1}'.format(raw_code[:3], raw_code[3:])
                elif raw_code[0].isalpha(): 
                    code = '{0}.{1}'.format(raw_code[:3], raw_code[3:])
            
                else: 
                    return []             
                
                codes.append(str(code))         
    return codes

def apply_charleston_groupers(codes):
    charleston_features = check_against_charleston(codes)
    return charleston_features

def get_person_ethnicity(person):
    '''
    Ethnicity is noted in some Admissions (not Patient). See definitions file
    '''
    subrecords = person.visit_occurances
    ethnicities = set([sub.ethnicity for sub in subrecords])
    ethnicities = list(ethnicities)
    ethnicity = ethnicities[0] # even if there are multiples, pick the first. Randomize this later
    
    ethnicity_features = ethnicity_values.copy()
    if ethnicity in ethnicity_dict: 
        ethnicity_features[ethnicity_dict[ethnicity]] = 1
        return ethnicity_features
    else: 
        return ethnicity_features

    

def get_person_marital(person):
    '''
    Marital status noted in some Admissions (not Patient). See definitions file
    '''
    marital_features = marital_values.copy()
    marital_record = person.index_admission.marital_status
    if marital_record in marital_status_dict:
        marital_features[marital_status_dict[marital_record]] = 1
        return marital_features
    else: 
        return marital_features


def apply_extractors(person):
        assign_index_record(person)
        if person.index_admission == None: # leave out people with no index admission
            return None
        if person.index_admission.admission_type == 'NEWBORN':
            return None
#         person_id = person.person_id # is this needed? using as an index? 
        person_index_age = get_person_index_age(person)
        if person_index_age > 120: 
            return None # this is a bug in DOB for ~10~ of patients
        person_id = person.person_id
        index_admission_length = get_index_admission_length(person)
        person_gender = get_person_gender(person)
        ethnicity_features = get_person_ethnicity(person)
        marital_features = get_person_marital(person)
        admission_rate = get_admission_rate(person)
        codes = get_person_icd_codes(person) # matching patient codes to charleston comorbid values
        charleston_features = apply_charleston_groupers(codes)
        readmit_30 = get_readmit_30(person)
        features = [person_id, person_index_age, index_admission_length, person_gender, admission_rate]
        [features.append(feature) for feature in ethnicity_features.values()]
        [features.append(feature) for feature in marital_features.values()]
        [features.append(feature) for feature in charleston_features.values()]
        features.append(readmit_30) # just keeping this on the end
        return features 


'''
pseudo controller section
'''



df_columns = ["person_id", "person_index_age","index_admission_length","person_gender", "admission_rate"]
[df_columns.append(feature) for feature in ethnicity_values.keys()]
[df_columns.append(feature) for feature in marital_values.keys()]
[df_columns.append(feature) for feature in charleston_values.keys()]
df_columns.append("readmit_30")
 
empty_col = [0 for x in df_columns]
np_data = np.array(empty_col)
persons = create_test_batch(600)

 
for person in persons: 
    features = apply_extractors(person)
    if features: 
        np_data = np.vstack((np_data, features))
        print(features)
 
df = pd.DataFrame(data=np_data[1:,:], columns=df_columns) 


df.to_pickle('temp.pkl') # saves data 
# df = pd.read_pickle('temp.pkl') # read saved data

df.person_index_age = df.person_index_age.astype(int)
df.person_gender = df.person_gender.astype(int)
df.person_id = df.person_id.astype(int)

# df[5:] = df[5:].astype(int)


'''
sklearn setup
'''
sk_features = df.columns[1:-1]
X  = df[sk_features]
y = df["readmit_30"]

# using train_ty[test]est_split / no cross validation
# X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.35)
 
# RandomForestClassifier
# clf_rf = RandomForestClassifier()
# clf_rf.fit(X_train, y_train)look into tuning n_splits
# y_pred_rf = clf_rf.predict(X_test)
# acc_rf = accuracy_score(y_test, y_pred_rf)
# print('RFC accuracy: {}').format(acc_rf)
# # 
# # K nearest neighbors
# clf_knn = KNeighborsClassifier()
# clf_knn.fit(X_train, y_train)
# y_pred_knn = clf_knn.predict(X_test)
# acc_knn = accuracy_score(y_test, y_pred_knn)
# print("KNC accuracy: {}").format(acc_knn)


# Run classifier with cross-validation 

df_ = df.copy()
df_out = df_.drop(sk_features, axis=1)
df_out['prob'] = np.nan
df_out['auc'] = np.nan

kf = KFold(n_splits=10) # bring back to 10
kf.get_n_splits(X)
roc_collector = [] # not sure this is the best way to do this
for train, test in kf.split(X):
    clf_rf = RandomForestClassifier()
    clf_rf.fit(X.loc[train], y.loc[train])
    clf_pred = clf_rf.predict(X.loc[test])
    clf_prob = clf_rf.predict_proba(X.loc[test])
    prob = clf_prob[:,1]
    fpr, tpr, thresholds = roc_curve(y[test], prob)
    roc_auc = auc(fpr, tpr)
    # write to output df
    df_out.loc[test, 'prob'] = prob
    df_out.loc[test, 'auc'] = roc_auc
    

print('weeee')
print(df_out)



# show the plots - currently broke
# plt.figure(figsize=(5, 5))
# plt.plot(fpr, tpr, 'b')
# plt.plot([0, 1], [0, 1],'r--')
# plt.show()

    
    

