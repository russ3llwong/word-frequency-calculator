from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON) # count of the list of words
    result_no_stop_words = db.Column(JSON) # count of the list of words without stop words

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    # to represent the object when we query for it
    def __repr__(self):
        return '<id {}>'.format(self.id)