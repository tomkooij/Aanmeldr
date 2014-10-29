# Read from sqlite datables

import sqlite3
import sys
import hashlib, os, binascii # crypto voor wachtwoorden

def print_db():
  db = sqlite3.connect('flaskr.db')

  with db:
      db.row_factory = sqlite3.Row   # this enables the dictionary cursor

      cur = db.cursor()
      cur.execute("SELECT * FROM users")

      rows = cur.fetchall()

      for row in rows:
          print row

      for row in rows:
          print "%s %s" % (row["naam"], row["keuze"]) # use the dictionary cursor

def write_db_test():

  testtabel = (
    (1234,'Tom Kooij', 'b884c7577e7e04c0b9a8e242964db5dd', 'a8e6833a4588467a0702', 15), # wachtwoord = "geheim"
    (3141,'Pi','wachtwoord', 'salt', 1),
    (2789,'EEeee','wachtwoord', 'zout', 3),
    (007,'James Bond','test', 'peper', 7),
    (1,'Test Leerling','geheim', 'kruiden',1)
    )

  db = sqlite3.connect('flaskr.db')

  with db:

      cur = db.cursor()
#      cur.execute("INSERT INTO users VALUES (3145,'Pi','wachtwoord',1);")
#      cur.execute("INSERT INTO users VALUES (2789,'EEeee','wachtwoord',3);")
#      cur.execute("INSERT INTO users VALUES (007,'James Bond','wachtwoord',7);")
#      cur.execute("INSERT INTO users VALUES (1,'Test Leerling','geheim',1);")

      cur.execute("DROP TABLE IF EXISTS users")
      cur.execute("CREATE TABLE users(id INT, naam TEXT, wachtwoord TEXT, salt TEXT, keuze INT )")
      cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?)", testtabel)
      db.commit()

def sel():

  db = sqlite3.connect('flaskr.db')

  with db:
      cur = db.cursor()

      cur.execute("SELECT Naam, Wachtwoord FROM users WHERE Id=1234")
      db.commit()

      row = cur.fetchone()
      print row[0], row[1]


def change_ww(leerlingnummer, wachtwoord):
  db = sqlite3.connect('flaskr.db')

  with db:
      cur = db.cursor()

      cur.execute("UPDATE users SET wachtwoord=? WHERE id=?", (wachtwoord,leerlingnummer))
      db.commit()



def check_login(username, wachtwoord):

  leerlingnummer = int(username)
  
  db = sqlite3.connect('flaskr.db')

  with db:

      db.row_factory = sqlite3.Row   # this enables the dictionary cursor
      cur = db.cursor()

      cur.execute("SELECT * FROM users WHERE Id=:Id", {"Id": leerlingnummer})
      db.commit()

      row = cur.fetchone()
      db_wachtwoord = row["wachtwoord"]
      db_salt = row["salt"]

      m = hashlib.md5()
      m.update(db_salt+wachtwoord)
      mijn_hash = m.hexdigest()

      print "naam in database: ", row["naam"]
      print "wachtwoord in db: ", db_wachtwoord
      print wachtwoord, mijn_hash

      if (mijn_hash==row["wachtwoord"]):
        return True

  return False
