'''
Created on Jan 13, 2017

@author: mattlewis
'''
from oreader.test.test_readers_and_writers import table_from_class
from mimic_package.data_model.mapper import D_Item, Icustay

'''
Porting over the mapper.py that currently exists (as an implementation of SQLAlchemy) to OReader
- currently stealing imports from the test_readers_and_writers.py
'''

from oreader.base import DataObject, schema, IntegerColumn, StringColumn,\
    RealColumn, DateColumn, backrelate, relate, sqa_schema
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, Date
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
# Imports from existing code
from mimic_package.data_model.metadata import metadata





class ChartObj(DataObject):
    partition_attribute = 'row_id'


@sqa_schema(metadata.tables['mimiciii.patients'])
class Patient(ChartObj):
    identity_key_ = ('row_id', 'id')
    sort_key_ = ('row_id', 'id')
#     container_key_ = ('school_id', 'school_id')
 
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
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.diagnoses_icd'])
class Diagnosis_ICD(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.drgcodes'])
class Drgcode(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 


@sqa_schema(metadata.tables['mimiciii.icustays'])
class Icustay(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.inputevents_cv'])    
class Inputevent_CV(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.inputevents_mv'])
class Inputevent_MV(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.labevents'])
class Labevent(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.microbiologyevents'])
class Microbiologyevent(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.noteevents'])
class Noteevent(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 


@sqa_schema(metadata.tables['mimiciii.outputevents'])
class Outputevent(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 


@sqa_schema(metadata.tables['mimiciii.prescriptions'])
class Prescription(ChartObj):
    identity_key_ = (('row_id', 'id'))
    sort_key_ = ('row_id')
    container_key = (('row_id', 'id')) 

@sqa_schema(metadata.tables['mimiciii.procedureevents_mv'])
class Procedureevent_MV(ChartObj):
    identity_key_ = (('row_id', 'id'), ('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))
    sort_key_ = ('row_id')
    container_key = (('icustay_id', 'icustay_id'), ('hadm_id', 'hadm_id'), ('subject_id', 'subject_id'), ('cgid', 'cgid'))

@sqa_schema(metadata.tables['mimiciii.procedures'])
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
    
# Create a test database and table
# Not sure any of this has to be in here in the end 
engine = create_engine('sqlite://')
metadata = MetaData(bind=engine)
metadata.create_all()

patients_table = table_from_class(Patient, metadata, 'patients')

# Define the mapping between tables and objects for writing
writer_config = {Patient: SqaWriterConfig(patients_table, create_table_if_not_exist=True)}

# Define the mapping between tables and objects for reading
    # what is engine here? why would it be in mppaer
reader_config = {Patient: SqaReaderConfig(patients_table, engine)}

print('wah')
    
    
    
    