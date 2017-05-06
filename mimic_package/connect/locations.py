import os

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, '..', '..', '..', '..', 'data')
export_dir = os.path.join(here, '..', '..', '..', '..', 'exports')
features_dir = os.path.join(data_dir, 'features')
password_file = os.path.join(data_dir, 'crypt', 'password.txt')
