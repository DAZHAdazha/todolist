from exts import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'  # 表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)  # autoincrement为自增
    username = db.Column(db.String(16), unique=True, nullable=False)  # nullable=False 不能为空
    age = db.Column(db.Integer)
    phone = db.Column(db.String(11))
    password = db.Column(db.Text)
    # content = db.Column(db.Text) # text类型为无限长度的字符串

    def __init__(self, *args, **kwargs):
        username = kwargs.get('username')
        phone = kwargs.get('phone')
        password = kwargs.get('password')
        age = kwargs.get('age')
        self.phone = phone
        self.age = age
        self.username = username
        # 加密密码，注意需要导入
        self.password = generate_password_hash(password)

    # 检查密码函数
    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result

    def __repr__(self):
        return '<id:%d username:%s age:%d phone:%s password:%s >' % (self.id, self.username, self.age, self.phone, self.password)


class User_Data(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    list = db.Column(db.Text)
    # 第一参数为要关联的表的模型的名字,作为正向引用，backref表示反向引用，以后可以通过User.user_datas反向引用来通过user对象查找
    # 对应User_data表的数据
    user = db.relationship('User', backref=db.backref("user_datas"))

    def __repr__(self):
        return '<id:%d username:%s list:%s >' % (self.id, self.username, self.list)


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    title = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

    def __repr__(self):
        return '<id:%d description:%s date:%s title:%s deadline:%s status:%d' % (self.id, self.description, self.date
                                                                            /self.title, self.deadline, self.status)
