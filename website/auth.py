from flask import Blueprint, render_template, request, flash, redirect
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from . import utils

auth = Blueprint('auth', __name__)

@auth.route('/auth', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.form.get('meta') == 'login':
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect("/")
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')
        else:
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', category='error')
            elif not utils.check_email(email):
                flash('Email is not valid.', category='error')
            elif not utils.check_name(name):
                flash('Name is not valid.', category='error')
            elif not utils.check_pass(password):
                flash('Password is not valid.', category='error')
            else:
                new_user = User(email=email, name=name, alerts="",password=generate_password_hash(password, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect('/')

    if request.method == "GET":
      mode = request.args.get('mode', 'signin')
      return render_template("auth.html", user=current_user, mode = mode)
      
    return render_template("auth.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.',category='success')
    return redirect('/')