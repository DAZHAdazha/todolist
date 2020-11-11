from flask_script import Manager
# "app" is not need to add to Manager() as long as "if __name__ == '__main__'" because this is not the main script
db_manager = Manager()

@db_manager.command
def init():
    print('database had been initialized.')


@db_manager.command
def migrate():
    print('database had been migrated.')