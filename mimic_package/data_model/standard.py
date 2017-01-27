'''
standard does not know about mapper
'''

    
class OMOPStandardData(object):
    pass
    # add any top level methods here
 
class OMOPPerson(OMOPStandardData): 

    def __init__(self, person_id, DOB, DOD, gender, expire_flag, drug_exposures, visit_occurances, 
                 procedures, observations, conditions, death, index_admission):
        self.person_id = person_id
        self.DOB = DOB
        self.DOD = DOD
        self.gender = gender
        self.expire_flag = expire_flag
        self.drug_exposures = drug_exposures
        self.visit_occurances = visit_occurances
        self.procedures = procedures
        self.observations = observations
        self.conditions = conditions
        self.death = death 
        self.index_admission = index_admission

        
class OMOPDrugExposure(OMOPStandardData): 
    # from prescription table
    def __init__(self, exposure_id, person_id, starttime, endtime, ndc, visit_occurance_id):
        self.exposure_id = exposure_id
        self.person_id = person_id 
        self.starttime = starttime 
        self.endtime = endtime
#         self.drug_type = drug_type # one or more of the drug fields, look into the data
        self.ndc = ndc
        self.visit_occurance_id = visit_occurance_id

    

class OMOPVisitOccurance(OMOPStandardData): 
    """ From OMOP: 
    The Visit Occurrence table contains all Person visits to health care providers, including inpatient,
    outpatient, and ER visits. A Visit is an encounter for a patient at a point of care for a duration of time.
    There could be several Providers involved in the patient's care during the Visit.
    """
    def __init__(self, visit_occurance_id, person_id, visit_start_date, 
                 visit_end_date, place_of_service_source_value, diagnosis, admission_type):
        self.visit_occurance_id = visit_occurance_id
        self.person_id = person_id 
        self.visit_start_date = visit_start_date
        self.visit_end_date = visit_end_date
        self.place_of_service_source_value = place_of_service_source_value
        self.diagnosis = diagnosis
#         self.time_in_ed = time_in_ed # need to add / calculated from Admission.edregtime and Admission.edouttime
        self.admission_type = admission_type
        # maybe some basic stats or discharge info from this admission, provided it can be grouped or made 0-100 
    pass

class OMOPConditionOccurance(OMOPStandardData): 
    
    def __init__(self, condition_occurance_id, person_id, admission_id, icd9_code, icd9_title):
        self.condition_occurance_id = condition_occurance_id
        self.person_id = person_id
        self.admission_id = admission_id
        self.icd9_code = icd9_code
        self.icd9_title = icd9_title
        
    
class OMOPPayPlanPeriod(OMOPStandardData):
    # unclear if this data is in MIMIC in a meaningful way
    pass 

class OMOPProcedureOccurance(OMOPStandardData): 
    """
    two tables apply: procedureevents_mv and procedures_icd. mv has the 
    advantage of having timestamp info (plus a lot more) 
    """
    
    def __init__(self, procedure_occurance_id, person_id, procedure_date, provider_id):
        self.procedure_occurance_id = procedure_occurance_id
        self.person_id = person_id
        self.procedure_date = procedure_date 
        self.provider_id = provider_id
    

class OMOPObservation(OMOPStandardData):
    """
    Currently limited to LabData
    """
    def __init__(self, observation_id, person_id, observation_date, observation_time, 
                 admission_id, observation_type, observation_value):
        
        self.observation_id = observation_id
        self.person_id = person_id 
        self.observation_date = observation_date 
        self.observation_time = observation_time 
        self.admission_id = admission_id
        self.observation_type = observation_type
        self.observation_value = observation_value
        # note no cgid in the labevents table
    
class OMOPDeath(OMOPStandardData): 
    """ records death of a Patient in records. Currently pulling from Patients w/ expired flag""" 
    def __init__(self, person_id, death_date, ICD9_code=None):
        self.person_id = person_id
        self.death_date = death_date
        self.ICD9_code = ICD9_code
    

class OMOPProvider(OMOPStandardData):
    
    def __init__(self, provider_id, label):
        self.provider_id = provider_id
        self.label = label 
    














