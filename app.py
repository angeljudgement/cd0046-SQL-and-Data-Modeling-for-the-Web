# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, timezone

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO_DONE: connect to a local postgresql database


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, unique=False, default=False)
    seeking_description = db.Column(db.Text)
    shows = db.relationship("Show", backref="Venue")
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)

    # TODO_DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    musicGenres = db.Column(ARRAY(db.String(100)))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, unique=False, default=False)
    seeking_description = db.Column(db.Text)
    shows = db.relationship("Show", backref="Artist")
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    start_time = db.Column(db.String(100))

    # TODO_DONE: implement any missing fields, as a database migration using Flask-Migrate


# TODO_DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


def newerThan(show):
    now = datetime.now()
    then = datetime.fromisoformat(show.start_time)

    return now < then


def olderThan(show):
    now = datetime.now()
    then = datetime.fromisoformat(show.start_time)

    return now > then


def count_matching(condition, seq):
    """Returns the amount of items in seq that return true from condition"""
    if seq.__len__() > 0:
        return sum(1 for item in seq if condition(item))


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():

    def mappingVenues(venue):
        mappedVenue = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": (
                venue.num_upcoming_shows if hasattr(venue, "num_upcoming_shows") else 0
            ),
        }
        mappedVenue = {
            **mappedVenue,
            "num_upcoming_shows": count_matching(newerThan, venue.shows),
        }

        return mappedVenue

    def mappingArea(area):
        print(area)
        value = {
            "city": list(area)[0].city,
            "state": list(area)[0].state,
            "venues": list(map(mappingVenues, area)),
        }

        return value

    def mappingCityState(venue):
        return venue.city + venue.state

    venues = Venue.query.all()
    areas = []
    cityState = list(set(map(mappingCityState, venues)))
    groupedCityState = []

    for state in cityState:
        tempGroupedCityState = []
        for venue in venues:
            compareCityState = venue.city + venue.state
            if state == compareCityState:
                tempGroupedCityState.append(venue)
        groupedCityState.append(tempGroupedCityState)

    areas = map(mappingArea, groupedCityState)

    return render_template("pages/venues.html", areas=areas)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO_DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    class VenueSearch:
      def __init__(self, count, data):
          self.id = count
          self.data = data
    class VenueSearchData:
      def __init__(self, id, name, num_upcoming_shows):
          self.id = id
          self.name = name
          self.num_upcoming_shows = num_upcoming_shows
    def mapSearchVenue(venue):
      return VenueSearchData(venue.id, venue.name, count_matching(newerThan, venue.shows))
      
    searchTerm = request.form.get("search_term", "")
    venues = Venue.query.filter(func.lower(Venue.name).icontains(func.lower(searchTerm))).all()
    response = VenueSearch(venues.__len__, list(map(mapSearchVenue, venues)))

    return render_template(
        "pages/search_venues.html", results=response, search_term=searchTerm
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO_DONE: replace with real venue data from the venues table, using venue_id
    class VenueShow:
        def __init__(self, id, artist_id, artist_name, artist_image_link, start_time):
            self.id = id
            self.artist_id = artist_id
            self.artist_name = artist_name
            self.artist_image_link = artist_image_link
            self.start_time = start_time

    def mapShows(show):
        artist = Artist.query.get(show.artist_id)
        return VenueShow(
            show.id, artist.id, artist.name, artist.image_link, show.start_time
        )

    def filterShowsOlder(show):
        if olderThan(show):
            return True
        else:
            return False

    def filterShowsNewer(show):
        if newerThan(show):
            return True
        else:
            return False

    data = Venue.query.get(venue_id)
    show = list(map(mapShows, data.shows))
    pastShow = list(filter(filterShowsOlder, show))
    upcomingShow = list(filter(filterShowsNewer, show))
    data = {
        **data.__dict__,
        "past_shows_count": pastShow.__len__(),
        "upcoming_shows_count": upcomingShow.__len__(),
        "past_shows": pastShow,
        "upcoming_shows": upcomingShow,
    }

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO_DONE: insert form data as a new Venue record in the db, instead
    # TODO_DONE: modify data to be the data object returned from db insertion

    error = False
    form_data = request.form.to_dict()
    try:
        if "seeking_talent" in form_data.keys():
            form_data["seeking_talent"] = (
                True if form_data["seeking_talent"] == "y" else False
            )
        form_data["genres"] = request.form.getlist("genres")
        venue = Venue(**form_data)
        db.session.add(venue)
        db.session.commit()
        db.session.refresh(venue)
    except:
        error = True
        db.session.rollback()
        flash("An error occurred. Venue " + form_data["name"] + " could not be listed.")
    finally:
        db.session.close()
    if not error:
        flash("Venue " + form_data["name"] + " was successfully listed!")
    else:
        abort(500)

    # on successful db insert, flash success

    # TODO_DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # TODO_DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("venues"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO_DONE: replace with real data returned from querying the database
    def mapArtist(artist):
        return {"id": artist.id, "name": artist.name}

    artists = Artist.query.all()
    data = map(mapArtist, artists)
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO_DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    class ArtistSearch:
      def __init__(self, count, data):
          self.id = count
          self.data = data
    class ArtistSearchData:
      def __init__(self, id, name, num_upcoming_shows):
          self.id = id
          self.name = name
          self.num_upcoming_shows = num_upcoming_shows
    def mapSearchVenue(venue):
      return ArtistSearchData(venue.id, venue.name, count_matching(newerThan, venue.shows))
      
    searchTerm = request.form.get("search_term", "")
    artists = Artist.query.filter(func.lower(Artist.name).icontains(func.lower(searchTerm))).all()
    response = ArtistSearch(artists.__len__, list(map(mapSearchVenue, artists)))
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO_DONE: replace with real artist data from the artist table, using artist_id
    class ArtistShow:
        def __init__(self, id, venue_id, venue_name, venue_image_link, start_time):
            self.id = id
            self.venue_id = venue_id
            self.venue_name = venue_name
            self.venue_image_link = venue_image_link
            self.start_time = start_time

    def mapShows(show):
        venue = Venue.query.get(show.venue_id)
        return ArtistShow(
            show.id, venue.id, venue.name, venue.image_link, show.start_time
        )

    def filterShowsOlder(show):
        if olderThan(show):
            return True
        else:
            return False

    def filterShowsNewer(show):
        if newerThan(show):
            return True
        else:
            return False

    data = Artist.query.get(artist_id)
    show = list(map(mapShows, data.shows))
    pastShow = list(filter(filterShowsOlder, show))
    upcomingShow = list(filter(filterShowsNewer, show))
    data = {
        **data.__dict__,
        "past_shows_count": pastShow.__len__(),
        "upcoming_shows_count": upcomingShow.__len__(),
        "past_shows": pastShow,
        "upcoming_shows": upcomingShow,
    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(**artist.__dict__)
    # TODO_DONE: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO_DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form_data = request.form.to_dict()
    artist = Artist.query.get(artist_id)
    try:
        if "seeking_venue" in form_data.keys():
            form_data["seeking_venue"] = (
                True if form_data["seeking_venue"] == "y" else False
            )
        else:
            form_data = {**form_data, "seeking_venue": False}
        form_data["musicGenres"] = request.form.getlist("musicGenres")
        form = ArtistForm(**form_data)
        form.populate_obj(artist)
        db.session.commit()
        db.session.refresh(artist)
    except:
        error = True
        db.session.rollback()
        flash("An error occurred. Venue " + form_data["name"] + " could not be listed.")
    finally:
        db.session.close()
    if error:
        abort(500)
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(**venue.__dict__)
    # TODO_DONE: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO_DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    form_data = request.form.to_dict()
    venue = Venue.query.get(venue_id)
    try:
        if "seeking_talent" in form_data.keys():
            form_data["seeking_talent"] = (
                True if form_data["seeking_talent"] == "y" else False
            )
        else:
            form_data = {**form_data, "seeking_talent": False}
        form_data["genres"] = request.form.getlist("genres")
        form = VenueForm(**form_data)
        form.populate_obj(venue)
        db.session.commit()
        db.session.refresh(venue)
    except:
        error = True
        db.session.rollback()
        flash("An error occurred. Venue " + form_data["name"] + " could not be listed.")
    finally:
        db.session.close()
    if error:
        abort(500)
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO_DONE: insert form data as a new Venue record in the db, instead
    # TODO_DONE: modify data to be the data object returned from db insertion
    error = False
    form_data = request.form.to_dict()
    try:
        if "seeking_venue" in form_data.keys():
            form_data["seeking_venue"] = (
                True if form_data["seeking_venue"] == "y" else False
            )
        form_data["musicGenres"] = request.form.getlist("musicGenres")
        artist = Artist(**form_data)
        db.session.add(artist)
        db.session.commit()
        db.session.refresh(artist)
    except:
        error = True
        db.session.rollback()
        flash(
            "An error occurred. Artist " + form_data["name"] + " could not be listed."
        )
    finally:
        db.session.close()
    if not error:
        flash("Artist " + form_data["name"] + " was successfully listed!")
    else:
        abort(500)
    # on successful db insert, flash success
    # TODO_DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO_DONE: replace with real venues data.
    def mappingShow(show):
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        return {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time,
        }

    shows = Show.query.all()
    data = map(mappingShow, shows)
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO_DONE: insert form data as a new Show record in the db, instead

    error = False
    form_data = request.form.to_dict()
    try:
        show = Show(**form_data)
        db.session.add(show)
        db.session.commit()
        db.session.refresh(show)
    except Exception as e:
        print(e)
        error = True
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
    finally:
        db.session.close()
    if not error:
        flash("Show was successfully listed!")
    else:
        abort(500)

    # on successful db insert, flash success

    # TODO_DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
