
local_host = 'localhost'
user = 'mimic'
db = 'mimic'
port = '5432'


connection_string = 'postgresql://{user}@{local_host}:{port}/{db}'.format(user = user, local_host = local_host, db = db, port = port)

