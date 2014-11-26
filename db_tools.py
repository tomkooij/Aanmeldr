# several function used for development of aanmeldr
#   will be replaced by a toolchain for setting up the database
#
#
# usage: set up (test) database:
#  from db_tools import *
#  write_testdb()
#  write_workshops()
#  print_db()


import sqlite3
import sys
import hashlib, os, binascii # crypto voor wachtwoorden
import random
import csv

DATABASE = 'flaskr.db'

def print_db():
  db = sqlite3.connect(DATABASE)

  with db:
      db.row_factory = sqlite3.Row   # this enables the dictionary cursor

      cur = db.cursor()
      cur.execute("SELECT * FROM users")

      rows = cur.fetchall()

      for row in rows:
          print row

      for row in rows:
          print "%s %s" % (row["naam"], row["keuze"]) # use the dictionary cursor

def print_workshops():
  db = sqlite3.connect(DATABASE)

  with db:
      db.row_factory = sqlite3.Row   # this enables the dictionary cursor

      cur = db.cursor()
      cur.execute("SELECT * FROM workshops")

      rows = cur.fetchall()

      for row in rows:
          print row



def write_workshops():
    workshops = ( (0,"Geen keuze",100000),
          (1,"Film", 5),
          (2,"Sport", 5),
          (3,"Dansen", 15),
          (4,"Kerstkaarten maken", 5),
          (5,"Robots bouwen", 5),
          (6,"l33t h4x0rs", 1) )



    db = sqlite3.connect(DATABASE)

    with db:

        cur = db.cursor()
        #      cur.execute("INSERT INTO users VALUES (3145,'Pi','wachtwoord',1);")
        #      cur.execute("INSERT INTO users VALUES (2789,'EEeee','wachtwoord',3);")
        #      cur.execute("INSERT INTO users VALUES (007,'James Bond','wachtwoord',7);")
        #      cur.execute("INSERT INTO users VALUES (1,'Test Leerling','geheim',1);")

        cur.execute("DROP TABLE IF EXISTS workshops")
        cur.execute("CREATE TABLE workshops(id INT, titel TEXT, plaatsen INT )")
        cur.executemany("INSERT INTO workshops VALUES(?, ?, ?)", workshops)
        db.commit()




def write_testdb():

  testtabel = (
    (1234,'Tom Kooij', '234655232ffd54cb74f6d75aa65132f79c0f404f', 'a8e6833a4588467a0702', 15), # wachtwoord = "geheim"
    (3141,'Pi','b107f52a6e547eb63666ef74ac39525db2917116', 'salt', 1),
    (2789,'EEeee','wachtwoord', 'zout', 3),
    (007,'James Bond','test', 'peper', 7),
    (1,'Test Leerling','geheim', 'kruiden',1)
    )

  db = sqlite3.connect(DATABASE)

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

def read_users_and_write_passwords():

    with open('users.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
        with open('output.csv', 'wb') as f:
            writer = csv.writer(f)

            for row in reader:
                leerlingnummer = row[0]
                password = generate_password(10)
                salt = generate_password(64)

                naam = unicode((row[2]+' '+row[3]).decode('utf-8','ignore')) # strip illegal chars

                print [leerlingnummer, naam, password, salt, 0]
                writer.writerow([leerlingnummer, naam, password, salt, 0])


def create_userdb():

    usertable = []

    with open('output.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            # read password and salt from csv
            db_salt = row[3]
            wachtwoord = row[2]     # the real password

            # create the salted hash for the passwd csv
            m = hashlib.sha1()
            m.update(db_salt+wachtwoord)
            row[2] = m.hexdigest()  # the salted hash
            print row
            usertable.append(row)

    db = sqlite3.connect(DATABASE)

    with db:

        cur = db.cursor()

        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("CREATE TABLE users(id INT, naam TEXT, wachtwoord TEXT, salt TEXT, keuze INT )")
        cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?)", usertable)
        db.commit()

def sel():

  db = sqlite3.connect(DATABASE)

  with db:
      cur = db.cursor()

      cur.execute("SELECT Naam, Wachtwoord FROM users WHERE Id=1234")
      db.commit()

      row = cur.fetchone()
      print row[0], row[1]


def change_ww(leerlingnummer, wachtwoord):
  db = sqlite3.connect(DATABASE)

  with db:
    db.row_factory = sqlite3.Row   # this enables the dictionary cursor
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE Id=:Id", {"Id": leerlingnummer})
    db.commit()

    row = cur.fetchone()
    db_salt = row["salt"]

    m = hashlib.sha1()
    m.update(db_salt+wachtwoord)
    mijn_hash = m.hexdigest()

    cur = db.cursor()

    cur.execute("UPDATE users SET wachtwoord=? WHERE id=?", (mijn_hash,leerlingnummer))
    db.commit()



def check_login(username, wachtwoord):

  leerlingnummer = int(username)

  db = sqlite3.connect(DATABASE)

  with db:

      db.row_factory = sqlite3.Row   # this enables the dictionary cursor
      cur = db.cursor()

      cur.execute("SELECT * FROM users WHERE Id=:Id", {"Id": leerlingnummer})
      db.commit()

      row = cur.fetchone()
      db_wachtwoord = row["wachtwoord"]
      db_salt = row["salt"]

      m = hashlib.sha1()
      m.update(db_salt+wachtwoord)
      mijn_hash = m.hexdigest()

      print "naam in database: ", row["naam"]
      print "wachtwoord in db: ", db_wachtwoord
      print wachtwoord, mijn_hash

      if (mijn_hash==row["wachtwoord"]):
        return True

  return False

#
# random.choice() is size(2^50=1e15)
#    size of the password is ((24+8)^length)
#    (32^10 = (2^5)^10 = 2^50)
#    length=10 is the best password length
#
def generate_password(length):
    pw_set = ('abcdefghijkmnpqrstuvwxyz'
                '23456789')
    pw = length * ' '
    return ''.join([random.choice(pw_set) for c in pw])


if __name__=='__main__':
    print "This is db_tools.py!"
