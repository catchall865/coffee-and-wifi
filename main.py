import os
from flask import Flask, render_template, url_for, redirect, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from forms import RegisterUserForm, LoginUserForm, NewStoreForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

db = SQLAlchemy()

app = Flask(__name__)
Bootstrap(app=app)

KEY = os.urandom(12).hex()
app.config['SECRET_KEY'] = KEY


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffee_and_wifi.db'
db.init_app(app=app)

login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.is_authenticated and current_user.id != 1):
            abort(403)
        else:
            return function(*args, **kwargs)
    return wrapper_function

# Database models
class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    maps_url = db.Column(db.String(200), unique=False, nullable=True)
    seating = db.Column(db.Integer, nullable=False)
    wifi_rating = db.Column(db.Integer, nullable=False)
    power_rating = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='stores')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    pw = db.Column(db.String(100), unique=False, nullable=False)

    stores = relationship('Store', back_populates='user')

# with app.app_context():
#     db.create_all()

# Page routing
@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        user_stores = Store.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', stores=user_stores)
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = NewStoreForm()
    if request.method == 'POST':
        new_store = Store(
            name=request.form['name'],
            maps_url=request.form['maps_url'],
            seating=request.form['seating'],
            wifi_rating=request.form['wifi_rating'],
            power_rating=request.form['power_rating'],
            user_id=current_user.id
        )
        db.session.add(new_store)
        db.session.commit()
        flash('You have added a new store to your list.')
        return redirect(url_for('home'))
    return render_template('add_store.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash("It looks like that account already exists. Try logging in!")
            return redirect(url_for('login'))
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            pw=generate_password_hash(request.form['pw'],
                                                method='pbkdf2:sha256',
                                                salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Your account has been registered.')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()
    if request.method != "POST":
        return render_template("login.html", form=form)
    else:
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            flash("That user does not exist. Try again.")
        else:
            if not check_password_hash(user.pw, request.form['pw']):
                flash("Wrong password. Try again.")
            else:
                login_user(user)
                flash("Login successful!")
                return redirect(url_for('home'))
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
