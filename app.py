from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import and_
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import os
import datetime
import json

## INITIALIZE WEB APP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gjhadkerbouabfue'

# CREATE CKEDITOR
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


##CREATE DATABASE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    account_type = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(2500), nullable=True)
    website_url = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(500), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    vulnerability_notification = db.Column(db.Boolean, default=True)
    vulnerability_summary_notification = db.Column(db.Boolean, default=True)
    comment_notification = db.Column(db.Boolean, default=True)
    message_notification = db.Column(db.Boolean, default=False)
    reminders_notification = db.Column(db.Boolean, default=True)
    events_notification = db.Column(db.Boolean, default=True)
    following_notification = db.Column(db.Boolean, default=False)
    # This will act like a List of ticket objects attached to each User.
    # The "developer" refers to the developer property in the Ticket class.
    tickets = relationship("Ticket", back_populates="developer")
    # This will act like a List of projects managed by each User.
    projects_managed = relationship("Project", back_populates="project_manager")
    # This will act like a List of team member objects attached to each Project.
    # The "project" refers to the project property in the Ticket class.
    team = relationship("Team", back_populates="user")


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=False)
    priority = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    project_manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    # Create reference to the User object, the "tickets" refers to the tickets property in the User class.
    project_manager = relationship("User", back_populates="projects_managed")

    # This will act like a List of ticket objects attached to each Project.
    # The "project_name" refers to the project_name property in the Ticket class.
    tickets = relationship("Ticket", back_populates="project_name")

    # This will act like a List of team member objects attached to each Project.
    # The "project" refers to the project property in the Ticket class.
    team = relationship("Team", back_populates="project")

    # Relationship with company
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    company = relationship("Company", back_populates='projects')


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    # Create a Foreign Key, "projects.id"
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    # Create reference to the Project object
    project_name = relationship("Project", back_populates="tickets")

    description = db.Column(db.String(1000), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    developer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    # Create reference to the User object, the "tickets" refers to the tickets property in the User class.
    developer = relationship("User", back_populates="tickets")


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)

    # Relationship with projects
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="team")

    # Relationship with users
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="team")

    role = db.Column(db.String(100), nullable=False)


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    # Realtionship with projects
    projects = relationship("Project", back_populates="company")


db.create_all()


## ROOT ROUTE
# This is the landing page of the website
@app.route('/')
def landing_page():
    return render_template('landingpage.html')


## REGISTER ROUTES
# This page is used to register new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        username = request.form['username']
        account_type = request.form['account-type']
        if name and email and password and account_type:
            hash_and_salted_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            if not User.query.filter_by(email=request.form['email']).first():
                user = User(email=email, password=hash_and_salted_password, name=name, account_type=account_type,
                            username=username)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("You've already signed up with this email, log in instead!")
                return redirect(url_for('login'))
        else:
            flash("Please fill in all fields")
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


## LOGIN ROUTES
# This route is called when a legitimate user is logging in
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


# This method logs in a demo user when a demo button is clicked in the login page
@app.route('/login-demo/<user>', methods=['GET'])
def login_demo(user):
    if user.lower() == 'admin':
        email = 'demo.admin@email.com'
        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            print('error logging in demo admin')
            return redirect(url_for('login'))
    elif user.lower() == 'pm':
        pass
    elif user.lower() == 'developer':
        pass
    elif user.lower() == 'user':
        pass
    elif user.lower() == 'submitter':
        pass

#This method logs a user out
@app.route("/logout", methods=['GET'])
def log_out():
    logout_user()
    return redirect(url_for('login'))

##DASHBOARD ROUTE
# This is the main dashboard that shows statistics about a stakeholder or company
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    users = User.query.all()
    projects = Project.query.all()
    tickets = Ticket.query.all()
    statistics = {
        'active_projects': Project.query.filter_by(status='Active').count(),
        'total_tickets': Ticket.query.count(),
        'unassigned_tickets': Ticket.query.filter_by(developer=None).count(),
        'new_members': User.query.count(),
        'total_members': User.query.count(),
        'tickets_in_development': Ticket.query.filter(and_(Ticket.status != 'Resolved', Ticket.status != 'Archived')).count(),
        'total_developers': User.query.count(),
        'priority_project_pie': [Project.query.filter_by(priority='Urgent').count(),
                                 Project.query.filter_by(priority='High').count(),
                                 Project.query.filter_by(priority='Medium').count(),
                                 Project.query.filter_by(priority='Low').count()],
        'distribution_bar_data': distribution_list(projects),
        'ticket_distribution_pie': {"data":[len(project.tickets) for project in projects],
                                    'titles': [project.title for project in projects]},
    }
    return render_template('dashboard.html', projects=projects, users=users, tickets=tickets, statistics=statistics)

