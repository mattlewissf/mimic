'''
Created on Jan 13, 2017

@author: mattlewis
'''
from mimic_package.data_model.mapper import D_Item, Icustay, Chartevent
from mimic_package.data_model.standard import OMOPPerson
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

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def sqa_col(col):
    if isinstance(col, IntegerColumn):
        sqa_type = Integer()
    elif isinstance(col, StringColumn):
        sqa_type = String()
    elif isinstance(col, RealColumn):
        sqa_type = Float()
    elif isinstance(col, DateColumn):
        sqa_type = Date()
    # adding this because we are getting DateTimeColumn objects
    elif isinstance(col, DateTimeColumn):
        sqa_type = DateTime()
    else:
        assert('Got a {0} type for {1}').format(type(col), col.name)
    name = col.name
    return Column(name, sqa_type)

def table_from_class(klass, metadata, name):
    cols = [sqa_col(col) for col in klass.columns]
    return Table(name, metadata, *cols)


class ChartObj(DataObject):
    partition_attribute = 'row_id'


@sqa_schema(metadata.tables['mimiciii.patients'])
class Patient(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id', 'id')
    container_key_ = (('row_id', 'id')) # this is following example in read_write; don't quite get it... 
     
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
 
@sqa_schema(metadata.tables['mimiciii.admissions']) 
# @backrelate({'admissions': (Patient, True)})
class Admission(ChartObj):
    identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'subject_id') 
    container_key = (('subject_id', 'subject_id'))
     
@sqa_schema(metadata.tables['mimiciii.callout']) # is this table singular?
# @backrelate({'callouts': (Patient, True), 'callouts': (Admission, True)})  
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
@backrelate({'chartevents': (Patient, True), 'chartevents': (Admission, True), \
            'chartevents': (Icustay, True), 'chartevents': (D_Item, True), \
            'chartevents': (Caregiver, True)})
class ChartEvent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'), ('icustay_id', 'icustay_id'), \
                     ('item_id', 'item_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id', 'subject_id', 'hadm_id') 
    container_key = (('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'), ('icustay_id', 'icustay_id'), \
                     ('item_id', 'item_id'), ('cgid', 'cgid'))
 
   
