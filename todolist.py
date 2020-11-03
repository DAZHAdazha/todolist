from flask import Flask, render_template, flash, request, redirect, url_for, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
import config # 导入配置文件
from models import User, User_Data, Record  # database_init
from exts import db
from utils import login_log
from decorator import login_required
from sqlalchemy import or_

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




# # 自定义表单类
# class UserForm(FlaskForm):
#     username = StringField('用户名', validators=[DataRequired()])
#     password = PasswordField('密码', validators=[DataRequired()])
#     password2 = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password', '密码输入不一致')])
#     submit = SubmitField('提交')

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


@app.route('/HTML/user.html')
@login_required
def user():
    return render_template('./HTML/user.html', passing_data=passing_data)

# @app.route('/HTML/<file>', methods=['POST'])
# def cart(file):
#
#     # 1.判断登录
#
#     # 2.服务器操作数据
#
#     # 3.返回新网页
#
#     print(file)
#     return render_template('./HTML/' + file, passing_data=passing_data)


@app.route('/HTML/signup.html', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        data = request.form # 获取post请求的数据
        new_user = User(username=data['username'], age=data['age'], phone=data['phone'], password=data['password'])
        # 此时判断是否有重复用户名
        user = User.query.filter(User.username == data['username']).first()
        if user:
            return '0'

        else:
            new_userdata = User_Data(id=new_user.id, username=new_user.username, cart='')
            db.session.add_all([new_user, new_userdata])
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
        # 保存session id
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
    # session.pop('user_username') 三种形式删除
    # session.clear()  #删除全部session
    del session['user_username']
    return redirect(url_for('jump_to', file='HTML/login.html'))  # 向redirect传参数


@app.route('/buy')
@login_required
def buy():
    # 注意之后添加数据库模型物品的表之后 对应外键的值也应该注明 见知了课堂实战视频p13 7:40处
    user = g.user
    print(user.username)
    return 'here'


@app.route('/search/')
def search():
    # 获取html页面中传入的参数(search?xxx1=xxx1&xxx2=xxx2形式),得到的为字典
    q = request.args.get('q')
    # 根据名字查找 使用"or_"module需要引入

    # products = Product.query.filter(or_(Product.name.contains(q), Product.price.contains(q), Product.seller.contains(q))).order_by('id')

    # 与操作
    # products = Product.query.filter(Product.name.contains(q), Product.price.contains(q), Product.seller.contains(q)).order_by('id')

    # 若render_template出现error： 不是json type, 则是在html中定义了passing data, 而没有传过去的原因
    return render_template('./HTML/search_result.html', passing_data=passing_data, records=records)


# before_request: 在请求之前执行，作为钩子函数实在视图函数执行之前执行的，这个函数只是一个装饰器，它可以把需要设置为钩子函数的代码放到视图函数执行之前执行
@app.before_request
def my_before_quest():
    # 若session中有登录的信息就把session中信息存入g对象,这样就避免重复去服务器获取session信息
    username = session.get('user_username')
    if username:
        user = User.query.filter(User.username == username).first()
        g.user = user


@app.route('/addCart/<product_name>')
@login_required
def addCart(product_name):
    user = User.query.filter(User.username == g.user.username).first()
    for i in user.user_datas:
        i.cart += product_name + ','
    db.session.commit()
    g.user = user
    # 返回当前页面
    return redirect(request.referrer)


@app.route('/removeCart/<product_name>')
@login_required
def removeCart(product_name):
    user = User.query.filter(User.username == g.user.username).first()
    for i in user.user_datas:
        i.cart = i.cart.replace(product_name, '', 1)
    db.session.commit()
    g.user = user
    # 返回当前页面
    return redirect(request.referrer)


@app.route('/HTML/cart.html')
@login_required
def cart():
    for i in g.user.user_datas:
        cart_list = i.cart.split(',')
    cart_list.pop()
    cart_item = []
    for i in cart_list:
        # product = Product.query.filter(Product.name == i).first()
        # new_product = {'name': product.name, 'price': product.price, 'seller': product.seller, 'img_path': product.img_path,
                       'product_path': product.product_path, 'seller_path': product.seller_path}
        # cart_item.append(new_product)
    return render_template('/HTML/cart.html', passing_data=passing_data, cart_item=cart_item)



