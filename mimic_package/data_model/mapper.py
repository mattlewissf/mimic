from mimic_package.data_model.metadata import metadata
from sqlalchemy.sql.schema import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import relationship
from mimic_package.data_model.standard import OMOPPerson, OMOPDrugExposure, OMOPVisitOccurance, \
OMOPProcedureOccurance, OMOPObservation, OMOPConditionOccurance, OMOPDeath


Base = declarative_base()

def table_override(original, base, overrides={}):
    result = Table(original.name, base.metadata, schema=original.schema)
    for col in original.columns: 
        if col.name not in overrides: 
            result.append_column(col.copy())
        else: 
            new_col = overrides[col.name].copy()
            new_col.name = col.name
            result.append_column(new_col)
    return result 

class Admission(Base): # 
    __table__ = table_override(metadata.tables['mimiciii.admissions'],
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                "subject_id": Column(Integer, ForeignKey('mimiciii.patients.subject_id'))}) #
    callouts = relationship('Callout') #
    chartevents = relationship('Chartevent') #
    cptevents = relationship('CPTevent')
    datetimeevents = relationship('Datetimeevent')
    diagnoses_icd = relationship('Diagnosis_ICD')
    drgcodes = relationship('Drgcode')
    icustays = relationship('Icustay')
    inputevents_cv = relationship('Inputevent_CV')
    inputevents_mv = relationship('Inputevent_MV')
    labevents = relationship('Labevent')
    microbiologyevents = relationship('Microbiologyevent')
    noteevents = relationship('Noteevent')
    outputevents = relationship('Outputevent')
    prescriptions = relationship('Prescription')
    procedureevents_mv = relationship('Procedureevent_MV')
    procedures_icd = relationship('Procedure_ICD')
    services = relationship('Service')
    transfers = relationship('Transfer')
    

class Callout(Base): # note that callout is the only table in the schema with a singular name # 
    __table__ = table_override(metadata.tables['mimiciii.callout'],
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                "subject_id": Column(Integer, ForeignKey('mimiciii.patients.subject_id')), #
                "hadm_id": Column(Integer, ForeignKey('mimiciii.admissions.hadm_id'))}) #

class Caregiver(Base): #
    __table__ = table_override(metadata.tables['mimiciii.caregivers'],
               Base, 
               {"row_id": Column(Integer, primary_key =True)}) #
    
    chartevents = relationship('Chartevent') #
    datetimeevents = relationship('Datetimeevent')
    inputevents_cv = relationship('Inputevent_CV')
    inputevents_mv = relationship('Inputevent_MV')
    noteevents = relationship('Noteevent')
    outputevents = relationship('Outputevent')
    procedureevents_mv = relationship('Procedureevent_MV')
    
class Chartevent(Base): #
    __table__ = table_override(metadata.tables['mimiciii.chartevents'],
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                "subject_id": Column(Integer, ForeignKey('mimiciii.patients.subject_id')), #
                "hadm_id": Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), #
                "icustay_id": Column(Integer, ForeignKey('mimiciii.icustays.icustay_id')), 
                "itemid": Column(Integer, ForeignKey('mimiciii.d_items.itemid')), 
                 "cgid": Column(Integer, ForeignKey('mimiciii.caregivers.cgid'))}) #
    
class CPTevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.cptevents'],
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id'))})
    
# class D_CPT(Base):
#     # not sure we need this, and hard to implement the right way 

class D_ICD_Diagnosis(Base): # 
    __table__ = table_override(metadata.tables['mimiciii.d_icd_diagnoses'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                "icd9_code": Column(Integer, ForeignKey('mimiciii.diagnoses_icd.icd9_code'))}) # is this right? 
    
class D_ICD_Procedure(Base):
    __table__ = table_override(metadata.tables['mimiciii.d_icd_procedures'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True)})

class D_Item(Base):
    __table__ = table_override(metadata.tables['mimiciii.d_items'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True)})
    
    chartevents = relationship('Chartevent')
    datetimeevents = relationship('Datetimeevent')
    

class D_Labitem(Base):
    __table__ = table_override(metadata.tables['mimiciii.d_labitems'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True)})
    
    labevents = relationship('Labevent')

class Datetimeevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.datetimeevents'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid')), 
                'itemid': Column(Integer, ForeignKey('mimiciii.d_items.itemid')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id'))                
                })

class Diagnosis_ICD(Base):
    __table__ = table_override(metadata.tables['mimiciii.diagnoses_icd'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id'))
                })
    d_icd_diagnoses = relationship('D_ICD_Diagnosis') # is this right? see mimic online 

class Drgcode(Base):
    __table__ = table_override(metadata.tables['mimiciii.drgcodes'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id'))})

class Icustay(Base):
    __table__ = table_override(metadata.tables['mimiciii.icustays'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id'))})
    
    chartevents = relationship('Chartevent')
    datetimeevents = relationship('Datetimeevent')
    inputevents_cv = relationship('Inputevent_CV')
    inputevents_mv = relationship('Inputevent_MV')
    outputevents = relationship('Outputevent')
    prescriptions = relationship('Prescription')
    procedureevents_mv = relationship('Procedureevent_MV')
    transfers = relationship('Transfer')
        
class Inputevent_CV(Base):
    __table__ = table_override(metadata.tables['mimiciii.inputevents_cv'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid'))})
    
class Inputevent_MV(Base):
    __table__ = table_override(metadata.tables['mimiciii.inputevents_mv'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid'))})
        
class Labevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.labevents'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')),
                'itemid': Column(Integer, ForeignKey('mimiciii.d_labitems.itemid'))})
    
    
    
class Microbiologyevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.microbiologyevents'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id'))})
    
class Noteevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.noteevents'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid'))})
    
class Outputevent(Base):
    __table__ = table_override(metadata.tables['mimiciii.outputevents'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True),  
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid')),  
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id'))})
    
class Patient(Base): #
    __table__ = table_override(metadata.tables['mimiciii.patients'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True)})
    admissions = relationship('Admission') #
    callouts = relationship('Callout') #
    chartevents = relationship('Chartevent') # 
    cptevents = relationship('CPTevent') 
    datetimeevents = relationship('Datetimeevent')
    diagnoses_ICD = relationship('Diagnosis_ICD')
    drgcodes = relationship('Drgcode')
    icustays = relationship('Icustay')
    inputevents_cv = relationship('Inputevent_CV')
    inputevents_mv = relationship('Inputevent_MV')
    labevents = relationship('Labevent')
    microbiologyevents = relationship('Microbiologyevent')
    noteevents = relationship('Noteevent')
    outputevents = relationship('Outputevent')
    prescriptions = relationship('Prescription')
    procedureevents_mv = relationship('Procedureevent_MV')
    procedures_icd = relationship('Procedure_ICD')
    services = relationship('Service')
    transfers = relationship('Transfer')
    
    @property
    def person(self):
        '''
        Create a standard Person. Set attributes in the arguments to match init over in Standard
        Have this create all of the needed information 
        '''        
        person = OMOPPerson(person_id=self.subject_id, DOB=self.dob, DOD=self.dod, 
                          gender=self.gender, expire_flag=self.expire_flag, 
                          drug_exposures = self.drug_exposures, visit_occurances = self.visit_occurances, 
                          procedures = self.procedures, observations = self.observations, 
                          conditions = self.conditions, death = self.death, index_admission = None)
        # for testing
        print("person id {0}").format(person.person_id)
        return person
    
   
    
    @property
    def visit_occurances(self):
        visit_occurances = self.admissions
        return_occurances = [] 
        for visit_occurance in visit_occurances:
            return_occurances.append(OMOPVisitOccurance(visit_occurance_id=visit_occurance.row_id, 
                                  person_id=self.subject_id, 
                                  visit_start_date=visit_occurance.admittime, 
                                  visit_end_date = visit_occurance.dischtime, 
                                  place_of_service_source_value=visit_occurance.admission_location, 
                                  diagnosis = visit_occurance.diagnosis, 
#                                   time_in_ed = something_calculated, # define how to calculate this
                                  admission_type = visit_occurance.admission_type))
        return return_occurances
    
    @property 
    def drug_exposures(self): 
        """ 
        is subject_id the right argument here? Ideally you'd want to pass in a person object? 
        """
         
        drug_exposures = self.prescriptions
        return_occurances = [] 
        for drug_exposure in drug_exposures: 
            return_occurances.append(OMOPDrugExposure(visit_occurance_id= drug_exposure.hadm_id, 
                                exposure_id=drug_exposure.row_id, 
                                person_id= self.subject_id, 
                                starttime=drug_exposure.startdate, 
                                endtime=drug_exposure.enddate, 
                                ndc=drug_exposure.ndc))
        return return_occurances