@sqa_schema(metadata.tables['mimiciii.cptevents'])
@backrelate({'cptevents': (Patient, True), 'cptevents': (Admission, True)})
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
# @backrelate({'datetimeevents': (Admission, True), 'datetimeevents': })
class Datetimeevent(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id' ), ('itemid', 'itemid'), ('cgid', 'cgid'), \
                     ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    sort_key_ = ('row_id')
    container_key = (('icustay_id', 'icustay_id' ), ('itemid', 'itemid'), ('cgid', 'cgid'), \
                     ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    

@sqa_schema(metadata.tables['mimiciii.diagnoses_icd'])
class Diagnosis_ICD(ChartObj):
    identity_key_ = (('row_id', 'id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id')
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
class Prescription(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'icustay_id','hadm_id', 'subject_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'))

@sqa_schema(metadata.tables['mimiciii.procedureevents_mv'])
class Procedureevent_MV(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id')
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

'''
 Settings? Mappings? Pulling these from the test file and trying to re-work them
- Does any of this belong here or does it belong somewhere else? 
'''
    
# # Create a test database and table
# # Not sure any of this has to be in here in the end 
engine = create_engine('sqlite://') # does this need to be something else? 
metadata = MetaData(bind=engine)


# need to write one of these for all classes 
# Define the mapping between tables and objects for writing
patients_table = table_from_class(Patient, metadata, 'patients')
admissions_table = table_from_class(Admission, metadata, 'admissions')
caregivers_table = table_from_class(Caregiver, metadata, 'caregivers')
callouts_table = table_from_class(Callout, metadata, 'callouts')
chartevents_table = table_from_class(ChartEvent, metadata, 'chartevents')
cptevents_table = table_from_class(CPTevent, metadata, 'cptevents')
# d_icd_diagnoses_table = table_from_class(D_ICD_Diagnosis, metadata, 'd_icd_diagnoses') # hold
# d_icd_procedures_table = table_from_class(D_ICD_Procedure, metadata, 'd_icd_procedures') # hold
d_items_table = table_from_class(D_Item, metadata, 'd_items')
d_labitems_table = table_from_class(D_Labitem, metadata, 'd_labitems')
datetimeevents_table = table_from_class(Datetimeevent, metadata, 'datetimeevents')
diagnosis_icd_table = table_from_class(Diagnosis_ICD, metadata, 'diagnoses_icd')
drg_codes_table = table_from_class(Drgcode, metadata, 'drgcodes')
icustay_codes_table = table_from_class(Icustay, metadata, 'icustays')
inputevents_cv_table = table_from_class(Inputevent_CV, metadata, 'inputevents_cv')
inputevents_mv_table = table_from_class(Inputevent_MV, metadata, 'inputevents_mv')
labevents_table = table_from_class(Labevent, metadata, 'labevents')
microbiologyevents_table = table_from_class(Microbiologyevent, metadata, 'microbiologyevents')
noteevents_table = table_from_class(Noteevent, metadata, 'noteevents')
outputevents_table = table_from_class(Outputevent, metadata, 'outputevents')
prescrptions_table = table_from_class(Prescription, metadata, 'prescriptions')
procedureevents_mv_table = table_from_class(Procedureevent_MV, metadata, 'procedureevents_mv')
procedures_icd_table = table_from_class(Procedure_ICD, metadata, 'procedures_icd')
services_table = table_from_class(Service, metadata, 'services')
transfers_table = table_from_class(Transfer, metadata, 'transfers')

metadata.create_all()



 
# Define the mapping between tables and objects for writing
writer_config = {
                Patient: SqaWriterConfig(patients_table, create_table_if_not_exist=True),
                Admission: SqaWriterConfig(admissions_table, create_table_if_not_exist=True),
                Caregiver: SqaWriterConfig(caregivers_table, create_table_if_not_exist=True),
                Callout: SqaWriterConfig(callouts_table, create_table_if_not_exist=True),
                ChartEvent: SqaWriterConfig(chartevents_table, create_table_if_not_exist=True),
                CPTevent: SqaWriterConfig(cptevents_table, create_table_if_not_exist=True),
#                 D_ICD_Diagnosis: SqaWriterConfig(d_icd_diagnoses_table, create_table_if_not_exist=True),
#                 D_ICD_Procedure: SqaWriterConfig( d_icd_procedures_table, create_table_if_not_exist=True),
                D_Item: SqaWriterConfig(d_items_table, create_table_if_not_exist=True),
                D_Labitem: SqaWriterConfig(d_labitems_table, create_table_if_not_exist=True),
                Datetimeevent: SqaWriterConfig(datetimeevents_table, create_table_if_not_exist=True),
                Diagnosis_ICD: SqaWriterConfig(diagnosis_icd_table, create_table_if_not_exist=True),
                Drgcode: SqaWriterConfig(drg_codes_table, create_table_if_not_exist=True),
                Icustay: SqaWriterConfig(icustay_codes_table, create_table_if_not_exist=True),
                Inputevent_CV: SqaWriterConfig(inputevents_cv_table, create_table_if_not_exist=True),
                Inputevent_MV: SqaWriterConfig(inputevents_mv_table, create_table_if_not_exist=True),
                Labevent: SqaWriterConfig(labevents_table, create_table_if_not_exist=True),
                Microbiologyevent: SqaWriterConfig(microbiologyevents_table, create_table_if_not_exist=True),
                Noteevent: SqaWriterConfig(noteevents_table, create_table_if_not_exist=True),
                Outputevent: SqaWriterConfig(outputevents_table, create_table_if_not_exist=True),
                Prescription: SqaWriterConfig(prescrptions_table, create_table_if_not_exist=True),
                Procedureevent_MV: SqaWriterConfig(procedureevents_mv_table, create_table_if_not_exist=True),
                Procedure_ICD: SqaWriterConfig(procedures_icd_table, create_table_if_not_exist=True),
                Service: SqaWriterConfig(services_table, create_table_if_not_exist=True),
                Transfer: SqaWriterConfig(transfers_table, create_table_if_not_exist=True)
                }
            

# Define the mapping between tables and objects for reading
# what is engine here? why would it be in mppaer
reader_config = {
                Patient: SqaReaderConfig(patients_table, engine),
                Admission: SqaReaderConfig(admissions_table, engine),
                Caregiver: SqaReaderConfig(caregivers_table, engine),
                Callout: SqaReaderConfig(callouts_table, engine),
                ChartEvent: SqaReaderConfig(chartevents_table, engine),
                CPTevent: SqaReaderConfig(cptevents_table, engine),
#                 D_ICD_Diagnosis: SqaReaderConfig(d_icd_diagnoses_table, engine),
#                 D_ICD_Procedure: SqaReaderConfig( d_icd_procedures_table, engine),
                D_Item: SqaReaderConfig(d_items_table, engine),
                D_Labitem: SqaReaderConfig(d_labitems_table, engine),
                Datetimeevent: SqaReaderConfig(datetimeevents_table, engine),
                Diagnosis_ICD: SqaReaderConfig(diagnosis_icd_table, engine),
                Drgcode: SqaReaderConfig(drg_codes_table, engine),
                Icustay: SqaReaderConfig(icustay_codes_table, engine),
                Inputevent_CV: SqaReaderConfig(inputevents_cv_table, engine),
                Inputevent_MV: SqaReaderConfig(inputevents_mv_table, engine),
                Labevent: SqaReaderConfig(labevents_table, engine),
                Microbiologyevent: SqaReaderConfig(microbiologyevents_table, engine),
                Noteevent: SqaReaderConfig(noteevents_table, engine),
                Outputevent: SqaReaderConfig(outputevents_table, engine),
                Prescription: SqaReaderConfig(prescrptions_table, engine),
                Procedureevent_MV: SqaReaderConfig(procedureevents_mv_table, engine),
                Procedure_ICD: SqaReaderConfig(procedures_icd_table, engine),
                Service: SqaReaderConfig(services_table, engine),
                Transfer: SqaReaderConfig(transfers_table, engine)
                }



#     
    
    