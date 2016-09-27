from .resources import metadata_filename
import pickle

with open(metadata_filename, 'rb') as infile: 
    metadata = pickle.load(infile)
    
    # this just grabs the metadata so you can import it - Jason 