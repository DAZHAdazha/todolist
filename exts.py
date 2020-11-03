from flask_sqlalchemy import SQLAlchemy

# 解决循环引用问题
db = SQLAlchemy()
