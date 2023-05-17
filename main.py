from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import requests
import os

load_dotenv()

movies_url= "https://api.themoviedb.org/3/search/movie"
movie_url = "https://api.themoviedb.org/3/movie"


db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
db.init_app(app)
Bootstrap5(app)

class EditForm(FlaskForm):
    rating = DecimalField('Your Rating out of 10', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Search')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars()
    all_movies = movies.all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies = all_movies)

@app.route('/edit', methods=["GET", "POST"])
def edit():
    edit_form = EditForm()
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    if edit_form.validate_on_submit():
        movie.rating = edit_form.rating.data
        movie.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=edit_form, movie=movie)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        response = requests.get(movies_url, params={"api_key": os.getenv("API_KEY"), "query":form.title.data})
        data = response.json()["results"]
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)

@app.route('/find')
def find():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f"{movie_url}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": os.getenv("API_KEY"), "language": 'en-US'})
        data = response.json()
        print(data['poster_path'])
        new_movie = Movie(
            title=data['title'],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True, port=9000)

#finished
