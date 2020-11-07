from flask import Flask, render_template, flash, request, redirect, url_for, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
import config
from models import User, Record
from exts import db
from utils import login_log
from decorator import login_required
from sqlalchemy import or_
import datetime
from sqlalchemy import func

# 初始化一个flaskd对象 传递一个"__name__"
# 1.方便flask框架去寻找资源
# 2.方便flask插件比如Flask-Sqlalchemy出现错误时，好去寻找出错的位置
app = Flask(__name__)
app.config.from_object(config) # 导入配置文件
db.app = app  # !!!很重要分开models文件时记得加上
db.init_app(app)  # 为解决循环引用问题

# with app.app_context():  #flask中上下文问题，db可以init多个app，但是需要手动将app推入服务器的app栈才能作用，此语句即用于将当前app推入app栈
#     db.create_all()


# jinja2模板加载变量的{{ }}和jquery-tmpl插件中的{{ }}相冲突的解决方案，用于js读取flask传递json数据
app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'

# 配置mysql
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fengyunjia@127.0.0.1:3306/wabao'  # dialect+driver://username:password@hostname/database
# 是否动态修改 如为True 则会消耗性能 且改接口以后会被弃用 不建议开启
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLAlchemy是导入的一个类，因此需要新建一个db对象

# 设置session过期时间
# from datetime import timedelta
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.secret_key = 'dazha' # import os; app.secret_key = os.urandom(24) # 用os库自动生成24位的secret key

passing_data = {'signup_user': 0}  # 若字典中嵌套字典或字典中存储对象，在html中都可以使用object(dic).attr的形式访问变量，也可以使用object(dic)['attr']的形式


# 此处装饰器作用是做一个url与视图函数的映射
@app.route('/', methods=['GET', 'POST']) # url
def index(): # 视图函数
    return render_template('./homePage.html', passing_data=passing_data)


@app.route('/HTML/<file>')
def jump(file):
    # 判断是否注册，若没有注册则初始化数据，否则调用数据库的数据

    return render_template('./HTML/' + file, passing_data=passing_data)


@app.route('/<file>')
def jump_to(file):
    return render_template('./' + file, passing_data=passing_data)


@app.route('/HTML/newTask.html')
@login_required
def newTask():
    return render_template('./HTML/newTask.html', passing_data=passing_data)



@app.route('/HTML/user.html')
@login_required
def user():
    try:
        record_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id).scalar()

        completed_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status ==
                                                                         True).scalar()
        uncompleted_count = record_count - completed_count
    except:
        pass

    return render_template('./HTML/user.html', passing_data=passing_data, record_count=record_count,
                           completed_count=completed_count, uncompleted_count=uncompleted_count)


@app.route('/HTML/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        new_user = User(username=data['username'], password=data['password'])
        user = User.query.filter(User.username == data['username']).first()
        if user:
            return '0'
        else:
            db.session.add(new_user)
            db.session.commit()
            session['user_username'] = data['username']
            return '1'

    elif request.method == 'GET':
        return render_template('./HTML/signup.html', passing_data=passing_data)


@app.route('/login', methods=['POST', 'GET'])
def login():
    data = request.form
    user = User.query.filter(User.username == data['username']).first()
    if user:
        if user.check_password(data['password']):
            session['user_username'] = user.username
            if data['remember'] == 'true':
                session.permanent = True
            else:
                session.permanent = False
            return '1'
        else:
            return '2'
    else:
        return '0'

# 执行顺序： @before_request -> 视图函数 -> @context_processor
# context_processor: 上下文处理器,作为钩子函数
@app.context_processor
def my_context_processor():
    # 判断g对象是否有user属性
    if hasattr(g, 'user'):
        return {'user': g.user}
    else:
        # 注意这个装饰器修饰的钩子函数，必须要返回一个字典，即使为空也要返回
        return {}


@app.route('/logout/')
def logout():
    del session['user_username']
    return redirect(url_for('jump_to', file='HTML/login.html'))


@app.route('/viewAll/')
@login_required
def viewAll():
    record_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id).scalar()
    records = Record.query.filter(g.user.id == Record.user_id).order_by('id')
    return render_template('./HTML/search_result.html', passing_data=passing_data, records=records, count=record_count)


