# -*- coding: utf-8 -*-
"""
    Aanmeldr
    ~~~~~~~~

    Coornhert kerstworkshop aanmeldwebsite
    (Based on Flaskr, a Flask example. See README for license)

"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack


import hashlib, os, binascii # crypto voor wachtwoorden

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'This should be changed in a production enviroment'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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


@app.route('/', methods=['GET'])
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':

      db = get_db()
      cur = db.execute('select * from workshops')
      workshops = cur.fetchall()
      if not session.get('logged_in'):
        return redirect(url_for('login'))

      return render_template('show_entries.html', workshops=workshops)

@app.route('/kies_workshop', methods=['POST'])
def kies_workshop():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from workshops')
    workshops = cur.fetchall()

    # maak een int van de keuze die in unicode binnenkomt
    # vang onbekende keuzes af
    tmp_keuze = request.form['keuze']
    if str(tmp_keuze).isdigit:
      keuze = int(tmp_keuze)
    else:
      keuze = 0

    # als op de een of andere manier de worshop ID groter is dan het aantal
    if (keuze > (len(workshops)-1)):
      flash('OEPS! Er is iets fout gegaan. Je bent waarschijnlijk niet meer ingeschreven.')
      keuze = 0

    # zijn er nog plaatsen? Het kan best zijn dat de workshop inmiddels vol is
    # kies_workshop POST kan 2 dagen na de laaste GET van show_entries zijn
    if (workshops[keuze][2] < 1):
      flash('Sorry! Workshop is niet meer beschikbaar')
      return redirect(url_for('show_entries'))
    elif (keuze == session['keuze']):
      # keuze hetzelfde is als huidige kueze
      flash('Je bent al ingeschreven voor deze workshop!')
      return redirect(url_for('show_entries'))
    else:
#      flash('DEBUG: Attempting to write the workshop database')

      # schrijf eerst de workshop database
      # uitschrijven huidige keuze (staat in cookie)
      cur = db.execute("UPDATE workshops set plaatsen = plaatsen + 1 where id = ? ", [session['keuze']])
      # inschrijven nieuwe keuze
      # Dit is heel eng want plaatsen kan kleiner worden dan 0 helaas heeft sqllite geen GREATEST en MAX werkt niet
      # GETEST : werkt nog wel met "plaatsen = -10"
      # misschien moet plaatsen een unsigned int worden en dan afvangen van de error?
      cur = db.execute("UPDATE workshops set plaatsen = plaatsen - 1 where id = ?", [keuze])
      db.commit()

      #
      # VANG HIER ERRORS AF!!!!!!!!!!!!!!!!!!!!!!
      #

      # Schrijf nu de keuze in de user database
      #
#      flash('DEBUG: Attempting to write the user database')
      db.execute("UPDATE users set keuze = ? where id = ? ",
                   [keuze, session['username']])
      db.commit()
      #
      # VANG HIER ERRORS AF!!!!!!!!!!!!!!!!!!!!!!
      #


      session['keuze'] = keuze  # update cookie
      flash('Je hebt nu gekozen voor: '+str(workshops[keuze][1]))

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
          if session['keuze'] > 0:
            flash('Je hebt al eerder een workshop gekozen:')
          return redirect(url_for('show_entries'))
        else:
          error = "Login mislukt!"

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Je bent uitgelogd!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
