'''
Created on Jan 26, 2017

@author: mattlewis
'''

from itertools import islice
from oreader.base import IntegerColumn, StringColumn, RealColumn, DateColumn,\
    DateTimeColumn
from sqlalchemy.sql.sqltypes import Integer, String, Float, Date, DateTime
from sqlalchemy.sql.schema import Column, Table, MetaData
from mimic_package.data_model.oreader_mapper import Patient, Admission,\
    Caregiver, Callout, ChartEvent, CPTevent, D_Item, D_Labitem, Datetimeevent,\
    Diagnosis_ICD, Drgcode, Icustay, Inputevent_CV, Inputevent_MV, Labevent,\
    Microbiologyevent, Noteevent, Outputevent, Prescription, Procedureevent_MV,\
    Procedure_ICD, Service, Transfer
from oreader.writer_configs import SqaWriterConfig
from oreader.reader_configs import SqaReaderConfig
from sqlalchemy.engine import create_engine

'''
Holding as where I am putting all of the reader config stuff that was in oreader_mapper
Subject to change 
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
    elif isinstance(col, DateTimeColumn):
        sqa_type = DateTime()
    else:
        assert('Got a {0} type for {1}').format(type(col), col.name)
    name = col.name
    return Column(name, sqa_type)

def table_from_class(klass, metadata, name):
    cols = [sqa_col(col) for col in klass.columns]
    return Table(name, metadata, *cols)

all_classes = [Patient, Admission, Caregiver, Callout, ChartEvent, CPTevent, D_Item, D_Labitem, Datetimeevent, 
               Diagnosis_ICD, Drgcode, Icustay, Inputevent_CV, Inputevent_MV, Labevent, Microbiologyevent,
               Noteevent, Outputevent, Prescription, Procedureevent_MV, Procedure_ICD, Service, Transfer]

default_table_names = {Patient: 'patients', Admission: 'admissions', Caregiver: 'caregivers', 
                       Callout: 'callouts', ChartEvent: 'chartevents', 
                       CPTevent: 'cptevents', D_Item: 'd_items', D_Labitem: 'd_labitems', Datetimeevent: 'datetimeevents', 
                       Diagnosis_ICD: 'diagnoses_icd', Drgcode: 'drgcodes', Icustay: 'icustays', Inputevent_CV: 'inputevents_cv', 
                       Inputevent_MV: 'inputevents_mv', Labevent: 'labevents', Microbiologyevent: 'microbiologyevents',
                       Noteevent: 'noteevents', Outputevent: 'outputevents', Prescription: 'prescriptions', 
                       Procedureevent_MV: 'procedureevents_mv', Procedure_ICD: 'procedures_icd', 
                       Service: 'services', Transfer: 'transfers'}

def create_tables(metadata, table_names=None):
    table_names_ = default_table_names.copy()
    if table_names is not None:
        table_names_.update(table_names)
    return {klass: table_from_class(klass, metadata, table_names_[klass]) for klass in all_classes}

# Define the mapping between tables and objects for writing
def create_sqa_writer_config(connection_string, table_names=None):
    engine = create_engine(connection_string)
    metadata = MetaData(bind=engine)
    tables = create_tables(metadata, table_names)
    writer_config = {klass: SqaWriterConfig(table, create_table_if_not_exist=True) for klass, table in tables.items()}
    return writer_config
            

# Define the mapping between tables and objects for reading
def create_sqa_reader_config(connection_string, table_names=None, schema='mimiciii', echo=False, **kwargs):
    engine = create_engine(connection_string, echo=echo)
    metadata = MetaData(bind=engine, schema=schema)
    tables = create_tables(metadata, table_names)
    reader_config = {klass: SqaReaderConfig(table, engine, **kwargs) for klass, table in tables.items()}
    return reader_config

if __name__ == '__main__':
    pass