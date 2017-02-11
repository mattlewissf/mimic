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

'''
 Settings? Mappings? Pulling these from the test file and trying to re-work them
- Does any of this belong here or does it belong somewhere else? 
'''
    
# # Create a test database and table
# engine = create_engine('sqlite://') # does this need to be something else? 
# metadata = MetaData(bind=engine)


# # Define the mapping between tables and objects for writing
# patients_table = table_from_class(Patient, metadata, 'patients')
# admissions_table = table_from_class(Admission, metadata, 'admissions')
# caregivers_table = table_from_class(Caregiver, metadata, 'caregivers')
# callouts_table = table_from_class(Callout, metadata, 'callouts')
# chartevents_table = table_from_class(ChartEvent, metadata, 'chartevents')
# cptevents_table = table_from_class(CPTevent, metadata, 'cptevents')
# # d_icd_diagnoses_table = table_from_class(D_ICD_Diagnosis, metadata, 'd_icd_diagnoses') # hold
# # d_icd_procedures_table = table_from_class(D_ICD_Procedure, metadata, 'd_icd_procedures') # hold
# d_items_table = table_from_class(D_Item, metadata, 'd_items')
# d_labitems_table = table_from_class(D_Labitem, metadata, 'd_labitems')
# datetimeevents_table = table_from_class(Datetimeevent, metadata, 'datetimeevents')
# diagnosis_icd_table = table_from_class(Diagnosis_ICD, metadata, 'diagnoses_icd')
# drg_codes_table = table_from_class(Drgcode, metadata, 'drgcodes')
# icustay_codes_table = table_from_class(Icustay, metadata, 'icustays')
# inputevents_cv_table = table_from_class(Inputevent_CV, metadata, 'inputevents_cv')
# inputevents_mv_table = table_from_class(Inputevent_MV, metadata, 'inputevents_mv')
# labevents_table = table_from_class(Labevent, metadata, 'labevents')
# microbiologyevents_table = table_from_class(Microbiologyevent, metadata, 'microbiologyevents')
# noteevents_table = table_from_class(Noteevent, metadata, 'noteevents')
# outputevents_table = table_from_class(Outputevent, metadata, 'outputevents')
# prescrptions_table = table_from_class(Prescription, metadata, 'prescriptions')
# procedureevents_mv_table = table_from_class(Procedureevent_MV, metadata, 'procedureevents_mv')
# procedures_icd_table = table_from_class(Procedure_ICD, metadata, 'procedures_icd')
# services_table = table_from_class(Service, metadata, 'services')
# transfers_table = table_from_class(Transfer, metadata, 'transfers')

