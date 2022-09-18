from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gjhadkerbouabfue'

#Create CKEditor
ckeditor = CKEditor(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bug-tracker.db"
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
    bio = db.Column(db.String(2500), nullable=True)
    website_url = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(500), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    vulnerability_notification = db.Column(db.Boolean,default=True)
    vulnerability_summary_notification = db.Column(db.Boolean, default=True)
    comment_notification = db.Column(db.Boolean, default=True)
    message_notification = db.Column(db.Boolean, default=False)
    reminders_notification = db.Column(db.Boolean, default=True)
    events_notification = db.Column(db.Boolean, default=True)
    following_notification = db.Column(db.Boolean, default=False)

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=False)
    priority = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    project_manager = db.Column(db.String(100), nullable=False)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    developer = db.Column(db.String(100), nullable=True)

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
        username = request.form['username']
        if name and email and password:
            hash_and_salted_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            if not User.query.filter_by(email=request.form['email']).first():
                user = User(email=email, password=hash_and_salted_password, name=name, username=username)
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

@app.route('/notification-center', methods=['GET', 'POST'])
def notification_center():
    return render_template('notification-center.html')

@app.route('/tickets', methods=['GET'])
def ticket_dashboard():
    return render_template('ticket-dashboard.html')

@app.route('/ticket-details', methods=['GET'])
def ticket_details():
    return render_template('ticket-details.html')

@app.route('/ticket/<action>', methods=['GET', 'POST'])
def modify_ticket(action):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['ckeditor']
        start_date = datetime.date.today()
        deadline = request.form['deadline']
        ticketType = request.form['type']
        priority = request.form['priority']
        status = request.form['status']
        developer =request.form['developer']
        ticket = Ticket(title=title, description=description, start_date=start_date, deadline=deadline, type=ticketType, priority=priority, status=status, developer=developer)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('ticket_details'))
    else:
        return render_template('modify-ticket.html', action=action)

@app.route('/search-ticket', methods=['POST'])
def search_ticket():
    json_data = request.data
    print(json_data)
    return jsonify(message = "Success")

# Ensure tp fix the projects list table button onclick
@app.route('/projects', methods=['GET'])
def projects_dashboard():
    return render_template('project-dashboard.html')

@app.route('/project-details', methods=['GET'])
def project_details():
    return render_template('project-details.html')

@app.route('/project/<action>', methods=['GET', 'POST'])
def modify_project(action):
    if request.method == 'POST':
        project_title = request.form['title']
        description = request.form['ckeditor']
        start_date = datetime.date.today()
        deadline = request.form['deadline']
        priority = request.form['priority']
        status = request.form['status']
        project_manager = request.form['project-manager']

        if project_title and description and deadline and priority and status:
            if action.lower() == 'new':
                # Check if the project name is already used
                ## NOTE VERY IMPORTANT: THIS IS A BUG, IT SHOULD CHECK IF THE CURRENT USER HAS ANY PROJECT CALLED TITLE
                if Project.query.filter_by(title=project_title).first():
                    flash("There already  exists a project with this name1 Please choose another one")
                    return redirect(url_for('modify_project', action=action))

                # Check if the user has selected a project manager
                if not project_manager:
                    flash("Please assign a project manager for your project")
                    return redirect(url_for('modify_project', action=action))

                #Convert deadline to datetime in proper format
                deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d')

                project = Project(title=project_title, description=description, start_date=start_date, deadline=deadline, priority=priority, status=status, project_manager=project_manager)
                db.session.add(project)
                db.session.commit()
                return redirect(url_for('project_details'))

            elif action.lower() == 'edit':
                project = Project(title=project_title, description=description, priority=priority, status=status)
                db.session.add(project)
                db.session.commit()
                return render_template('project_details')

        else:
            flash('Please provide all the fields')
            return redirect(url_for('modify-project'))
    else:
        return render_template('modify-project.html', action=action)

@app.route('/search-project', methods=['POST'])
def search_project():
    json_data = request.data
    print(json_data)
    return jsonify(message = "success 204 - No content")

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/personal-info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        print('Changes Saved')
        return redirect(url_for('personal_info'))
    return render_template('personal-info.html')

@app.route('/account-settings', methods=['GET', 'POST'])
def account_settings():
    if request.method == 'POST':
        print('Changes Saved')
        return redirect(url_for('account_settings'))
    return render_template('account-settings.html')

@app.route('/notification-settings', methods=['GET', 'POST'])
def notification_settings():
    if request.method == 'POST':
        print('Changes Saved')
        return redirect(url_for('notification_settings'))
    return render_template('notification-settings.html')

@app.route('/security-settings', methods=['GET', 'POST'])
def security_settings():
    if request.method == 'POST':
        print('Changes Saved')
        return redirect(url_for('security_settings'))
    return render_template('security-settings.html')

@app.route('/view-profile', methods=['GET'])
def view_user_profile():
    return render_template('user-page.html')

if __name__ == '__main__':
    app.run(debug=True)
