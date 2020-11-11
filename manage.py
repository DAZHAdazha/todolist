from flask_script import Manager
# it need app as argument to create Manager object
from todolist import app
from db_script import db_manager
from flask_migrate import Migrate, MigrateCommand
from exts import db
from models import User, Record

manager = Manager(app)

# this script is used for flask-migrate
# migrate steps: model => migrate files(migrations/versions/xxxfile) => tables in database
# 1.to use flask-migrate, app and db are required to bind
migrate = Migrate(app, db)
# 2. MigrateCommand need to be added to manager
manager.add_command('db', MigrateCommand)
# 3. in terminal, "python manage.py db init" should be used at the first time
# if any changes taken place, "python manage.py db migrate" should be used, then "python manage.py db upgrade"
# init is to initialize all files, migrate is to generate migration files, upgrade will project migration files to tables

# all database related operations could be placed in db_script file
@manager.command
def runsever(): 
    # using python manage.py runsever in commandline
    print("server is running")

if __name__ == '__main__':
    manager.run()
