import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from mimic_package.connect.locations import features_dir, export_dir
from mimic_package.data_model.oreader_mapper import Patient
from mimic_package.connect.connect import connection_string
from mimic_package.data_model.configs import create_sqa_reader_config
from mimic_package.data_model.definitions import ethnicity_dict, ethnicity_values, marital_status_dict,\
    marital_values, check_against_charlson, charlson_features, check_against_ccs, index_admission_types,\
    insurance_values, parse_icd_code
from types import NoneType 
from ccs.icd9 import dx_code_sets_dict
from clinvoc.icd9 import ICD9CM


'''
Reader config
'''
reader_config = create_sqa_reader_config(connection_string, limit_per=10000, n_tries=10)
reader = Patient.reader(reader_config)

""" 
Extraction helper functions.
""" 

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

'''
When trying to pull in all 46k patient records, I often fail to get all of the records
'''
def piecemeal_to_df():
    persons = []
    counter = 0  
    df_num = 1
    for patient in reader:
        if counter > 1000: 
            persons.append(patient.person)
            pickle_df = extract_to_dataframe(persons)
            pd.to_pickle(pickle_df, 'piecemeal_{}.pkl'.format(df_num)) # put piecemeal back when you want
            print('piecemeal_{}'.format(df_num))
            counter = 0
            persons = []
            df_num += 1
        elif reader.peek()  == None: 
            persons.append(patient.person)
            pickle_df = extract_to_dataframe(persons)
            pd.to_pickle(pickle_df, 'piecemeal.pkl')
            print('finished')
        else: 
            persons.append(patient.person)
            counter += 1
            
            
def combine_piecemeal_dfs():
    combined_df = None
    for x in xrange(1,46): 
        if combined_df is not None: 
            target_df = pd.read_pickle('piecemeal_{}.pkl'.format(x))
            combined_df = combined_df.append(target_df, ignore_index=True)
        else: 
            combined_df = pd.read_pickle('piecemeal_{}.pkl'.format(x))
            

    pd.to_pickle(combined_df, 'features.pkl')
    print('created combined_df')
    return combined_df

def grab_specific_persons(*args):
    person_collector = [] 
    for x in reader: 
        print(x.subject_id)
        if x.subject_id in args:
            person_collector.append(x.person)
            if len(args) == len(person_collector):
                return person_collector
                     
def export_to_csv(df, name):
    path = '{0}/{1}.csv'.format('extract/', name)
    df.to_csv(path, sep='\t', encoding='utf-8')

'''
Extraction functions
'''    

def assign_index_record(person): 
    sub_records = person.visit_occurances
    if len(sub_records) != 0: # if there are associated objects, else skip 
        sub_records_shape = np.shape(sub_records)[0]
        sub_records_sample = np.random.choice(sub_records_shape)
        index_record = sub_records[sub_records_sample]
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

def get_person_index_age(person):
    try: 
        index_record_date = person.index_admission.visit_start_date
    except AttributeError: 
        print('person_index_age_error')
    person_dob = person.DOB
    person_age_at_index = index_record_date - person_dob
    person_age_at_index = format((person_age_at_index.total_seconds() / (365.25 * 86400)), '.2f') # convert to years 
    return float(person_age_at_index)

def get_index_admission_length(person):
    index_admission = person.index_admission
    index_admission_length = index_admission.visit_end_date - index_admission.visit_start_date 
    index_admission_length = format((index_admission_length.total_seconds() / 86400), '.2f')  # convert to days 
    if index_admission_length < 0: 
        index_admission_length = 0
    return float(index_admission_length)

def get_index_admission_type(person):
    # can be either urgent / emergency / elective
    index_admission_type = person.index_admission.admission_type
    admission_types = index_admission_types.copy() 
    if index_admission_type in admission_types:
        admission_types[index_admission_type] = 1
    return admission_types


def get_person_gender(person):
    person_gender = person.gender
    if person_gender == "M":
        return 0
    if person_gender == "F": 
        return 1


def get_admission_rate(person):
    # backwards 12 months of admissions / period taken from CMS documentation 
    period_start = person.index_admission.visit_start_date - relativedelta(years=1)
    admissions_in_period = [admission for admission in person.visit_occurances if 
                            admission.visit_start_date > period_start and admission.visit_start_date < 
                            person.index_admission.visit_start_date]
    admission_rate = len(admissions_in_period) / 12.0 #TODO: 'normalize' this
    return admission_rate

def get_readmit_30(person):
    period_end = person.index_admission.visit_end_date + relativedelta(days=30)
    admissions_within_30_days = [admission for admission in person.visit_occurances 
                                 if admission.visit_start_date > person.index_admission.visit_end_date 
                                 and admission.visit_start_date < period_end]

    if len(admissions_within_30_days) > 0: 
        for admission in admissions_within_30_days: 
            if admission.admission_type == 'EMERGENCY' or 'URGENT': 
                return 1
            else: 
                print admission.admission_type
                return 0
    else: 
        return 0
    
