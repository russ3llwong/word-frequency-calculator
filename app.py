import os
import requests
import operator
import re
import nltk
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

q = Queue(connection=conn)  # setup redis connection and initialize Queue

from models import *

# function to process input and save to db
def count_and_save_words(url):

    errors = []

    try:
        r = requests.get(url)
    except Exception as e:
        errors.append("Unable to get info from URL. Please make sure URL is valid.")
        errors.append("Error:")
        errors.append(e)
        return render_template('index.html', errors=errors)

    # text processing
    if r:
        raw = BeautifulSoup(r.text, "html.parser").get_text()
        nltk.data.path.append('./nltk_data/') # access to nltk resources in case nltk not installed
        tokens = nltk.word_tokenize(raw)
        text = nltk.Text(tokens)

        # remove punctuation and count raw words
        nonPunct = re.compile('.*[A-Za-z].*')
        raw_words = [w for w in text if nonPunct.match(w)]
        raw_word_count = Counter(raw_words)

        # stop words
        no_stop_words = [w for w in raw_words if w.lower() not in stops]
        no_stop_words_count = Counter(no_stop_words)

        # save the results
        try:
            result = Result(
                url=url,
                result_all=raw_word_count,
                result_no_stop_words=no_stop_words_count
            )
            db.session.add(result)
            db.session.commit()
            print("DB saved")
            return result.id
        except:
            errors.append("Unable to add item to database.")
            return {"errors": errors}

# home page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

# process input
@app.route('/start', methods=['POST'])
def get_counts():

    # process url
    data = json.loads(request.data.decode())
    url = data["url"]
    if not url[:8].startswith(('https://', 'http://')):
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    return job.get_id()

# for angular to check on job
@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:10]
        return jsonify(results)
    else:
        return "Still counting words.", 202

if __name__ == '__main__':
    app.run()