# metadata.create_all()


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
#     writer_config = {
#                     Patient: SqaWriterConfig(patients_table, create_table_if_not_exist=True),
#                     Admission: SqaWriterConfig(admissions_table, create_table_if_not_exist=True),
#                     Caregiver: SqaWriterConfig(caregivers_table, create_table_if_not_exist=True),
#                     Callout: SqaWriterConfig(callouts_table, create_table_if_not_exist=True),
#                     ChartEvent: SqaWriterConfig(chartevents_table, create_table_if_not_exist=True),
#                     CPTevent: SqaWriterConfig(cptevents_table, create_table_if_not_exist=True),
#     #                 D_ICD_Diagnosis: SqaWriterConfig(d_icd_diagnoses_table, create_table_if_not_exist=True),
#     #                 D_ICD_Procedure: SqaWriterConfig( d_icd_procedures_table, create_table_if_not_exist=True),
#                     D_Item: SqaWriterConfig(d_items_table, create_table_if_not_exist=True),
#                     D_Labitem: SqaWriterConfig(d_labitems_table, create_table_if_not_exist=True),
#                     Datetimeevent: SqaWriterConfig(datetimeevents_table, create_table_if_not_exist=True),
#                     Diagnosis_ICD: SqaWriterConfig(diagnosis_icd_table, create_table_if_not_exist=True),
#                     Drgcode: SqaWriterConfig(drg_codes_table, create_table_if_not_exist=True),
#                     Icustay: SqaWriterConfig(icustay_codes_table, create_table_if_not_exist=True),
#                     Inputevent_CV: SqaWriterConfig(inputevents_cv_table, create_table_if_not_exist=True),
#                     Inputevent_MV: SqaWriterConfig(inputevents_mv_table, create_table_if_not_exist=True),
#                     Labevent: SqaWriterConfig(labevents_table, create_table_if_not_exist=True),
#                     Microbiologyevent: SqaWriterConfig(microbiologyevents_table, create_table_if_not_exist=True),
#                     Noteevent: SqaWriterConfig(noteevents_table, create_table_if_not_exist=True),
#                     Outputevent: SqaWriterConfig(outputevents_table, create_table_if_not_exist=True),
#                     Prescription: SqaWriterConfig(prescrptions_table, create_table_if_not_exist=True),
#                     Procedureevent_MV: SqaWriterConfig(procedureevents_mv_table, create_table_if_not_exist=True),
#                     Procedure_ICD: SqaWriterConfig(procedures_icd_table, create_table_if_not_exist=True),
#                     Service: SqaWriterConfig(services_table, create_table_if_not_exist=True),
#                     Transfer: SqaWriterConfig(transfers_table, create_table_if_not_exist=True)
#                     }
#     return writer_config
            

# Define the mapping between tables and objects for reading
def create_sqa_reader_config(connection_string, table_names=None, schema='mimiciii', **kwargs):
    engine = create_engine(connection_string, echo=True)
    metadata = MetaData(bind=engine, schema=schema)
    tables = create_tables(metadata, table_names)
    reader_config = {klass: SqaReaderConfig(table, engine, **kwargs) for klass, table in tables.items()}
    return reader_config
#     reader_config = {
#                     Patient: SqaReaderConfig(patients_table, engine),
#                     Admission: SqaReaderConfig(admissions_table, engine),
#                     Caregiver: SqaReaderConfig(caregivers_table, engine),
#                     Callout: SqaReaderConfig(callouts_table, engine),
#                     ChartEvent: SqaReaderConfig(chartevents_table, engine),
#                     CPTevent: SqaReaderConfig(cptevents_table, engine),
#     #                 D_ICD_Diagnosis: SqaReaderConfig(d_icd_diagnoses_table, engine),
#     #                 D_ICD_Procedure: SqaReaderConfig( d_icd_procedures_table, engine),
#                     D_Item: SqaReaderConfig(d_items_table, engine),
#                     D_Labitem: SqaReaderConfig(d_labitems_table, engine),
#                     Datetimeevent: SqaReaderConfig(datetimeevents_table, engine),
#                     Diagnosis_ICD: SqaReaderConfig(diagnosis_icd_table, engine),
#                     Drgcode: SqaReaderConfig(drg_codes_table, engine),
#                     Icustay: SqaReaderConfig(icustay_codes_table, engine),
#                     Inputevent_CV: SqaReaderConfig(inputevents_cv_table, engine),
#                     Inputevent_MV: SqaReaderConfig(inputevents_mv_table, engine),
#                     Labevent: SqaReaderConfig(labevents_table, engine),
#                     Microbiologyevent: SqaReaderConfig(microbiologyevents_table, engine),
#                     Noteevent: SqaReaderConfig(noteevents_table, engine),
#                     Outputevent: SqaReaderConfig(outputevents_table, engine),
#                     Prescription: SqaReaderConfig(prescrptions_table, engine),
#                     Procedureevent_MV: SqaReaderConfig(procedureevents_mv_table, engine),
#                     Procedure_ICD: SqaReaderConfig(procedures_icd_table, engine),
#                     Service: SqaReaderConfig(services_table, engine),
#                     Transfer: SqaReaderConfig(transfers_table, engine)
#                     }
#     return reader_config



if __name__ == '__main__':
    pass