def distribution_list(projects):
    users_list = []
    developers = []
    pms = []
    distribution_list = []
    for project in projects:
        users_num = 0
        devs = 0
        pm = 1
        for member in project.team:
            if member.role == 'User':
                users_num += 1
            elif member.role == 'Developer':
                devs += 1
        users_list.append(users_num)
        developers.append(devs)
        pms.append(pm)
    distribution_list.append(users_list)
    distribution_list.append(developers)
    distribution_list.append(pms)
    return distribution_list

##NOTIFICATION CENTER ROUTE
# This page displays all the current users notifications
@app.route('/notification-center', methods=['GET', 'POST'])
def notification_center():
    return render_template('notification-center.html')


## TICKET ROUTES
# This is a dashboard for tickets, it displays a list of tickets associated with a stakeholder
@app.route('/tickets', methods=['GET'])
def ticket_dashboard():
    tickets = Ticket.query.all()
    return render_template('ticket-dashboard.html', tickets=tickets)


# This page displays details for a specific ticket
@app.route('/ticket-details/<ticket_id>', methods=['GET'])
def ticket_details(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    return render_template('ticket-details.html', ticket=ticket)


# This page displays a form to edit a ticket or create a new one
@app.route('/ticket/<action>', methods=['GET', 'POST'])
def modify_ticket(action):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['ckeditor']
        project = request.form['ticket-project']
        start_date = datetime.date.today()
        deadline = datetime.datetime.strptime(request.form['deadline'], '%Y-%m-%d')
        ticketType = request.form['type']
        priority = request.form['priority']
        status = request.form['status']
        developer = request.form['developer']
        ticket = Ticket(title=title, description=description, project_id=project, start_date=start_date,
                        deadline=deadline, type=ticketType, priority=priority, status=status, developer_id=developer)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('ticket_details',ticket_id=ticket.id))
    else:
        users = User.query.all()
        projects = Project.query.all()
        return render_template('modify-ticket.html', action=action, users=users, projects=projects)


# This route is called when a user is assigning a project for a new ticket or an edited ticket
@app.route('/search-ticket', methods=['POST'])
def search_ticket():
    json_data = request.data
    print(json_data)
    return jsonify(message="Success")


## PROJECT ROUTES
# This page displays  all projects in a list
# it is a dashboard for projects
# Ensure tp fix the projects list table button onclick
@app.route('/projects', methods=['GET'])
def projects_dashboard():
    projects = Project.query.all()
    return render_template('project-dashboard.html', projects=projects)


# This route displays a page that shows details about a specific project
@app.route('/project-details/<project_id>', methods=['GET'])
def project_details(project_id):
    project = Project.query.filter_by(id=project_id).first()
    users = User.query.all()
    if project:
        return render_template('project-details.html', project=project, users=users)
    else:
        return render_template('404.html')


# This route displays a form page to create a new or edit a project
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

                # Convert deadline to datetime in proper format
                deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d')

                project = Project(title=project_title, description=description, start_date=start_date,
                                  deadline=deadline, priority=priority, status=status,
                                  project_manager_id=project_manager)
                db.session.add(project)
                db.session.commit()
                return redirect(url_for('project_details', project_id=project.id))

            elif action.lower() == 'edit':
                project = Project(title=project_title, description=description, priority=priority, status=status)
                db.session.add(project)
                db.session.commit()
                return render_template(url_for('project_details'))

        else:
            flash('Please provide all the fields')
            return redirect(url_for('modify_project', action=action))
    else:
        users = User.query.all()
        return render_template('modify-project.html', action=action, users=users)


# This route is called when the user searches for a project when assigning a project manager for a project
@app.route('/search-project', methods=['POST'])
def search_project():
    json_data = request.data
    print(json_data)
    return jsonify(message="success 204 - No content")


# This route assigns a team member to a project
@app.route('/add-team-member/<project_id>', methods=['POST'])
def add_team_member(project_id):
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        project = Project.query.filter_by(id=project_id).first()
        if project:
            user = User.query.filter_by(username=username).first()
            if user:
                if user in project.team:
                    flash("The user is already in the team")
                    return redirect(url_for('project_dashboard'))
                else:
                    team = Team(project_id=project_id, user_id=user.id, role=role)
                    db.session.add(team)
                    db.session.commit()
                    return redirect(url_for('project_details', project_id=project_id))
            else:
                return render_template('404.html')


