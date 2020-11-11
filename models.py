from exts import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) 
    username = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    records = db.relationship('Record', backref="user", lazy='dynamic')
    def __init__(self, *args, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        records = kwargs.get('records')
        email = kwargs.get('email')
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result
    def __repr__(self):
        return '<id:%d username:%s email:%s password:%s records:%s>' % (self.id, self.username, self.email, self.password, self.records)

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text(200), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.Text(50), nullable=True)
    finish_time = db.Column(db.DateTime)
    status = db.Column(db.Boolean, nullable=True, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    def __repr__(self):
        return '<id:%d description:%s date:%s title:%s finish_time:%s status:%d user_id:%s' % \
               (self.id, self.description, self.date,self.title, self.finish_time, self.status, self.user_id)
