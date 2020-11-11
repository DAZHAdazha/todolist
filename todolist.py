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

# initialize a flask object by transmitting a "__name__"
# 1.convenient for flask frame to locate resource
# 2.convenient for locate errors when flask plug-in like Flask-SqlAlchemy goes wrong
app = Flask(__name__)
# import config file
app.config.from_object(config)
# very important! when dividing models file with this script!
db.app = app
# to solve the problem of recursive reference
db.init_app(app) 

# solution for conflicts between jinja2 templates loading variable identifier "{{ }}" and jQuery-tmpl plug-in identifier"{{ }}",
# using for passing data from flask to json
app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'

# setting session overdue time 
# from datetime import timedelta
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.secret_key = 'dazha' # import os; app.secret_key = os.urandom(24) # 用os库自动生成24位的secret key

# if there is nested dictionary or object stored in dictionary, "object(dic).attr" could be used in HTML to visit variables
# or using the form of "object(dic)['attr']"
passing_data = {'signup_user': 0}  

# this decorator will project to a url view function
@app.route('/', methods=['GET', 'POST']) # url
def index(): # view function
    return render_template('./HTML/index.html')


@app.route('/HTML/<file>')
def jump(file):
    return render_template('./HTML/' + file)


@app.route('/<file>')
def jump_to(file):
    return render_template('./' + file)


@app.route('/HTML/createTask.html')
@login_required
def createTask():
    return render_template('./HTML/createTask.html')


@app.route('/HTML/user-.html')
@login_required
def user():
    record_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id).scalar()
    completed_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status == True).scalar()
    uncompleted_count = record_count - completed_count
    return render_template('./HTML/user-.html', record_count=record_count,
                           completed_count=completed_count, uncompleted_count=uncompleted_count)


@app.route('/HTML/sign-up.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter(User.email == data['email']).first()
        if user:
            return '0'
        else:
            new_user = User(username=data['username'], password=data['password'], email=data['email'])
            db.session.add(new_user)
            db.session.commit()
            session['user_email'] = data['email']
            return '1'
    elif request.method == 'GET':
        return render_template('./HTML/sign-up.html')


@app.route('/HTML/log-in.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter(User.email == data['email']).first()
        if user:
            if user.check_password(data['password']):
                session['user_email'] = user.email
                if data['remember'] == 'true':
                    session.permanent = True
                else:
                    session.permanent = False
                return '1'
            else:
                return '2'
        else:
            return '0'
    else:
        return render_template('./HTML/log-in.html')


# executing sequence： @before_request -> view function -> @context_processor
# context_processor: working as hook
@app.context_processor
def my_context_processor():
    # whether g object has user attribute
    if hasattr(g, 'user'):
        return {'user': g.user}
    else:
        # note that hook functions warpped by this decorator need to return a dictionary(even it is empty)
        return {}


@app.route('/logout/')
@login_required
def logout():
    del session['user_email']
    return redirect(url_for('login'))


@app.route('/viewAll/')
@login_required
def viewAll():
    record_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id).scalar()
    records = Record.query.filter(g.user.id == Record.user_id).order_by('id')
    return render_template('./HTML/new.html', records=records, count=record_count)


@app.route('/viewCompleted/')
@login_required
def viewCompleted():
    completed_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status ==
                                                                     True).scalar()
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == True).order_by('id')
    return render_template('./HTML/new.html', records=records, count=completed_count)


@app.route('/viewUnompleted/')
@login_required
def viewUncompleted():
    uncompleted_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status ==
                                                                     False).scalar()
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == False).order_by('id')
    return render_template('./HTML/new.html',records=records, count=uncompleted_count)

@app.route('/taskStatus/<task_id>')
@login_required
def taskStatus(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    if record:
        if record.status == True:
            record.status = False
            record.finish_time = None
        else:
            record.status = True
            current_time = datetime.datetime.now()
            record.finish_time = current_time
        db.session.commit()
    else:
        return render_template('./HTML/error.html')
    return redirect(request.referrer)


@app.route('/search/')
@login_required
def search():
    q = request.args.get('q')
    count = db.session.query(func.count(Record.id)).filter(or_(Record.title.contains(q), Record.description.contains(q),
                                      Record.date.contains(q), Record.finish_time.contains(q)), g.user.id == Record.user_id).scalar()
    records = Record.query.filter(or_(Record.title.contains(q), Record.description.contains(q),
                                      Record.date.contains(q), Record.finish_time.contains(q)), g.user.id == Record.user_id).order_by('id')
    # return render_template('./HTML/search_result.html', records=records, count=count)
    return render_template('./HTML/new.html', records=records, count=count)



# before_request: execute before requests,working as hook function and execute before view functions, and this function is
# a decorator, it could execute codes before view functions
@app.before_request
def my_before_quest():
    email = session.get('user_email')
    if email:
        user = User.query.filter(User.email == email).first()
        g.user = user


@app.route('/task/<task_id>')
@login_required
def task(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    if record:
        return render_template('./HTML/task.html', record=record)
    else:
        return render_template('./HTML/error.html')


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
    return redirect(url_for('viewAll'))


@app.route('/changeTask/<task_id>')
@login_required
def changeTask(task_id):
    record = Record.query.filter(Record.id == task_id).first()
    if record:
        title = request.args.get('title')
        description = request.args.get('description')
        record.title = title
        record.description = description
        db.session.commit()
    else:
        return render_template('./HTML/error.html')
    return redirect(url_for('viewAll'))


@app.route('/removeTask/<task_id>')
@login_required
def removeTask(task_id):
    record = Record.query.filter(Record.id == task_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
    else:
        return render_template('./HTML/error.html')
    return redirect(request.referrer)


if __name__ == '__main__':
    # delete all tables
    # db.drop_all()
    # create al tables
    # db.create_all()

    # set default user admin
    # 重写！！！！
    # exists = User.query.filter(User.username == 'admin').scalar()
    # if exists == None:
    #     admin = User(username='admin', password='admin')
    #     db.session.add(admin)
    #     db.session.commit()


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
    # record3 = Record(description='a aa3', title='dem3o', status=True, user_id=1)
    # db.session.add(record3)
    #
    #
    # record4 = Record(description='a2dem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4odem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4odem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4o34', title='dem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4o', status=False, user_id=1)
    # db.session.add(record4)
    # db.session.commit()
    #
    # record5 = Record(description='a2dem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaa4o34', title='dem3sdadadadaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4o', status=False, user_id=1,date=datetime.datetime.now())
    # db.session.add(record5)
    # db.session.commit()
    app.run()
