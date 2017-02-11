import os
from mimic_package.connect.locations import features_dir
from mimic_package.data_model.oreader_mapper import Patient
from mimic_package.connect.connect import connection_string
from mimic_package.data_model.configs import create_sqa_reader_config

outfilename = os.path.join(features_dir, 'extracted_features.csv')

reader_config = create_sqa_reader_config(connection_string, limit_per=100, n_tries=10)

reader = Patient.reader(reader_config)

for patient in reader:
    print patient