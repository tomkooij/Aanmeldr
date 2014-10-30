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
SECRET_KEY = 'This should be changed in a production enviroment'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



workshops = ( (0,"Geen keuze",750),
              (1,"Film", 200),
              (2,"Sporten in de Mammoet", 100),
              (3,"Dansem", 20),
              (4,"Kerstkaarten maken", 20),
              (5,"Robots bouwen", 10),
              (6,"Geen keuze",750),
              (7,"Filmssssssss", 200),
              (8,"Sporten ergens anders", 100),
              (9,"Nog meer Dansen", 20),
              (10,"Kerstkaarten maken", 20),
              (15,"Robots bouwen", 10))


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
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()

    return render_template('show_entries.html', workshops=workshops)



@app.route('/kies_workshop', methods=['POST'])
def kies_workshop():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
# let op request.form['kueze'] = UNICODE check in html en vang af

    # maak een int van de keuze die in unicode binnenkomt
    # vang onbekende keuzes af
    tmp_keuze = request.form['keuze']
    if str(tmp_keuze).isdigit:
      keuze = int(tmp_keuze)
    else:
      keuze = 0

    db.execute("UPDATE users set keuze = ? where id = ? ",
                 [keuze, session['username']])
    db.commit()
    session.keuze = keuze  # update cookie
    message = 'Je hebt nu gekozen voor: '+str(workshops[keuze][1])
    flash(message)


#    return render_template('show_entries.html', workshops=workshops)
    return redirect(url_for('show_entries'))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':

    # check login/pass in database
    login_username = request.form['username']
    login_password = request.form['password']

    # maak van usernaam een int()
    if not login_username.isdigit():
      error = login_username+' is geen leerlingnummer'
    else:
      leerlingnummer = int(login_username)

      # Haal userrecord uit databae

      user = query_db('select * from users where id = ?',
                    [leerlingnummer], one=True)

      if user is None:
        error = ('Leerlingnummer %s onbekend' % leerlingnummer)
      else:
        db_salt = user['salt']
        db_hash = user['wachtwoord']
        m = hashlib.md5()
        m.update(db_salt+login_password)
        mijn_hash = m.hexdigest()

        if (mijn_hash==db_hash):
          error = "Login gelukt!"

          # store in session cookie (crypto)
          session['logged_in'] = True
          session['username'] = leerlingnummer
          session['naam'] = user['naam']
          session['keuze'] = user['keuze']
          flash('Welkom %s. Je bent ingelogd.' % user['naam'])
          return redirect(url_for('show_entries'))
        else:
          error = "Login mislukt!"

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Je bent uitgelogd!')
#    return redirect(url_for('show_entries'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