@app.route('/viewCompleted/')
@login_required
def viewCompleted():
    completed_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status ==
                                                                     True).scalar()
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == True).order_by('id')
    return render_template('./HTML/search_result.html', passing_data=passing_data, records=records, count=completed_count)


@app.route('/viewUnompleted/')
@login_required
def viewUncompleted():
    uncompleted_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status ==
                                                                     False).scalar()
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == False).order_by('id')
    return render_template('./HTML/search_result.html', passing_data=passing_data, records=records, count=uncompleted_count)

@app.route('/taskStatus/<task_id>')
@login_required
def taskStatus(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    if record.status == True:
        record.status = False
        record.finish_time = None
    else:
        record.status = True
        current_time = datetime.datetime.now()
        record.finish_time = current_time
    db.session.commit()
    return redirect(request.referrer)


@app.route('/search/')
@login_required
def search():
    # 获取html页面中传入的参数(search?xxx1=xxx1&xxx2=xxx2形式),得到的为字典
    q = request.args.get('q')
    count = db.session.query(func.count(Record.id)).filter(or_(Record.title.contains(q), Record.description.contains(q),
                                      Record.date.contains(q)), g.user.id == Record.user_id).scalar()
    records = Record.query.filter(or_(Record.title.contains(q), Record.description.contains(q),
                                      Record.date.contains(q)), g.user.id == Record.user_id).order_by('id')

    # 若render_template出现error： 不是json type, 则是在html中定义了passing data, 而没有传过去的原因
    # return render_template('./HTML/search_result.html', passing_data=passing_data)
    return render_template('./HTML/search_result.html', passing_data=passing_data, records=records, count=count)


# before_request: 在请求之前执行，作为钩子函数实在视图函数执行之前执行的，这个函数只是一个装饰器，它可以把需要设置为钩子函数的代码放到视图函数执行之前执行
@app.before_request
def my_before_quest():
    username = session.get('user_username')
    if username:
        user = User.query.filter(User.username == username).first()
        g.user = user

@app.route('/viewTask/<task_id>')
@login_required
def viewTask(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    return render_template('./HTML/viewTask.html', passing_data=passing_data, record=record)


@app.route('/addTask/')
@login_required
def addTask():
    title = request.args.get('title')
    description = request.args.get('description')

    current_time = datetime.datetime.now()
    current_user_id = g.user.id

    new_record = Record(user_id=current_user_id, date=current_time, title=title, description=description)

    db.session.add(new_record)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/changeTask/<task_id>')
@login_required
def changeTask(task_id):
    record = Record.query.filter(Record.id == task_id).first()

    title = request.args.get('title')
    description = request.args.get('description')

    record.title = title
    record.description = description

    db.session.commit()

    return redirect(url_for('viewAll'))



@app.route('/removeTask/<task_id>')
@login_required
def removeTask(task_id):
    record = Record.query.filter(Record.id == task_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
    else:
        return render_template('./HTML/404.html', passing_data=passing_data)
    return redirect(request.referrer)


if __name__ == '__main__':
    # 删除表
    # db.drop_all()
    # 创建表
    # db.create_all()

    # set default user admin
    exists = User.query.filter(User.username == 'admin').scalar()
    if exists == None:
        admin = User(username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()


    # user = User(username='dazha',password='111')
    # db.session.add(user)
    #
    #
    # record = Record(description='a new task', title='demo', status=True, user_id=1)
    # db.session.add(record)
    # db.session.commit()
    #
    # user2 = User(username='da',password='121')
    # db.session.add(user2)
    #
    #
    # record2 = Record(description='a aa', title='dem2o', status=True, user_id=1)
    # db.session.add(record2)
    #
    # record3 = Record(description='a aa3', title='dem3o', status=True, user_id=2)
    # db.session.add(record3)
    #
    #
    # record4 = Record(description='a234', title='dem34o', status=False, user_id=2)
    # db.session.add(record4)
    # db.session.commit()


    # new_da = Record.query.filter(Record.user_id=='1').first()
    # new_u = User.query.filter(User.username=='dazha').first()
    # print(new_da.user.username)
    # # 注意反向引用调用的结果需要用for遍历
    # for i in new_u.records:
    #     print(i.title)


    app.run()
