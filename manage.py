from flask_script import Manager  # 导入flask_script
from todolist import app # 新建Manager对象需要传递app参数
from db_script import db_manager
from flask_migrate import Migrate, MigrateCommand
from exts import db
from models import User, User_Data, Record  # 数据迁移时需要在manage文件用import引入需要导入Model


manager = Manager(app)


#这块代码用于flask-migrate
# 迁移步骤： 模型 -> 迁移文件(migrations下versions目录中文件) -> 表
# 1.要使用flask-migrate，必须绑定app和db
migrate = Migrate(app, db)
# 2.把MigrateCommand命令添加到manager中
manager.add_command('db', MigrateCommand)
# 3.在terminal中使用先后使用python manage.py db init以及python manage.py db migrate,最后python manage.py db upgrade
# init为初始化，migrate为生成迁移文件,upgrade为将迁移文件映射成表,因此在初始化后若要在服务器运行时更改数据库模型则只用运行后两个命令




# 将数据库相关的操作可以全部放到db_script文件
# 这块代码对应db_script文件
#manager.add_command('db', db_manager)  # 'db'为自定义的命令子名称，
# 在命令行中可使用python manage.py db init(注意仍是manage.py文件，'init'为db_script文件中定义的command函数)来运行


@manager.command
def runsever(): # 在命令行使用python manage.py runsever 即可运行该函数
    print("server is running")


if __name__ == '__main__':
    manager.run()