# @app.route('/', methods=['GET', 'POST'])
# def login():
#
#     # 创建自定义的表单类
#     user_form = UserForm()
#
#     # 调用WTF的函数实现验证
#     if user_form.validate_on_submit():
#         # 验证通过获取数据
#         username = user_form.username.data
#         password = user_form.password.data
#
#         user = User.query.filter_by(username=username).first() # 返回第一个数据 没有的话返回none
#         # User.query.filter(User.password == 'hahaha') # 此时是sql语句
#         # result = User.query.filter(User.password == 'hahaha').all() # 现在才是结果,返回对象数组，如没有会报错
#
#         if user:
#             flash('已存在同名用户')
#
#         else:
#             try:
#                 new_user = User(username=username, password=password)
#                 db.session.add(new_user)
#                 db.session.commit()
#
#             except Exception as e:
#                 print(e)
#                 flash('添加新用户')
#                 db.session.rollback()
#     else:
#         if request.method == 'POST':
#             flash('参数不全或两次密码填写不一致')
#
#     # 查询所有的作者信息，让信息传递给模板
#     users = User.query.all()
#
#     return render_template('./wabao/index.html', users=users, form=user_form)
#
# @app.route('/delete_user/<username>') # '<>'传递参数
# def delete_user(username):
#     user = User.query.get(username)
#     if user:
#         try:
#             db.session.delete(user)
#             db.session.commit()
#         except Exception as e:
#             print(e)
#             flash('删除用户出错')
#             db.session.rollback()
#     else:
#         flash('无该用户')
#         # 需要返回当前网址 ——>重定向
#         # return redirect('www.baidu.com') # redirect 用来重定向
#         # return redirect('/')
#         # url_for('index') 需要传入识图函数名，返回视图函数对应的路由地址
#     return redirect(url_for('login'))  # 之前的视图函数名为login
#


# @app.route('/get/')
# def get():
#
#     # 添加数据到session中
#     # 操作session时跟操作字典是一样的
#     # 注意使用session需要配置secret key, secret key 作为“盐” 打乱插入到经过算法加密后的数据中，避免他人通过找到加密算法通过逆向生成得到数据
#     # 注意若重启服务器(重新运行代码)后且secret_key是用random生成的话，secret_key值会改变，并导致之前的session数据失效！
#     # 如果没有给session设置过期时间,则默认为会话结束时即失效
#     session['session_data'] = 'example'  # 同样可以使用方法来获得session数据如 session.get('session_data'),后者的好处为如果该值不存在则不会抛出异常而是返回null
#     # 设置session过期时间为一个月31天, 默认为False,若要更改过期时间,则去代码前面查看配置app.config设置'PERMANENT_SESSION_TIMELIFE',该值的数据类型为datetime.timedelay类型
#     session.permanent = True
#     return session.get('session_data')

# # 删除session数据
# @app.route('/deleteSession/')
# def deleteSession():
#     # 先设置
#     session['session_data'] = 'example'
#     # 删除使用pop方法
#     print(session.get('session_data'))
#     session.pop('session_data')
#     print(session.get('session_data'))
#     return 'success'

# #删除session中所有键值对
# @app.route('/clearSession/')
# def clearSession():
#     # 先设置
#     session['session_data'] = 'example'
#     session['session_data2'] = 'example2'
#     # 删除session中所有数据
#     print(session.get('session_data'))
#     print(session.get('session_data2'))
#     session.clear()
#     print(session.get('session_data'))
#     print(session.get('session_data2'))
#     return 'success'

# @app.route('/home/')
# def home():
#     return render_template('home.html')


# # 默认的视图函数只能采用get请求，若向使用post,则应该特殊说明，这里post,get都需要使用
# @app.route('/login/', methods=['POST','GET'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     else:
#         # request.form与request.args类似用来获取post请求的参数，也为字典
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if username == 'DAZHA' and password == '123':
#             # 使用g(global)可以保存全局变量，避免频繁传递参数给多个函数，全局属性g对象在一次请求的变量在其他函数中都可以使用
#             session['username'] = username
#             g.username = username
#             login_log()
#             return '登录成功'
#         else:
#             return '用户名密码错误'


# @app.route('/edit/')
# def edit():
#     if hasattr(g, 'username'):
#         pass  # 修改代码
#         return '修改成功'
#     else:
#         return redirect(url_for('login'))


if __name__ == '__main__':
    # 启动一个应用服务器，来接受用户请求
    # 类似于监听模型
    # while True:
    #   listen()
    # user = User(id=1, username='xixixix', age=20)
    # db.session.add(user)
    # new_data = User_Data(id=1, username="xixixix", favorite='hhh', cart='hehehe', buy='no')
    # db.session.add(new_data)
    # db.session.commit()
    # new_da = User_Data.query.filter(User_Data.favorite=='hhh').first()
    # new_u = User.query.filter(User.username=='xixixix').first()
    # print(new_da.user.username)
    # 注意反向引用调用的结果需要用for遍历
    # for i in new_u.user_datas:
    #     print(i.favorite)

    # 删除表
    # db.drop_all()
    # 创建表
    # db.create_all()
    # 初始化商品数据
    # database_init()
    app.run()
