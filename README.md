# Word Frequency Calculator

Flask web app that calculates the word-frequency pairs of a given URL. **Redis** is used for the task queue, while **Angular** is used for the client-side polling.

**Staging**: http://www.wordfreqcalc-stage.herokuapp.com

**Production**: http://www.wordfreqcalc-prod.herokuapp.com

<img src="http://g.recordit.co/1Mf6nS9YDr.gif"/>

## Setup

### Installations
```shell
$ pyvenv-3.5 env
$ source .env
$ pip install -r requirements.txt 
```
### Database Migration
```shell
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```
### Run
Run these in 3 different terminal windows.
```shell
$ redis server

$ python worker.py

$ python app.py
```

## References

- When ```source .env``` is executed in terminal, the commands in the .env file will be executed. This will save you time, not needing to activate the isolated environment and export env variables.
- The **heroku.sh** file (called by **Procfile**) allows Heroku to run 2 processes in the same dyno. (Not recommended for actual production applications)

