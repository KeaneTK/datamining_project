from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, update

from core.database.models.movie import Base, Movie

class DatabaseServices(object):
    """ Methods to ease interfacing with ORM """

    def __init__(self, db_file_name):
        self.filename = db_file_name
        self.engine = None
        self.session = None

    def init_engine(self):
        """ Create the database engine."""

        # TODO: if db already exists, prompt to ask if it should be overwritten
        # appended, etc..
        self.engine = create_engine(
            'sqlite:///{0}.db'.format(self.filename)
            , echo=False)

        Base.metadata.create_all(self.engine)

    def get_session(self):
        """ Get a session for the database """

        if self.engine is None:
            self.init_engine()

        session = sessionmaker(bind=self.engine)

        self.session = session()

    def add_movie_review(self, byline, display_title, release_date, critics_pick,
                         mpaa_rating, link_url, link_type):
        """ Adds a movie review object to the db session and commits.
        If session doesn't exist, it will be created
        """

        if self.session is None:
            self.get_session()

        new_movie = Movie(
            byline=byline,
            display_title=display_title,
            release_date=release_date,
            critics_pick=critics_pick,
            mpaa_rating=mpaa_rating,
            link_url=link_url,
            link_type=link_type)

        try:
            self.session.add(new_movie)
            self.session.commit()
        except (IntegrityError, UnicodeEncodeError) as exc:
            print exc
            print '\n\n'
            print 'There was an error adding a movie to the db.'
            print 'Movie title is likely a duplicate; rolling back and moving on...'
            self.session.rollback()

    def get_review_by_title(self, movie_title):
        """ Gets a movie review by the title of the movie

        Returns the first item in the DB matching that title
        """

        if self.session is None:
            self.get_session()

        return self.session.query(Movie).filter_by(display_title=movie_title).first()

    def get_review_by_id(self, movie_id):
        """ Gets a movie review by the title of the movie

        Returns the first item in the DB matching that title
        """

        if self.session is None:
            self.get_session()

        return self.session.query(Movie).filter_by(movie_id=movie_id).first()

    def get_num_movies(self):
        """ Fetches the number of movie reviews stored in DB """
        if self.session is None:
            self.get_session()

        return self.session.query(func.count(Movie.movie_id)).scalar()

    def get_all_movie_ids(self):
        """ Fetches all movie_ids from the DB """
        if self.session is None:
            self.get_session()

        return self.session.query(Movie).options(load_only("movie_id"))

    def add_review_full_text(self, movie_id, full_text):
        ''' Updates the DB entry with the full review text '''
        if self.session is None:
            self.get_session()

        movie = self.get_review_by_id(movie_id)
        movie.full_review = full_text
        self.session.commit()

    def add_box_office_gross(self, movie_id, box_office_gross):
        ''' Adds the box office gross as a string to the DB '''
        if self.session is None:
            self.get_session()

        movie = self.get_review_by_id(movie_id)
        movie.box_office_earnings = box_office_gross
        self.session.commit()

    def add_item_csv(self, movie_id, item_csv):
        ''' Adds a csv containing the review words to the DB '''
        if self.session is None:
            self.get_session()

        movie = self.get_review_by_id(movie_id)
        movie.itemset = item_csv
        self.session.commit()
        