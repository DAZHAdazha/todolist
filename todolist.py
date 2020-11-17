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

# capture 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('./HTML/error.html'), 404


# jump to HTML template if the requiring file exists
@app.route('/HTML/<file>')
def jump(file):
    try:
        return render_template('./HTML/' + file)
    except:
        return render_template('./HTML/error.html')


# similar to previous function
@app.route('/<file>')
def jump_to(file):
    try:
        return render_template('./' + file)
    except:
        return render_template('./HTML/error.html')


# view function to render the page createTask.html
@app.route('/HTML/createTask.html')
@login_required
def createTask():
    return render_template('./HTML/createTask.html')


# to render page user.html and passing arguments of 3 type of task counts
@app.route('/HTML/user.html')
@login_required
def user():
    record_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id).scalar()
    completed_count = db.session.query(func.count(Record.id)).filter(Record.user_id == g.user.id, Record.status == True).scalar()
    uncompleted_count = record_count - completed_count
    return render_template('./HTML/user.html', record_count=record_count,
                           completed_count=completed_count, uncompleted_count=uncompleted_count)


#  handling GET and POST request
# for POST, register this user
# for GET, to render page sign-up.html
@app.route('/HTML/sign-up.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter(User.email == data['email']).first()
        # if the email had been used
        if user:
            return "This email had been registered"
        # else it could be signed up
        else:
            new_user = User(username=data['username'], password=data['password'], email=data['email'])
            db.session.add(new_user)
            db.session.commit()
            session['user_email'] = data['email']
            return '1'
    elif request.method == 'GET':
        return render_template('./HTML/sign-up.html')


# handling POST and GET request
# for POST, to log in the user
# for GET, to render log-in.html
@app.route('/HTML/log-in.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter(User.email == data['email']).first()
        # the user is existed
        if user:
            # the user's password is right
            if user.check_password(data['password']):
                session['user_email'] = user.email
                # user ticked the remember-me option
                if data['remember'] == 'true':
                    session.permanent = True
                else:
                    session.permanent = False
                return '1'
            else:
                return "Wrong password, please try again"
        else:
            return "Wrong email address,please try again"
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


# logout view function, delete the sessions
@app.route('/logout/')
@login_required
def logout():
    del session['user_email']
    return redirect(url_for('login'))


# function to see all tasks owned by the user
@app.route('/viewAll/')
@login_required
def viewAll():
    records = Record.query.filter(g.user.id == Record.user_id).order_by('id')
    return render_template('./HTML/result.html', records=records)


# function to see all completed tasks owned by the user
@app.route('/viewCompleted/')
@login_required
def viewCompleted():
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == True).order_by('id')
    return render_template('./HTML/result.html', records=records)


# function to see all uncompleted tasks owned by the user
@app.route('/viewUnompleted/')
@login_required
def viewUncompleted():
    records = Record.query.filter(g.user.id == Record.user_id, Record.status == False).order_by('id')
    return render_template('./HTML/result.html',records=records)


# function to change task status(completed or uncompleted)
@app.route('/taskStatus/<task_id>')
@login_required
def taskStatus(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    # if the record is founded
    if record:
        # if it is true, then set to false, and erase finish time
        if record.status == True:
            record.status = False
            record.finish_time = None
        # else, set to true, and update finish time
        else:
            record.status = True
            current_time = datetime.datetime.now()
            record.finish_time = current_time
        db.session.commit()
    else:
        return render_template('./HTML/error.html')
    return redirect(request.referrer)


# function to handle search request, search for title, description, date, finish time
@app.route('/search/')
@login_required
def search():
    q = request.args.get('q')
    records = Record.query.filter(or_(Record.title.contains(q), Record.description.contains(q),
                                      Record.date.contains(q), Record.finish_time.contains(q)), g.user.id == Record.user_id).order_by('id')
    return render_template('./HTML/result.html', records=records)



# before_request: execute before requests,working as hook function and execute before view functions, and this function is
# a decorator, it could execute codes before view functions
@app.before_request
def my_before_quest():
    email = session.get('user_email')
    if email:
        user = User.query.filter(User.email == email).first()
        g.user = user


# function to check specific task
@app.route('/task/<task_id>')
@login_required
def task(task_id):
    record = Record.query.filter(task_id == Record.id).first()
    if record:
        return render_template('./HTML/task.html', record=record)
    else:
        return render_template('./HTML/error.html')


# function to add a new task
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


# function to update a task
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


# function to delete a task
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
    # !!! only fun for the first time to create all tables in database !!!
    # delete all tables
    # db.drop_all()
    # create al tables
    # db.create_all()

    # set default user admin
    exists = User.query.filter(User.email == 'admin@qq.com').scalar()
    if exists == None:
        admin = User(email="admin@qq.com", username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()
    app.run()
