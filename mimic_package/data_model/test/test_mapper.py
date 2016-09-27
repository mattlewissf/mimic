from mimic_package.data_model.mapper import Patient, Admission, Callout,\
    Chartevent, Caregiver, CPTevent, D_ICD_Diagnosis, Diagnosis_ICD,\
    D_ICD_Procedure, D_Item, D_Labitem, Datetimeevent, Icustay, Inputevent_CV,\
    Inputevent_MV, Labevent, Microbiologyevent, Noteevent, Outputevent,\
    Prescription, Procedureevent_MV, Drgcode

# testing mimic table classes and relationship setup

def test_admission(): 
    Admission().row_id
    Admission().religion
    # relationships
    isinstance(Admission().callouts, list)
    isinstance(Admission().chartevents, list)
    
def test_callout():
    Callout().row_id
    Callout().outcometime


def test_caregiver():
    Caregiver().row_id
    Caregiver().label
    # relationships 
    isinstance(Caregiver().chartevents, list)
    isinstance(Caregiver().procedureevents_mv, list)
      
def test_chartevent():
    Chartevent().row_id
    Chartevent().warning
    
def test_cptevent():
    CPTevent().row_id
    CPTevent().cpt_cd
    
def test_d_icd_diagnose():
    D_ICD_Diagnosis().row_id
    D_ICD_Diagnosis().short_title
    
def test_d_icd_procedure():
    D_ICD_Procedure().row_id
    D_ICD_Procedure().long_title
    
def test_d_item():
    D_Item().row_id
    D_Item().category
    # relationships 
    isinstance(D_Item().datetimeevents, list)

def test_d_labitem():
    D_Labitem().row_id
    D_Labitem().fluid
    # relationships
    isinstance(D_Labitem().labevents, list)
    
def test_datetimeevent():
    Datetimeevent().row_id
    Datetimeevent().resultstatus

def test_diagnosis_icd():
    Diagnosis_ICD().row_id
    Diagnosis_ICD().seq_num
    # relationships
    isinstance(Diagnosis_ICD().d_icd_diagnoses, list)# check on this 

def test_drgcode():
    Drgcode().row_id
    Drgcode().drg_severity
    

def test_icustay():
    Icustay().row_id
    Icustay().first_careunit
    # relationships
    isinstance(Icustay().transfers, list)
    
def test_inputevent_cv():
    Inputevent_CV().row_id
    Inputevent_CV().rate

def test_inputevent_mv():
    Inputevent_MV().row_id
    Inputevent_MV().rate
    
def test_labevent():
    Labevent().row_id
    Labevent().value
    
def test_microbiologyevent(): # this failed with some of the attributes 
    Microbiologyevent().row_id
    Microbiologyevent().chartdate
    
def test_noteevent():
    Noteevent().row_id
    Noteevent().description
    
def test_outputevent():
    Outputevent().row_id
    Outputevent().value
    
def test_patient(): 
    Patient().row_id
    Patient().gender
    Patient().dob
    # relationships
    isinstance(Patient().admissions, list)
    isinstance(Patient().callouts, list)
    isinstance(Patient().chartevents, list)
    
def test_prescription():
    Prescription().row_id
    Prescription().route
    Prescription().startdate
    
def test_procedureevent_mv():
    Procedureevent_MV().row_id
    Procedureevent_MV().value

# this is some specific idiom that Jason gave you for testing nose with SQLalchemy 
if __name__ == '__main__': 
    import sys
    import nose
    module_name = sys.modules[__name__].__file__
    
    result = nose.run(argv=[sys.argv[0], 
                            module_name, 
                            '-s', '-v'])