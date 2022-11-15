from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# Index Function for rendering index.html page
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# About Function for rendering about.html page
@bp.route('/about')
def about():
    return render_template('blog/about.html')


# Contact function for redering contact.html page
@bp.route('/contact', methods=['GET','POST']) # default request is get request
def contact():
    # Check request is post or not
    if request.method == 'POST':
        pass
                

    # Outside POST requset (default request is get request)
    return render_template('blog/contact.html')

# post function for redering post.html page
@bp.route('/<int:id>/post',methods=['GET'])
def post(id):
    db = get_db()
    post = db.execute( 'SELECT * FROM post WHERE id = ?',(id,) ).fetchone()
    return render_template('blog/post.html',post=post)