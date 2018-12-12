import json, urllib.request, sqlite3, time
from imdb import IMDb
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)
imdb = IMDb()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Main function to update and jsonify once a day
def main():
    update()
    jsonify()
    time.sleep(86400)


# Parsing function
def update():
    SQL = sqlite3.connect('movies.db')
    database = SQL.cursor()
    print("Starting the list update...\n")
    page_counter = 1
    url = "https://www.rottentomatoes.com/api/private/v2.0/browse?" \
          "maxTomato=100&maxPopcorn=100&certified&sortBy=release&type=cf-dvd-streaming-all&page="
    movies = []
    count = 32
    while count >= 32:
        print("Parsing RottenTomatoes, page " + str(page_counter), end='\r')
        response = urllib.request.urlopen(url+str(page_counter))
        results = json.loads(response.read())
        if results["results"]:
            movies.append(results["results"])
        count = int(results["counts"]["count"])
        page_counter += 1
    for i in movies:
        for x in i:
            movie_id = x["id"]
            movie_title = x["title"]
            # Check DB if movie already exists, update only if it does not.
            query = database.execute("SELECT * FROM movies WHERE id = ? AND title = ?", (movie_id, movie_title))
            db_movie = query.fetchall()
            if not db_movie:
                if "url" in x:
                    movie_url = 'https://www.rottentomatoes.com' + x["url"]
                else:
                    movie_url = 'n/a'
                if "tomatoIcon" in x:
                    movie_tomato_icon = x["tomatoIcon"]
                else:
                    movie_tomato_icon = 'blank'
                if "tomatoScore in x":
                    movie_tomato_score = x["tomatoScore"]
                else:
                    movie_tomato_score = '0'
                if "popcornIcon" in x:
                    movie_popcorn_icon = x["popcornIcon"]
                else:
                    movie_popcorn_icon = 'blank'
                if "popcornScore" in x:
                    movie_popcorn_score = x["popcornScore"]
                else:
                    movie_popcorn_score = '0'
                if "theaterReleaseDate" in x:
                    movie_theater_release = x["theaterReleaseDate"]
                else:
                    movie_theater_release = 'n/a'
                if "dvdReleaseDate" in x:
                    movie_physical_release = x["dvdReleaseDate"]
                else:
                    movie_physical_release = 'n/a'
                if "mpaaRating" in x:
                    movie_rating = x["mpaaRating"]
                else:
                    movie_rating = 'n/a'
                if "synopsis" in x:
                    movie_synopsis = x["synopsis"]
                else:
                    movie_synopsis = 'n/a'
                if "runtime" in x:
                    movie_length = x["runtime"]
                else:
                    movie_length = 'n/a'
                if "mainTrailer" in x:
                    movie_trailer = x["mainTrailer"]["sourceId"]
                else:
                    movie_trailer = 'n/a'
                if "posters" in x:
                    movie_poster = x["posters"]["primary"]
                else:
                    movie_poster = 'n/a'
                if "actors" in x:
                    movie_actors = ", ".join(x["actors"])
                else:
                    movie_actors = 'n/a'
                # Checking the movie against iMDB database, populating year and imdb id if exists, skipping if not
                try:
                    search = imdb.search_movie(movie_title)
                    for i in search:
                        if i["year"] <= datetime.now().year and i["title"] == movie_title:
                            year = i["year"]
                            imdb_id = 'tt'+str(i.movieID)
                            break
                except:
                    print("Movie not found on iMDB, skipping..\n")
                    continue
                database.execute("INSERT OR IGNORE INTO movies (id, title, url, tomato_icon, tomato_score, popcorn_icon, popcorn_score, theater_release, physical_release, rating, synopsis, length, trailer, poster, actors, imdb_id, year)" \
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (movie_id, movie_title, movie_url, movie_tomato_icon, \
                    movie_tomato_score, movie_popcorn_icon, movie_popcorn_score, movie_theater_release, movie_physical_release, \
                    movie_rating, movie_synopsis, movie_length, movie_trailer, movie_poster, movie_actors, imdb_id, year))
                print("Adding " + movie_title + " to the list..\n")
            else:
                print(movie_title + " is already on the list, skipping..\n")
    SQL.commit()
    SQL.close()

# Function to build a JSON list out of the DB
def jsonify():
    SQL = sqlite3.connect('movies.db')
    database = SQL.cursor()
    data = []
    query = database.execute("SELECT * FROM movies")
    movies = query.fetchall()
    for i in movies:
        movie = {}
        movie["title"] = i[1]
        movie["imdb_id"] = i[15]
        movie["poster_url"] = i[13]
        data.append(movie.copy())
    movies_json = json.dumps(data)
    file = open("./static/movies.json", "w")
    file.write(movies_json)
    file.close()
    SQL.close()

@app.route("/", methods=["GET", "POST"])
def index():
    SQL = sqlite3.connect('movies.db')
    database = SQL.cursor()
    query = database.execute("SELECT * FROM movies ORDER BY year DESC, theater_release DESC")
    if request.method == "POST":
        sort_by = request.form.get("sort_by")
        if sort_by == "title":
            query = database.execute("SELECT * FROM movies ORDER BY title")
        elif sort_by == "year":
            query = database.execute("SELECT * FROM movies ORDER BY year DESC, theater_release DESC")
        elif sort_by == "tomato_score":
            query = database.execute("SELECT * FROM movies ORDER BY tomato_score DESC")
        elif sort_by == "popcorn_score":
            query = database.execute("SELECT * FROM movies ORDER BY popcorn_score DESC")
    movies = query.fetchall()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter = 'per_page')
    pagination_movies = movies[offset: offset + 10]
    pagination = Pagination(page = page, per_page = per_page, total = len(movies), css_framework='bootstrap4')
    SQL.close()
    return render_template("index.html", movies=pagination_movies, page=page, per_page=per_page, pagination=pagination)


if __name__ == '__main__':
    main()