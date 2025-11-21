from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def adminrequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role != 1:
            flash("Admin access only.")
            return redirect(url_for("dashboardPage"))
        return f(*args, **kwargs)
    return wrapper

def doctorrequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role != 2:
            flash("Doctor access only.")
            return redirect(url_for("dashboardPage"))
        return f(*args, **kwargs)
    return wrapper

def patientrequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role != 3:
            flash("Patient access only.")
            return redirect(url_for("dashboardPage"))
        return f(*args, **kwargs)
    return wrapper
