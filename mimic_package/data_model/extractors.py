import os
import numpy as np
import pandas as pd
import random
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from mimic_package.connect.locations import features_dir, export_dir
from mimic_package.data_model.oreader_mapper import Patient
from mimic_package.connect.connect import connection_string
from mimic_package.data_model.configs import create_sqa_reader_config
from mimic_package.data_model.definitions import ethnicity_dict, ethnicity_values, marital_status_dict


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
    
def get_index_admission_codes(person):
    '''
    gather all ICD9 / ICD10 / hcpcs codes associated with index admission in a basic way
    '''
    pass

def get_person_ethnicity(person):
    '''
    Ethnicity is noted in some Admissions (not Patient). See definitions file
    '''
    subrecords = person.visit_occurances
    ethnicities = set([sub.ethnicity for sub in subrecords])
    ethnicities = list(ethnicities)
    if len(ethnicities) > 1: # if more than one ethnicity in records , picks one at random 
        sub_records_shape = np.shape(subrecords)
        sample = np.random.choice(sub_records_shape)
        ethnicity =  ethnicities[sample -1]
    else: 
        ethnicity = ethnicities[0]
    
    if ethnicity_dict[ethnicity]:
        return ethnicity_values[ethnicity_dict[ethnicity]]
    else: 
        return 0 # change this later? should None have another value?

def get_person_marital(person):
    '''
    Marital status noted in some Admissions (not Patient). See definitions file
    '''
    if person.index_admission.marital_status:
        return marital_status_dict[person.index_admission.marital_status]
    else:    
        return 0 # again, should None have another value?


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
        index_admission_length = get_index_admission_length(person)
        person_gender = get_person_gender(person)
        person_ethnicity = get_person_ethnicity(person)
        person_marital_status = get_person_marital(person)
        admission_rate = get_admission_rate(person)
        readmit_30 = get_readmit_30(person)
        features = [person_index_age, index_admission_length, person_gender, admission_rate, person_ethnicity, person_marital_status, readmit_30]
        return features 


'''
pseudo controller section
'''

df_columns = ["person_index_age","index_admission_length","person_gender", "admission_rate", "person_ethnicity", "person_marital_status", "readmit_30"]
empty_col = [0 for x in df_columns]
np_data = np.array(empty_col)
persons = create_test_batch(500)

for person in persons: 
    features = apply_extractors(person)
    if features: 
        np_data = np.vstack((np_data, features))
        print(features)

df = pd.DataFrame(data=np_data[1:,:], columns=df_columns) 

df.person_index_age = df.person_index_age.astype(int)
df.person_gender = df.person_gender.astype(int)
df.readmit_30 = df.readmit_30.astype(int)


'''
sklearn setup
'''
sk_features = df.columns[:-1]
X  = df[sk_features]
y = df["readmit_30"]
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.35)

# RandomForestClassifier
clf_rf = RandomForestClassifier()
clf_rf.fit(X_train, y_train)
y_pred_rf = clf_rf.predict(X_test)
acc_rf = accuracy_score(y_test, y_pred_rf)
print('RFC accuracy: {}').format(acc_rf)

# K nearest neighbors
clf_knn = KNeighborsClassifier()
clf_knn.fit(X_train, y_train)
y_pred_knn = clf_knn.predict(X_test)
acc_knn = accuracy_score(y_test, y_pred_knn)
print("KNC accuracy: {}").format(acc_knn)
