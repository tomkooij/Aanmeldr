# -*- coding: utf-8 -*-
"""
    Aanmeldr
    ~~~~~~

    Coornhert kerstworkshop aanmeldwebsite (Based on Flaskr)


"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

# mijn eigen check_login
from read_db import check_login
import hashlib, os, binascii # crypto voor wachtwoorden

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'QQdw1maM2dJRkkYOFnn3DnnBFho='

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def check_login(username, wachtwoord):

  # maak van usernaam een int()
  if username.isdigit():
    leerlingnummer = int(username)
  else:
    return False, username+' is geen leerlingnummer'

  user = query_db('select * from users where id = ?',
                [username], one=True)
  if user is None:
    return False, 'Leerlingnummer %s onbekend' % leerlingnummer
  else:
    db_salt = user['salt']
    db_hash = user['wachtwoord']
    m = hashlib.md5()
    m.update(db_salt+wachtwoord)
    mijn_hash = m.hexdigest()

    if (mijn_hash==db_hash):
      return True, "Login gelukt!"

  return False, "Login mislukt!"

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':


    # check login/pass in database
    login_username = request.form['username']
    login_password = request.form['password']
    result, error = check_login(login_username, login_password)

    if result:
      # store in session cookie (crypto)
      session['logged_in'] = True
      session['username'] = request.form['username']
      flash('Je bent ingelogd')
      return redirect(url_for('show_entries'))

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Je bent uitgelogd!')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
