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
    """Logs user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    #gets user with specified email
    user = User.query.filter_by(email=email).first()

    #checks email exists and password is correct
    if user is not None and user.password == password and 'user_id' not in session.keys():
        session['user_id'] = user.user_id
        flash("Logged in")
        session.modified = True
        return redirect('/users/' + str(user.user_id))
    else:
        flash("Log in unsucessful")
        return redirect('/')


@app.route('/logout')
def logout():
    print(session)

    if 'user_id' in session: 
        session.pop('user_id')
        flash("Logged out")
        print(session)

    return redirect('/')


@app.route('/users/<user_id>')
def user_details(user_id): 
    """ Get the details of user by user id"""

    user = User.query.filter_by(user_id=user_id).one()
    user_ratings = Rating.query.filter_by(user_id=user_id).options(
        db.joinedload('movie')).all()
    
    # for user_rating in user_ratings: 
    #     print(user_rating.movie.title)


    return render_template('user_details.html', user=user, 
                            ratings=user_ratings)


@app.route('/movies')
def movie_list():
    """Show list of users."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def movie_details(movie_id):
    """ Get the details of movie by movie id"""

    movie = Movie.query.filter_by(movie_id = movie_id).one()
    movie_ratings = Rating.query.filter_by(movie_id = movie_id).all()
    scores = [str(rating.score) for rating in movie_ratings]
    scores_str = ', '.join(scores)

    return render_template('movie_details.html', movie = movie, ratings=movie_ratings, scores=scores_str)


@app.route('/movies/<movie_id>', methods = ['POST']) 
def rate_movie(movie_id):
    """ Store user's movie rating"""

    if is_logged_in():
        rating = int(request.form.get("rating"))
        previous_rating = Rating.query.filter( (Rating.user_id==session['user_id']) & (Rating.movie_id==movie_id)).first()
        if previous_rating: 
            #as previous ratings exists, update it
            previous_rating.score = rating
        
        else: 
            #as previous ratings does not exists, add a new record
            new_rating = Rating(user_id=session['user_id'],movie_id=movie_id,score=rating)
            db.session.add(new_rating)
        
        db.session.commit()
        flash("Rating updated")
        return redirect('/movies/' + movie_id)

    else: 
        flash("Please log in to rate this movie")
        return redirect('/login')
        
    


def is_logged_in():
    """True is a user is logged in"""
    return 'user_id' in session
    




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