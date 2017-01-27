# from mimic_package.data_model.mapper import Patient, Prescription
from mimic_package.data_model.oreader_mapper import Patient, Prescription,\
    reader_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mimic_package.connect.connect import connection_string
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from mimic_package.data_model.resources import testing_pickle_filename
import pickle
from sqlalchemy.sql.schema import MetaData

# create sessions
engine = create_engine(connection_string, echo=False, convert_unicode=True)
metadata = MetaData(bind=engine)
metadata.create_all()
reader = Patient.reader(reader_config)

# Session = sessionmaker(bind=engine)  
# session = Session()

""" 
Extraction helper methods.
""" 

def query_db(record_class, limit=20):
    records = session.query(record_class).limit(limit)# grabs arg Patient records / change after testing 
    print("query done") # testing 
    return records
    

def assign_index_record(person):# a Person class object 
    sub_records = person.visit_occurances 
    if len(sub_records) != 0: # if there are associated objects, else skip 
        sub_records_shape = np.shape(sub_records)[0]
        sub_records_sample = np.random.choice(sub_records_shape)
        index_record = sub_records[sub_records_sample]
        # check for future record
        index_record = check_for_future_record(index_record, sub_records)
        person.index_admission = index_record
    else: 
        pass
        # this might be creating a bug somewhere down below
        
def check_for_future_record(index_record, records, time_limit=30): # time_field is object attribute needed to look ahead
    """ takes a chosen index_record, looks forward to see if there is a record beyond it
        if so, returns it, else returns None - this needs to be updated when MIMIC support responds about study period 
    """
    # sort records by time
    records.sort(key= lambda x: x.visit_start_date, reverse=False)
    index_record_index = records.index(index_record)
    if index_record.visit_occurance_id != records[-1].visit_occurance_id: # checks to make it isn't the last one
        next_future_record = records[index_record_index + 1]
        next_record_diff = next_future_record.visit_start_date - index_record.visit_start_date #hardcoded
        if next_record_diff.days >= time_limit: 
            return index_record
    else: 
        return None
        # compare aganst period generator (not built yet)

""" 
    My computer is really slow - this allows me to store a basic set of transformed 
    Patient records as OMOPPerson objects to test extractor functionality
"""        

def create_testing_pickle(record_class):
    counter = 0
    raw_records = session.query(record_class).limit(500)
    print("query done")
    persons = [] 
    for record in raw_records: 
        if len(record.admissions) > 2 and counter < 10: # hardcode
            print("yep {0}").format(record.subject_id)
            person = record.person
            persons.append(person)
            counter += 1
        else: 
            print("nope")
    
    with open(testing_pickle_filename, 'wb') as outfile: 
        pickle.dump(persons, outfile)

def load_testing_pickle():
    with open(testing_pickle_filename, 'rb') as infile: 
        persons = pickle.load(infile)    
        return persons
    
""" 
    All of the extractors are based on an index admission for a Person 
    Additional features to consider: 
    - ICD9 codes for index admission (grouped by category) 
    - planned / unplanned admission 
"""

def get_person_index_age(person):
    index_record_date = person.index_admission.visit_start_date
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


def get_person_ethnicity(person):
    pass 
    # note that this might require chartevents

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
    Look more into other models for this, and what exists in the MIMIC record: 
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


def apply_extractors(person):
    if person.index_admission: # shouldn't need this check, person at this point needs to be clean 
        # run extractors 
        person_id = person.person_id # is this needed? using as an index? 
        person_index_age = get_person_index_age(person)
        index_admission_length = get_index_admission_length(person)
        person_gender = get_person_gender(person)
        admission_rate = get_admission_rate(person)
        readmit_30 = get_readmit_30(person)
        features = [person_id, person_index_age, index_admission_length, person_gender, admission_rate, readmit_30]
        return features 
    
# pseudo controller

create_testing_pickle(Patient)

persons = load_testing_pickle()
df_columns = ["person_id", "person_index_age","index_admission_length","person_gender", "admission_rate", 'readmit_30']
np_data = np.array(df_columns)

for person in persons: 
    assign_index_record(person)
    features = apply_extractors(person)
    if features: 
        np_data = np.vstack((np_data, features))
        print(features)

# create training / testing sets 
''' running on assumption that 40 / 60 is a good test / train ratio. Easily changeable. 
    Why did I create the columns in the first place? Are those supposed to be there? 
    Where do they go when I use sample or drop? 
'''
all_data_df = pd.DataFrame(data=np_data[1:,:], columns=np_data[0,:])

# clean data 


#stupid names, change

train_df = all_data_df.sample(frac=0.6)
train_df2 = train_df.drop('readmit_30', axis=1) 
test_df = all_data_df.drop(train_df.index)
test_df2 = test_df.drop('readmit_30', axis=1) 


# fit the model 
rf = RandomForestClassifier(n_estimators= 100)
m = rf.fit(test_df, test_df2)
output = rf.predict(train_df)

print "Features sorted by their score:"



# model = Earth().fit(X, y)
# print('testing')
