import os

resources = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
metadata_filename = os.path.join(resources, 'metadata.pickle')

# for storing test objects 
testing_pickle_filename = os.path.join(resources, 'testing.pickle')