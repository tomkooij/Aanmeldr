# -*- coding: utf-8 -*-
"""
    Aanmeldr
    ~~~~~~~~

    Coornhert kerstworkshop aanmeldwebsite
    (Based on Flaskr, a Flask example. See README for license)

"""
import MySQLdb
import MySQLdb.cursors
#from sqlite3 import dbapi2 as sqlite3

import logging
from logging.handlers import RotatingFileHandler
from time import time

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

from flask_sslify import SSLify


import hashlib, os, binascii # crypto voor wachtwoorden

# import configuration
from configuration import *




# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
sslify = SSLify(app)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = MySQLdb.connect(host=MYSQLSERVER, user=MYSQLUSER, db=MYSQLDB, passwd=MYSQLPASS)
        #sqlite_db.row_factory = sqlite_db
        top.sqlite_db = sqlite_db

    return top.sqlite_db

#
# user defined function for show_entries.html Jinja template
#

@app.context_processor
def utility_processor():

    # Zit deze leerling in een klas die zich mag inschrijven voor een bepaalde workshop?
    # Voodoo functie:
    # filter (uit de workshop tabel) = 2**klas, bijvoorbeeld 2**1+2**2+2**3 voor onderbouw
    # klas (uit user tabel dan wel sessie cookie)= 1, 2, 3...
    #
    def workshop_voor_deze_klas(klas, filter):
        if (2**klas & int(filter)):
            return 1
        else:
            return 0
    return dict(workshop_voor_deze_klas=workshop_voor_deze_klas)

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
      cur = db.cursor()
      cur.execute('select id,titel,plaatsen,filter from workshops')
      workshops = cur.fetchall()
      if not session.get('logged_in'):
        return redirect(url_for('login'))

      return render_template('show_entries.html', workshops=workshops)

@app.route('/kies_workshop', methods=['POST'])
def kies_workshop():
    # volgende regel sluit de site
    #return render_template('offline.html')
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.cursor()
    cur.execute('select * from workshops')
    workshops = cur.fetchall()


    # maak een int van de keuze die in unicode binnenkomt
    # vang onbekende keuzes af
    tmp_keuze = request.form['keuze']
    if str(tmp_keuze).isdigit:
        keuze = int(tmp_keuze)
    else:
        keuze = 0

    #schrijf de logfile, dit is echt heel ernstige beuncode
    app.logger.info('%s gebruiker %d probeert %d', time(), session['username'], keuze)

    # als op de een of andere manier de worshop ID groter is dan het aantal
    if (keuze > (len(workshops)-1)):
        flash('OEPS! Er is iets fout gegaan. Je bent waarschijnlijk niet meer ingeschreven.','error')
        keuze = 0

    # zijn er nog plaatsen? Het kan best zijn dat de workshop inmiddels vol is
    # kies_workshop POST kan 2 dagen na de laaste GET van show_entries zijn
    if (workshops[keuze][2] < 1):
        flash('Sorry! Workshop is niet meer beschikbaar','error')
        return redirect(url_for('show_entries'))
    elif (keuze == session['keuze']):
        # keuze hetzelfde is als huidige kueze
        if (keuze == 0):
            flash('Niet ingeschreven. Maak een keuze: ','flash')
        else:
            flash('Je bent al ingeschreven voor deze workshop!','error')
        return redirect(url_for('show_entries'))
    else:

        # schrijf eerst de workshop database
        # uitschrijven huidige keuze (staat in cookie)
        cur = db.cursor()
        cur.execute("UPDATE workshops set plaatsen = plaatsen + 1 where id = %s ", [session['keuze']])
        # inschrijven nieuwe keuze
        # Dit is heel eng want plaatsen kan kleiner worden dan 0 helaas heeft sqllite geen GREATEST en MAX werkt niet
        # GETEST : werkt nog wel met "plaatsen = -10"
        # misschien moet plaatsen een unsigned int worden en dan afvangen van de error?
        cur.execute("UPDATE workshops set plaatsen = plaatsen - 1 where id = %s", [keuze])
        db.commit()
        #
        # VANG HIER ERRORS AF!!!!!!!!!!!!!!!!!!!!!!
        #

        # Schrijf nu de keuze in de user database
        #
        #      flash('DEBUG: Attempting to write the user database')
        cur.execute("UPDATE users set keuze = %s where id = %s ",
                   [keuze, session['username']])
        db.commit()
        #
        # VANG HIER ERRORS AF!!!!!!!!!!!!!!!!!!!!!!
        #


        session['keuze'] = keuze  # update cookie
        if (keuze == 0):
            flash('Je bent nog niet (of niet meer) ingeschreven!','error')
        else:
            flash('Je hebt nu gekozen voor: '+str(workshops[keuze][1]),'flash')

        #schrijf de logfile, dit is echt heel ernstige beuncode
        app.logger.info('%s gebruiker %d ingeschreven %d', time(), session['username'], keuze)

        return redirect(url_for('show_entries'))

def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/login', methods=['GET', 'POST'])
def login():
  # volgende regel sluit de site
  #return render_template('offline.html')

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

      # Haal userrecord uit database

 #     user = query_db('select naam,wachtwoord,salt,keuze,klas from users where id = %s',
 #                   [leerlingnummer], one=True)

      db = get_db()
      cur = db.cursor()

      cur.execute("select naam,wachtwoord,salt,keuze,klas from users where id = %s",[leerlingnummer])
      db.commit()

      user = cur.fetchone()


      if user is None:
        error = ('Leerlingnummer %s onbekend' % leerlingnummer)
      else:
        db_salt = user[2]
        db_hash = user[1]
        m = hashlib.sha1()
        m.update(db_salt+login_password)
        mijn_hash = m.hexdigest()

        if (mijn_hash==db_hash):
          error = "Login gelukt!"

          # store in session cookie (crypto)
          session['logged_in'] = True
          session['username'] = leerlingnummer
          session['naam'] = user[0]
          session['keuze'] = user[3]
          session['klas'] = user[4]
          flash('Welkom %s. Je bent ingelogd.' % user[0],'flash')
          if session['keuze'] > 0:
            flash('Je hebt al een workshop gekozen!','error')

          #schrijf de logfile
          app.logger.info('%s login %d', time(), session['username'])
          return redirect(url_for('show_entries'))

        else:
          #schrijf de logfile, dit is echt heel ernstige beuncode
          app.logger.info('%s failpasswd %d', time(), leerlingnummer)
          error = "Login mislukt!"

  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Je bent uitgelogd!','flash')
    return redirect(url_for('login'))

if __name__ == '__main__':
    handler = RotatingFileHandler('aanmeldr.log', maxBytes=10000, backupCount=100)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.debug = False
    app.run()
