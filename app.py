import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
#print(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}

    if request.method == "POST":

        # get the url from user input
        try:
            url = request.form['url']
            # in case http:// or https:// is not included in input
            urlString = str(url)
            if urlString[:4] != "http":
                url = "http://" + url
            r = requests.get(url)
            #print(r.text)

        except Exception as e:
            errors.append("Unable to get info from URL. Please make sure URL is valid.")
            errors.append("Error:")
            errors.append(e)
            return render_template('index.html', errors=errors)

        # text processing
        if r:
            raw = BeautifulSoup(r.text, "html.parser").get_text()
            #print(raw)
            nltk.data.path.append('./nltk_data/')
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
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )
            print("R E S U L T S")
            print(results[:10])
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
           
    return render_template('index.html', errors=errors, results=results)

if __name__ == '__main__':
    app.run()