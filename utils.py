from flask import g

# log-in log to record current username
def login_log():
    print('Current log in user:' + g.username)
