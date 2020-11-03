from flask import g


# 登录日志
def login_log():
    print('Current log in user:' + g.username)