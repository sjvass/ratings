"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                    session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=['GET'])
def register_form():
    """user registration form"""
    return render_template("register_form.html")

@app.route('/register', methods=['POST'])
def register_process():
    """Adds new user"""

    email = request.form.get("email")
    password = request.form.get("password")

    #check if user already exists
    if User.query.filter_by(email=email).all():
        #if a user with that email is found, show message
        flash("A user with that email already exists!")
        print("A user with that email already exists")
    else:
        #if no user with that email exists, create new user
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registration complete!")

    return redirect('/')

@app.route('/login', methods=['GET'])
def login_form():
    """User login form"""

    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def user_login():
    """Loggs user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    #gets user with specified email
    user = User.query.filter_by(email=email).first()

    #checks email exists and password is correct
    if user is not None and user.password == password:
        session['user_id'] = user.user_id
        flash("Logged in")
        session.modified = True
    else:
        flash("Log in unsucessful")

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be5000 True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
5000