#     
    @property    
    def procedures(self):
        procedures = self.procedureevents_mv
        return_procedures = [] 
        for procedure in procedures: 
            return_procedures.append(OMOPProcedureOccurance(
                                          procedure_occurance_id = procedure.row_id, 
                                          person_id = self.subject_id, 
                                          procedure_date = procedure.starttime, 
                                          provider_id = procedure.cgid))
            
        return return_procedures
    
    @property        
    def observations(self):
        observations = self.labevents
        return_observations = [] 
        for observation in observations: 
            return_observations.append(OMOPObservation(observation_id = observation.row_id, 
                               person_id = self.subject_id, 
                               observation_date = observation.charttime, # format
                               observation_time = observation.charttime, # format
                               admission_id = observation.hadm_id, 
                               observation_type = observation.itemid, 
                               observation_value = observation.value))
        return return_observations
     
    @property   
    def conditions(self):
        conditions = self.diagnoses_ICD
        return_conditions = []
        for condition in conditions: 
            return_conditions.append(OMOPConditionOccurance(condition_occurance_id = condition.row_id , 
                                      person_id = self.subject_id, 
                                      admission_id = condition.hadm_id,
                                      icd9_code = None, 
                                      icd9_title = None))
#                                       icd9_code = condition.ICD9_code, 
#                                       icd9_title = condition.ICD9_code)) # throwing error about ICD9_code existing
        
    @property    
    def death(self):
        """ 
        - Currently just based off Admissions / Diagnosis_ICD data; there may be chart data that helps 
        """
        if self.expire_flag ==  1:
            admissions = self.admissions
            for admission in admissions: 
                if admission.hospital_expire_flag ==  1: # contrary to documentation, positive flag is 1, not "Y"
                    death = OMOPDeath(person_id = self.subject_id, death_date = admission.deathtime) # no ICD9_code implemented                            
                else: 
                    death = None  
        else: 
            death = None
        return death
    
#     @property 
#     def providers(self):
#         providers = self.caregivers
#         return_providers = [] 
#         for provider in providers: 
#             return_providers.append(OMOPProvider(provider_id = provider.cgid, label = provider.label))
#             
#         return return_providers
        

class Prescription(Base): 
    __table__ = table_override(metadata.tables['mimiciii.prescriptions'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id'))
                })
#     @property 
#     def drug_exposure(self): 
#         """ 
#         is subject_id the right argument here? Ideally you'd want to pass in a person object? 
#         """
#         return OMOPDrugExposure(visit_occurance_id= self.hadm_id, 
#                                 exposure_id=self.row_id, 
#                                 person_id= self.subject_id, 
#                                 starttime=self.startdate, 
#                                 endtime=self.enddate, 
#                                 ndc=self.ndc)
   

class Procedureevent_MV(Base):
    __table__ = table_override(metadata.tables['mimiciii.procedureevents_mv'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id')), 
                'cgid': Column(Integer, ForeignKey('mimiciii.caregivers.cgid'))})
    
class Procedure_ICD(Base):
    __table__ = table_override(metadata.tables['mimiciii.procedures_icd'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id'))})
    
class Service(Base):
    __table__ = table_override(metadata.tables['mimiciii.services'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True),
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id'))})
    
class Transfer(Base):
    __table__ = table_override(metadata.tables['mimiciii.transfers'], 
               Base, 
               {"row_id": Column(Integer, primary_key =True), 
                'hadm_id': Column(Integer, ForeignKey('mimiciii.admissions.hadm_id')), 
                'subject_id': Column(Integer, ForeignKey('mimiciii.patients.subject_id')), 
                'icustay_id': Column(Integer, ForeignKey('mimiciii.icustays.icustay_id'))})