# This route changes a project's project manager
@app.route('/change-pm/<project_id>/<user_id>', methods=['GET'])
def change_pm(project_id, user_id):
    project = Project.query.filter_by(id=project_id).first()
    user = User.query.filter_by(id=user_id).first()
    if project and user:
        project.project_manager_id = user.id
        db.session.commit()
        return redirect(url_for('project_details', project_id=project_id))
    else:
        flash("Either the project or the user do not exist")
        return redirect(url_for('project_details', project_id=project_id))


##ADMIN TAB ROUTE
# This route displays a company settings such as their team, projects and tickets
@app.route('/admin')
def admin():
    projects = Project.query.all()
    users = User.query.all()
    tickets = Ticket.query.all()
    return render_template('admin.html', projects=projects, users=users, tickets=tickets)


##PERSONAL INFORMATION ROUTES
# This route displays the current users profile information settings that are displayed when their profile is viewed
@app.route('/personal-info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        fullName = request.form['fullName']
        bio = request.form['bio']
        url = request.form['url']
        location = request.form['location']
        if fullName and bio and url and location:
            current_user.name = fullName
            current_user.bio = bio
            current_user.website_url = url
            current_user.location = location
            db.session.commit()
            return redirect(url_for('personal_info'))
    return render_template('personal-info.html')


## ACCOUNT SETTINGS ROUTE
# This route displays the current users account settings
@app.route('/account-settings', methods=['GET', 'POST'])
def account_settings():
    if request.method == 'POST':
        username = request.form['username']
        if username:
            if not User.query.filter_by(username=username).first():
                current_user.username = username
                db.session.commit()
                return redirect(url_for('account_settings'))
            else:
                flash('This username is already taken.')
                return redirect(url_for('account_settings'))
        else:
            flash('Please enter a username')
            return redirect(url_for('account_settings'))
    return render_template('account-settings.html')


##SECURITY SETTINGS ROUTE
# this route displays the current users Security Settings
@app.route('/security-settings', methods=['GET', 'POST'])
def security_settings():
    if request.method == 'POST':
        old_password = request.form['old-password']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']
        if old_password and new_password and confirm_password:
            if new_password == confirm_password:
                if check_password_hash(current_user.password, old_password):
                    hash_and_salted_password = generate_password_hash(
                        new_password,
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                    current_user.password = hash_and_salted_password
                    db.session.commit()
                    flash('Password successfully updated')
                    redirect(url_for('security_settings'))
                else:
                    flash('Incorrect Old Password.')
                    return redirect(url_for('security_settings'))
            else:
                flash('New Password does not match the confirmed password')
                return redirect(url_for('security_settings'))

        return redirect(url_for('security_settings'))
    return render_template('security-settings.html')


## NOTIFICATIONS SETTINGS
# This route displays the current users notification settings
@app.route('/notification-settings', methods=['GET', 'POST'])
def notification_settings():
    if request.method == 'POST':
        vul_notifications = request.form.get('vul_notifications')
        vul_summary = request.form.get('vul_summary')
        comments = request.form.get('comments')
        people_updates = request.form.get('people-updates')
        reminders = request.form.get('reminders')
        events = request.form.get('events')
        following = request.form.get('following')
        if vul_notifications:
            current_user.vulnerability_notification = True
        else:
            current_user.vulnerability_notification = False

        if vul_summary:
            current_user.vulnerability_summary_notification = True
        else:
            current_user.vulnerability_summary_notification = False

        if comments:
            current_user.comment_notification = True
        else:
            current_user.comment_notification = False

        if people_updates:
            current_user.message_notification = True
        else:
            current_user.message_notification = False

        if reminders:
            current_user.reminders_notification = True
        else:
            current_user.reminders_notification = False

        if events:
            current_user.events_notification = True
        else:
            current_user.events_notification = False

        if following:
            current_user.following_notification = True
        else:
            current_user.following_notification = False
        db.session.commit()
        return redirect(url_for('notification_settings'))
    return render_template('notification-settings.html')


## USER PROFILE VIEW PAGE ROUTE
# This route displays a users profile
@app.route('/view-profile<user_id>', methods=['GET'])
def view_user_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('user-page.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