def get_death_in_year(person):
    # check for death record in admissions
    period_end = person.index_admission.visit_end_date + relativedelta(days=365)
    admissions_within_year = [admission for admission in person.visit_occurances 
                                 if admission.visit_start_date > person.index_admission.visit_end_date 
                                 and admission.visit_start_date < period_end]
    
    if admissions_within_year > 0: 
        for admission in admissions_within_year: 
            if admission.visit_death: 
                print('death')
                return 1
    
    if person.death:
        if person.death.death_date < period_end: 
            return 1

    return 0
    # TODO: integrate Death model

def get_person_icd_codes(person, period=365):       
    '''
    goes through conditions assigned to patient (and not to specific admission)
    - uses ccs module to parse icd9
    '''
    vocab = ICD9CM()
    period_start = person.index_admission.visit_start_date - relativedelta(days=period)
    conditions = {}
    for condition in person.conditions:
        admission_id = str(condition.admission_id)
        if admission_id in conditions:  
            try:
                conditions[admission_id].append(condition.icd9_code)
            except AttributeError:
                pass
        else: 
            conditions[admission_id] = [condition.icd9_code]
    codes = []
    for visit in person.visit_occurances: 
        if visit.visit_start_date > period_start <= person.index_admission.visit_start_date: 
            for raw_code in conditions[str(visit.visit_occurance_id)]:
                try:
                    
                    code_set = vocab.parse(raw_code) # comes back as a set 
                    [codes.append(code) for code in code_set]
                except TypeError:
                    print("Type Error", raw_code)
    return codes

def apply_charlson_groupers(codes): 
    charlson_features_scores = check_against_charlson(codes)
    return charlson_features_scores

def apply_ccs_groups(codes):
    ccs_features = check_against_ccs(codes)
    return ccs_features

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
    
def get_insurance_status(person):
    ''' 
    This is index admission as noted by the index admission record; 
    there could be more to looking backward and constructing an insurance history
    '''
    insurance_features = insurance_values.copy()
    insurance_status = person.index_admission.insurance_status
    if insurance_status in insurance_features: 
        insurance_features[insurance_status] = 1
        return insurance_features
    else: 
        return insurance_features

def apply_extractors(person, extract='30_day'):
        assign_index_record(person)
        if person.index_admission == None: # leave out people with no index admission
            return None
        if person.index_admission.admission_type == 'NEWBORN':
            return None
        person_index_age = get_person_index_age(person)
        if person_index_age > 120: 
            return None # this is in DOB for ~10% of patients
        person_id = person.person_id
        index_admission_length = get_index_admission_length(person)
        # testing
        death_in_year = get_death_in_year(person) # new! need to sort out
        index_admission_type_features = get_index_admission_type(person)
        person_gender = get_person_gender(person)
        ethnicity_features = get_person_ethnicity(person)
        marital_features = get_person_marital(person)
        insurance_features = get_insurance_status(person) # need to break out below
        admission_rate = get_admission_rate(person)
        codes = get_person_icd_codes(person)
        charlson_features_scores = apply_charlson_groupers(codes)
        charlson_features = charlson_features_scores[0]
        charlson_score = charlson_features_scores[1]
        ccs_features = apply_ccs_groups(codes)
        readmit_30 = get_readmit_30(person)
        features = [person_id, person_index_age, index_admission_length, person_gender, admission_rate]
        [features.append(feature) for feature in index_admission_type_features.values()]
        [features.append(feature) for feature in ethnicity_features.values()]
        [features.append(feature) for feature in marital_features.values()]
        [features.append(feature) for feature in insurance_features.values()]
        [features.append(feature) for feature in charlson_features.values()]
        features.append(charlson_score)
        [features.append(feature) for feature in ccs_features.values()]
        if extract == '30_day': 
            features.append(readmit_30) 
        elif extract == 'death':
            features.append(death_in_year)
        return features 
    
def extract_to_dataframe(persons):
    # instantiating codeset for ccs just once here for speed - need to figure out more pythonic ways
#     codeset = ICD9()
#     print('using ICD9 codeset')
    
    df_columns = ["person_id", "person_index_age","index_admission_length","person_gender", "admission_rate"]
    [df_columns.append(feature) for feature in index_admission_types.keys()]
    [df_columns.append(feature) for feature in ethnicity_values.keys()]
    [df_columns.append(feature) for feature in marital_values.keys()]
    [df_columns.append(feature) for feature in insurance_values.keys()]
    [df_columns.append(feature) for feature in charlson_features.keys()]
    df_columns.append('charlson_score')
    [df_columns.append(feature) for feature in sorted(dx_code_sets_dict.keys())] 
    df_columns.append("readmit_30") 
    
    empty_col = [0 for x in df_columns]
    np_data = np.array(empty_col)
    
    for person in persons: 
        features = apply_extractors(person) 
        if features: 
            np_data = np.vstack((np_data, features))
        
    df = pd.DataFrame(data=np_data[1:,:], columns=df_columns)
    df.person_index_age = df.person_index_age.astype(int)
    df.person_gender = df.person_gender.astype(int)
    df.person_id = df.person_id.astype(int)
    return df
    
'''
Pseduo-controller
'''

test_batch = create_test_batch(20)
test_batch_df = extract_to_dataframe(test_batch)

# create a pickle with this df 
test_batch.to_pickle('test_batch.pkl')

print('extraction complete')




if __name__ == '__main__':
    pass

