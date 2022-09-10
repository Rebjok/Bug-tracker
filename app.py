from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gjhadkerbouabfue'

#Create CKEditor
ckeditor = CKEditor(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)


db.create_all()


@app.route('/')
def landing_page():
    return render_template('landingpage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if name and email and password:
            hash_and_salted_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            if not User.query.filter_by(email=request.form['email']).first():
                user = User(email=email, password=hash_and_salted_password, name=name)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("You've already signed up with that email, log in instead!")
                return redirect(url_for('login'))
        else:
            flash("Please fill in all fields")
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/ticket/<action>', methods=['GET', 'POST'])
def modify_ticket(action):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['ckeditor']
        ticketType = request.form['type']
        priority = request.form['priority']
        status = request.form['status']
        developer =request.form['developer']
        print(f'{title}, {description}, {ticketType}, {priority}, {status}, {developer}')
        return redirect(url_for('dashboard'))
    else:
        return render_template('modify-ticket.html', action=action)

@app.route('/projects', methods=['GET'])
def projects_dashboard():
    return render_template('project-dashboard.html')

@app.route('/project-details', methods=['GET'])
def project_details():
    return render_template('project-details.html')

@app.route('/project/<action>', methods=['GET', 'POST'])
def modify_project(action):
    if request.method == 'POST':
        print('project modified')
        return redirect(url_for('dashboard'))
    else:
        return render_template('modify-project.html', action=action)

if __name__ == '__main__':
    app.run(debug=True)
