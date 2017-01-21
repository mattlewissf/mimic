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
    RealColumn, DateColumn, backrelate, relate
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
# from frozendict import frozendict
from nose.tools import assert_list_equal, assert_raises, assert_equal, eq_
from oreader.groups import create_attribute_group_mixin,\
    AttributeGroup, AttributeGroupList
# Imports from existing code
from mimic_package.data_model.metadata import metadata


class ChartObj(DataObject):
    partition_attribute = 'row_id'

'''
does this even get a schema? It is the top object for everything
'''
# @schema([IntegerColumn(name='id'), 
#          StringColumn(name='name'), 
#          ])    
class Patient(ChartObj):
    identity_key_ = ('row_id', 'row_id')
    sort_key_ = ('row_id', 'row_id')
#     container_key_ = ('school_id', 'school_id')

@schema([IntegerColumn(name='row_id'), 
         IntegerColumn(name='subject_id') 
         ])       
@backrelate({'admissions': (Patient, True)})
class Admission(ChartObj):
    identity_key_ = (('row_id', 'row_id'), ('subject_id', 'subject_id'))
    sort_key_ = ('row_id', 'subject_id') 
    container_key = (('row_id', 'row_id'), ('subject_id', 'subject_id'))
    

@schema([IntegerColumn(name='row_id'), 
         IntegerColumn(name='subject_id'),
         IntegerColumn(name='hadm_id') 
         ])
@backrelate({'callouts': (Patient, True), 'callouts': (Admission, True)})  
class Callout(ChartObj):
    identity_key_ = (('row_id', 'row_id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    sort_key_ = ('row_id', 'subject_id', 'hadm_id') 
    container_key = (('row_id', 'row_id'), ('subject_id', 'subject_id'), ('hadm_id', 'hadm_id'))
    

class Caregiver(ChartObj):
    pass
    # this doesn't have any fk / check in schema docs again


@schema([IntegerColumn(name='row_id'), 
         IntegerColumn(name='subject_id'),
         IntegerColumn(name='hadm_id'), 
         IntegerColumn(name='icustay_id'), 
         IntegerColumn(name='item_id'), 
         IntegerColumn(name='cgid')
         ])
@backrelate({'chartevents': (Patient, True), 'chartevents': (Admission, True), \
            'chartevents': (Icustay, True), 'chartevents': (D_Item, True), \
            'chartevents': (Caregiver, True)})
class ChartEvent(ChartObj):
    pass

class CPTevent(ChartObj):
    pass

class D_ICD_Diagnosis(ChartObj):
    pass

class D_ICD_Procedure(ChartObj):
    pass
    
class D_Item(ChartObj):
    pass     

class D_Labitem(ChartObj):
    pass

class Datetimeevent(ChartObj):
    pass

class Diagnosis_ICD(ChartObj):
    pass

class Drgcode(ChartObj):
    pass

class Icustay(ChartObj):
    pass

class Inputevent_CV(ChartObj):
    pass

class Inputevent_MV(ChartObj):
    pass

class Labevent(ChartObj):
    pass

class Microbiologyevent(ChartObj):
    pass

class Noteevent(ChartObj):
    pass

class Outputevent(ChartObj):
    pass

class Prescription(ChartObj):
    pass

class Procedureevent_MV(ChartObj):
    pass

class Procedure_ICD(ChartObj):
    pass

class Service(ChartObj):
    pass

class Transfer(ChartObj):
    pass





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
    
    
    
    