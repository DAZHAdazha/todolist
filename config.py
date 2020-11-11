DEBUG = True
# config database URL here
# format: dialect+driver://username:password@host:port/database       
SQLALCHEMY_DATABASE_URI = 'mysql://root:fengyunjia@127.0.0.1:3306/todo'
# whether open dynamic modification, if it is on, server performance will be curtailed, and this API will be abandoned, thus False is recommended
SQLALCHEMY_TRACK_MODIFICATIONS = False 
# SECRET_KEY
# SQLALCHEMY_DB