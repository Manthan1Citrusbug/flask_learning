from flask import Flask, render_template, request, session, redirect
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import json

# include config file and de jasonify it 
with open('config.json','r') as config_file:
    config_data = json.load(config_file)

# create app
app = Flask(__name__)
app.config['SECRET_KEY'] = "login_secret_key"
# Configure Mail 
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = config_data['email_data']['sender_email'],
    MAIL_PASSWORD = config_data['email_data']['sender_pass']
)
mail = Mail(app)

# Configure the database
if config_data['params']['local_server']: # check app is run on local server or other server
    app.config['SQLALCHEMY_DATABASE_URI'] = config_data['params']['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = config_data['params']['prod_uri']
db = SQLAlchemy(app)

'''
NOTE: DATABASE IS CREATED IN LOCALHOST://PHPMYADMIN 
BEFORE THIS MODEL CREATED THIS MODEL IS USED TO SEND DATA TO DATABASE. 
'''
# create Contacts Class for database 
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(20), nullable = False)
    phone_no = db.Column(db.String(12), nullable = False)
    msg = db.Column(db.String(120), nullable = False)
    date = db.Column(db.String(12), nullable = False)

# create Post Class for database 
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    subtitle = db.Column(db.String(80), nullable = False)
    slug = db.Column(db.String(50), nullable = False)
    content = db.Column(db.String(120), nullable = False)
    date = db.Column(db.String(12), nullable = False)
    created_by = db.Column(db.Integer, nullable = False)


# create User Class for database 
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(30), nullable = False)

# Index Function for rendering index.html page
@app.route('/')
def index():
    posts_data = Posts.query.filter_by().all()[0:config_data['template_data']['no_of_posts']]
    return render_template('index.html', custom_data = config_data['template_data'],posts_data = posts_data)


# About Function for rendering about.html page
@app.route('/about')
def about():
    return render_template('about.html', custom_data = config_data['template_data'])


# Contact function for redering contact.html page
@app.route('/contact', methods=['GET','POST']) # default request is get request
def contact():
    # Check request is post or not
    if request.method == 'POST':

        # get all form data in variable
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone').replace("-",'')
        message = request.form.get('message')

        # create an object of Contact Model
        contactData = Contacts(name=name, email = email, phone_no = phone, date = datetime.now(), msg = message)

        # save data into the database
        db.session.add(contactData)
        db.session.commit()

        # Send Mail
        msg = Message(name+"is contacted you", sender=email, recipients=[config_data['email_data']['sender_email']])
        msg.body = "Hello,\n\tHope you're doing great. we want to know you that '{name}' is trying to reach you, Please reply to Him/Her.\nThank You."
        mail.send(msg)
                

    # Outside POST requset (default request is get request)
    return render_template('contact.html', custom_data = config_data['template_data'])

# post function for redering post.html page
@app.route('/post/<string:post_slug>',methods=['GET'])
def post(post_slug):
    post_data = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html', custom_data = config_data['template_data'],post_data=post_data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/dashboard")




# ADMIN PANEL
@app.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    if request.method == 'POST':
        if 'is_login' not in session:
            usermail = request.form.get('email')
            userpass = request.form.get('password')
            try:
                userValue = User.query.filter_by(email = usermail, password = userpass).first()
                session['is_login'] = True
                session['login_data'] = userValue.id
            except:
                return render_template('login.html', custom_data = config_data['template_data'], error = "Data Invalid")

    if 'is_login' in session:
        posts_data = Posts.query.filter_by(created_by = session['login_data']).all()
        return render_template('dashboard.html', custom_data = config_data['template_data'], posts_data = posts_data, login = session['login_data'])
    return render_template('login.html', custom_data = config_data['template_data'])

# edit function for redering edit.html page and edit post data

@app.route('/add', methods=['GET','POST'])
def add():
    if 'is_login' in session:
        if request.method == 'POST':
            title = request.form.get('name')
            subtitle = request.form.get('subtitle')
            content = request.form.get('content')
            slug = title.lower()
            slug = slug.replace(' ',"-")

            try:
                post_data = Posts(title=title, subtitle = subtitle, slug = slug, content = content, date = datetime.now(), created_by = session['login_data'])
                db.session.add(post_data)
                db.session.commit()
            except IntegrityError:
                return render_template('add.html', custom_data = config_data['template_data'],error = "This Heading is already available")
            # save data into the database
            return redirect('/dashboard')

        return render_template('add.html', custom_data = config_data['template_data'])
    else:
        return redirect('/dashboard')


@app.route('/edit/<string:post_slug>', methods=['GET','POST'])
def edit(post_slug):
    if 'is_login' in session:
        if request.method == 'POST':
            title = request.form.get('name')
            subtitle = request.form.get('subtitle')
            content = request.form.get('content')
            edit_slug = title.lower()
            edit_slug = edit_slug.replace(' ',"-")
            try:
                post_data = Posts.query.filter_by(slug = post_slug).first()
                post_data.title = title
                post_data.subtitle = subtitle
                post_data.content = content
                post_data.slug = edit_slug
                db.session.commit()
            except (PendingRollbackError, IntegrityError):
                db.session.rollback()
                post_data = Posts.query.filter_by(slug = post_slug).first()
                return render_template('edit.html', custom_data = config_data['template_data'], post=post_data, error = "This Heading is already available")
            return redirect('/dashboard')

        post_data = Posts.query.filter_by(slug = post_slug).first()
        return render_template('edit.html', custom_data = config_data['template_data'],post=post_data)
    else:
        return redirect('/dashboard')

# edit function for redering edit.html page and edit post data
@app.route('/delete/<string:post_slug>', methods=['GET','POST'])
def delete(post_slug):
    if 'is_login' in session:
        post_data = Posts.query.filter_by(slug = post_slug).first()
        db.session.delete(post_data)
        db.session.commit()
    return redirect('/dashboard')

# for run app
app.run(debug=True)