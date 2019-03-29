"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self): 
        """ Provide helpful representation when printed """

        return f"<User user_id = {self.user_id} email = {self.email}>"

    def similarity(self, user2):
        """compares user2's ratings to instance's ratings"""

        self_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            self_ratings[r.movie_id] = r

        for u2_rating in user2.ratings:
            self_rating = self_ratings.get(u2_rating.movie_id)
            if self_rating:
                pair = (self_rating.score, u2_rating.score)
                paired_ratings.append(pair)

        if paired_ratings:
            return pearson(paired_ratings)
        else:
            return 0.0

    def predict_ratings(self, movie):
        """Predicts what user will rate movie based on similar users' ratings"""
        other_ratings = movie.ratings

        other_users = [r.user for r in movie.ratings]

        users_similarity = []

        for o_user in other_users:
            o_user_similarity = self.similarity(o_user)
            similarity_pair = (o_user_similarity, o_user)
            users_similarity.append(similarity_pair)

        #sorts list of user similarities by most to least similar
        sorted_similariry = sorted(users_similarity, key=lambda users_similarity: users_similarity[0], reverse=True)
        most_similar_user = sorted_similariry[0]

        most_similar_user_rating = 0

        for r in most_similar_user[1].ratings:
            if r.movie_id == movie.movie_id:
                most_similar_user_rating = r.score

        predict_rating = most_similar_user_rating * most_similar_user[0]
        return predict_rating



# Put your Movie and Rating model classes here.

# Movie model
class Movie(db.Model): 
    """Movies for ratings on the website """

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable =False)
    release_at = db.Column(db.DateTime, nullable = False)
    imdb_url = db.Column(db.String(200), nullable = False)


#Ratings Model
class Rating(db.Model):
    """Ratings database"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    #Define relationship to user
    user = db.relationship("User",
                            backref=db.backref("ratings",
                                                order_by=rating_id))
    #Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings",
                                                order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Rating rating_id={self.rating_id}
                   movie_id={self.movie_id}
                   user_id={self.user_id}
                   score={self.score}>"""



def similarity(user1, user2):
    user1_ratings_dict = {}
    paired_ratings = []

    for r in user1.ratings:
        user1_ratings_dict[r.movie_id] = r

    for u2_rating in user2.ratings:
        u1_rating = user1_ratings_dict.get(u2_rating.movie_id)
        if u1_rating:
            pair = (u1_rating.score, u2_rating.score)
            paired_ratings.append(pair)

    if paired_ratings:
        return pearson(paired_ratings)
    else:
        return 0.0

def predict_ratings(user, movie):
    """Predicts what user will rate movie based on similar users' ratings"""
    other_ratings = movie.ratings

    other_users = [r.user for r in movie.ratings]

    users_similarity = []

    for o_user in other_users:
        o_user_similarity = user.similarity(o_user)
        similarity_pair = (o_user_similarity, o_user)
        users_similarity.append(similarity_pair)

    #sorts list of user similarities by most to least similar
    sorted_similariry = sorted(users_similarity, key=lambda users_similarity: users_similarity[0], reverse=True)
    most_similar_user = sorted_similariry[0]

    most_similar_user_rating = 0

    for r in most_similar_user[1].ratings:
        if r.movie_id == movie.movie_id:
            most_similar_user_rating = r.score

    predict_rating = most_similar_user_rating * most_similar_user[0]
    return predict_rating



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")

