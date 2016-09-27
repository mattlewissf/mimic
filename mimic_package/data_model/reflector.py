# grabs the schema from the db 
# run this any time the schema changes
# side note: metadata.pickle is kept in git 

if __name__ == '__main__': 
    from mimic_package.connect.connect import connection_string
    from sqlalchemy.sql.schema import MetaData
    from sqlalchemy.engine import create_engine
    from mimic_package.data_model.resources import metadata_filename
    import pickle
    
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    
    metadata = MetaData(bind=engine)
    metadata.reflect(schema='mimiciii')
    
    with open(metadata_filename, 'wb') as outfile: 
        pickle.dump(metadata, outfile)
    