from functools import wraps
from flask import redirect, url_for, session, render_template

# login required decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_email'):
            return func(*args, **kwargs)
        else:
            print('fuck')
            return redirect(url_for('login'))
            # return render_template('./HTML/log-in.html')
    return wrapper
