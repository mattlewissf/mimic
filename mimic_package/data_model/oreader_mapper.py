'''
Created on Jan 13, 2017

@author: mattlewis
'''
from mimic_package.data_model.standard import OMOPPerson, OMOPVisitOccurance,\
    OMOPDrugExposure, OMOPProcedureOccurance, OMOPObservation,\
    OMOPConditionOccurance, OMOPDeath
from oreader.base import DataObject, schema, IntegerColumn, StringColumn,\
    RealColumn, DateColumn, backrelate, relate, sqa_schema, DateTimeColumn
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, Date, DateTime
from oreader.writer_configs import SqaWriterConfig
# import names
import random
import numpy as np
import datetime
from oreader.reader_configs import SqaReaderConfig
from itertools import islice, chain, cycle
import unittest
from frozendict import frozendict
from nose.tools import assert_list_equal, assert_raises, assert_equal, eq_
from oreader.groups import create_attribute_group_mixin,\
    AttributeGroup, AttributeGroupList
from mimic_package.data_model.metadata import metadata

'''
These are taken from test_readers_and_writers. 
Seems like this should be hosted somewhere else than that for these purposes 
(or re-written)
'''


class ChartObj(DataObject):
    partition_attribute = 'row_id'


@sqa_schema(metadata.tables['mimiciii.patients'])
class Patient(ChartObj):
    partition_attribute = 'row_id'
    identity_key_ = (('row_id', 'id'),) # this could throw an error 
    sort_key_ = ('row_id',)
    container_key_ = (('row_id', 'id'),) # this is following example in read_write; don't quite get it... 
     
    @property
    def person(self):
        '''
        Create a standard Person. Set attributes in the arguments to match init over in Standard
        Have this create all of the needed information 
        '''        
        person = OMOPPerson(
                          person_id=self.subject_id, 
                          DOB=self.dob, DOD=self.dod, 
                          gender=self.gender, 
                          expire_flag=self.expire_flag, 
                          drug_exposures = self.drug_exposures, 
                          visit_occurances = self.visit_occurances, 
                          procedures = self.procedures, 
                          observations = self.observations, 
                          conditions = self.conditions, 
                          death = self.death, 
                          index_admission = None)
        # for testing
        print("person id {0}").format(person.person_id)
        return person
    
    @property
    def visit_occurances(self):
        visit_occurances = self.admissions
        return_occurances = [] 
        for visit_occurance in visit_occurances:
            return_occurances.append(OMOPVisitOccurance(
                                visit_occurance_id=visit_occurance.row_id, 
                                person_id=self.subject_id, 
                                visit_start_date=visit_occurance.admittime, 
                                visit_end_date = visit_occurance.dischtime, 
                                place_of_service_source_value=visit_occurance.admission_location, 
                                diagnosis = visit_occurance.diagnosis, 
#                                 time_in_ed = something_calculated, # define how to calculate this
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
 
@sqa_schema(metadata.tables['mimiciii.admissions']) 
@backrelate({'admissions': (Patient, True)})
class Admission(ChartObj):
    identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'subject_id') 
    container_key = (('subject_id', 'subject_id'))
     
@sqa_schema(metadata.tables['mimiciii.callout']) # is this table singular?
class Callout(ChartObj):
    identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    sort_key_ = ('row_id', 'subject_id', 'hadm_id') 
    container_key = (('row_id', 'row_id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
     
@sqa_schema(metadata.tables['mimiciii.caregivers'])
class Caregiver(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id'))

@sqa_schema(metadata.tables['mimiciii.chartevents'])
class ChartEvent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'), ('icustay_id', 'icustay_id'), \
                     ('item_id', 'item_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id', 'subject_id', 'hadm_id') 
    container_key = (('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'), ('icustay_id', 'icustay_id'), \
                     ('item_id', 'item_id'), ('cgid', 'cgid'))
 
   
@sqa_schema(metadata.tables['mimiciii.cptevents'])
class CPTevent(ChartObj):
        identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
        sort_key_ = ('row_id', 'subject_id', 'hadm_id')
        container_key = (('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))

@sqa_schema(metadata.tables['mimiciii.d_icd_diagnoses'])
class D_ICD_Diagnosis(ChartObj):
    pass
    # See original mapper - unclear if needed

@sqa_schema(metadata.tables['mimiciii.d_icd_procedures'])
class D_ICD_Procedure(ChartObj):
    pass
    # See original mapper - unclear if needed

@sqa_schema(metadata.tables['mimiciii.d_items'])    
class D_Item(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.d_labitems'])
class D_Labitem(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.datetimeevents'])
class Datetimeevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id' ), ('itemid', 'itemid'), ('cgid', 'cgid'), \
                     ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    sort_key_ = ('row_id')
    container_key = (('icustay_id', 'icustay_id' ), ('itemid', 'itemid'), ('cgid', 'cgid'), \
                     ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    

@sqa_schema(metadata.tables['mimiciii.diagnoses_icd'])
@backrelate({'diagnoses': (Patient, True)})
class Diagnosis_ICD(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id',)
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

@sqa_schema(metadata.tables['mimiciii.drgcodes'])
class Drgcode(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 


@sqa_schema(metadata.tables['mimiciii.icustays'])
class Icustay(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

@sqa_schema(metadata.tables['mimiciii.inputevents_cv'])    
class Inputevent_CV(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))

@sqa_schema(metadata.tables['mimiciii.inputevents_mv'])
class Inputevent_MV(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))

# why does 'itemid' not seem right here? Taken from mapper
@sqa_schema(metadata.tables['mimiciii.labevents'])
@backrelate({'labevents': (Patient, True)})
class Labevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('itemid', 'itemid'))
    sort_key_ = ('row_id', 'itemid', 'hadm_id', 'subject_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('itemid', 'itemid')) 

@sqa_schema(metadata.tables['mimiciii.microbiologyevents'])
class Microbiologyevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

@sqa_schema(metadata.tables['mimiciii.noteevents'])
class Noteevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id', 'cgid', 'subject_id', 'icustay_id')
    container_key = (('icustay_id', 'icustay_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))


@sqa_schema(metadata.tables['mimiciii.outputevents'])
class Outputevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id', 'icustay_id', 'hadm_id') # does it need all? 
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))


@sqa_schema(metadata.tables['mimiciii.prescriptions'])
@backrelate({'prescriptions': (Patient, True)})
class Prescription(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'icustay_id','hadm_id', 'subject_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))

@sqa_schema(metadata.tables['mimiciii.procedureevents_mv'])
@backrelate({'procedures': (Patient, True)})
class Procedureevent_MV(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id',)
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))

@sqa_schema(metadata.tables['mimiciii.procedures_icd'])
class Procedure_ICD(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

@sqa_schema(metadata.tables['mimiciii.services'])
class Service(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
    container_key = (('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

@sqa_schema(metadata.tables['mimiciii.transfers'])
class Transfer(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'icustay_id', 'hadm_id', 'subject_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id')) 

