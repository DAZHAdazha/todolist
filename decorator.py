from functools import wraps
from flask import redirect, url_for, session


# 登录限制装饰器 增加到购物车等函数
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('jump_to', file='HTML/login.html'))
    return wrapper