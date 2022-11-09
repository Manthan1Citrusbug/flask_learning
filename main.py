from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# include config file and de jasonify it 
with open('config.json','r') as config_file:
    config_data = json.load(config_file)

# create app
app = Flask(__name__)

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

# post function for redering post.html page
@app.route('/post/',methods=['GET'])
def semple_post():
    post_data = Posts.query.all()[0]
    return render_template('post.html', custom_data = config_data['template_data'],post_data=post_data)
# for run app
app.run(debug=True)