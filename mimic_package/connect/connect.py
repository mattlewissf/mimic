from mimic_package.connect.locations import password_file

local_host = 'localhost'
user = 'mimic'
try:
    with open(password_file, 'rb') as infile:
        password = infile.read().strip()
except:
    password = 'judges' 
db = 'mimic'
port = '5432'


connection_string = 'postgresql://{user}{password}@{local_host}:{port}/{db}'.format(user = user, password=':'+password if password is not None else '', 
                                                                                    local_host = local_host, db = db, port = port)

