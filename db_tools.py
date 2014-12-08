# several function used for development of aanmeldr
#   will be replaced by a toolchain for setting up the database
#
#
# usage: set up (test) database:
#  from db_tools import *
#  write_testdb()
#  write_workshops()
#  print_db()


#import sqlite3
import MySQLdb
import MySQLdb.cursors

import sys
import hashlib, os, binascii # crypto voor wachtwoorden
import random
import csv

# configuration (DATABASE location)
from configuration import DATABASE

def print_db():
    db = MySQLdb.connect(host='mysql.server', user='tomkooij', db='tomkooij$aanmeldr', passwd='geheim123')

    with db:
#         db.row_factory = sqlite3.Row   # this enables the dictionary cursor

        cur = db.cursor()
        cur.execute("SELECT * FROM users")

        rows = cur.fetchall()

        for row in rows:
            print row

#        for row in rows:
#            print "%s %s" % (row["naam"], row["keuze"]) # use the dictionary cursor

def print_workshops():
  #db = sqlite3.connect(DATABASE)
  db = MySQLdb.connect(host='mysql.server', user='tomkooij', db='tomkooij$aanmeldr', passwd='geheim123', cursorclass=MySQLdb.cursors.DictCursor)

  with db:
#      db.row_factory = MySQLdb.Row   # this enables the dictionary cursor

      cur = db.cursor()
      cur.execute("SELECT * FROM workshops")

      rows = cur.fetchall()

      for row in rows:
          print row

klas1 = 2**1
klas2 = 2**2
klas3 = 2**3
klas4 = 2**4
klas5 = 2**5
klas6 = 2**6
onderbouw = klas1+klas2+klas3
bovenbouw = klas4+klas5+klas6
alles = onderbouw+bovenbouw

def write_workshops():
    workshops = ( (0,"Geen keuze",100000, alles  ),
          (1,"Bootcamp", 20, alles ),
          (2,"Waterpolo", 25, klas3+klas4+klas5+klas6 ),
          (3,"Sporten in de Mammoet", 95 , onderbouw ),
          (4,"Vogelen", 15, alles),
          (5,"Debatteren", 40, alles),
          (6,"Kerstballen maken", 25, alles),
          (7,"EHBO", 20, alles),
          (8,"Film Flypaper", 30, onderbouw ),
          (9,"Film Pans Labyrinth", 30, onderbouw ),
          (10,"Film Shawshank redemption" 30 , alles ),
          (11,"Film Filmhuis", 75, bovenbouw),
          (12,"Dansen Step by Step", 40, alles),
          (13,"Schaken", 40, alles),
          (14,"Theaterworkshop (school)", 12, alles),
          (15,"Yoga. Klankworkshop", 25, alles),
          (16,"Theatertechniek", 10, alles),
          (17,"Zumba", 30, alles),
          (18,"Voedselbank", 10, alles),
          (19,"Striptekenen", 18, alles),
          (20,"Portrettekenen", 16, alles),
          (21,"Fotografie", 16, alles),
          (22,"Theater (kunstpunt)", 20, alles),
          (23,"Musical", 20, alles),
          (24,"Popzang", 16, alles),
          (25,"Logo Design", 18, alles),
          (23,"Power tape", 16, alles),
          (24,"Streetdance", 20, alles),
          (25,"Ritmesectieworkshop drum", 10, alles)
          )

    #db = sqlite3.connect(DATABASE)
    db = MySQLdb.connect(host='mysql.server', user='tomkooij', db='tomkooij$aanmeldr', passwd='geheim123')

    with db:

        cur = db.cursor()
        #      cur.execute("INSERT INTO users VALUES (3145,'Pi','wachtwoord',1);")
        #      cur.execute("INSERT INTO users VALUES (2789,'EEeee','wachtwoord',3);")
        #      cur.execute("INSERT INTO users VALUES (007,'James Bond','wachtwoord',7);")
        #      cur.execute("INSERT INTO users VALUES (1,'Test Leerling','geheim',1);")

        cur.execute("DROP TABLE IF EXISTS workshops")
        cur.execute("CREATE TABLE workshops(id INT, titel TEXT, plaatsen INT, filter INT )")
        db.commit()
        cur.executemany("INSERT INTO workshops VALUES(%s, %s, %s, %s)", workshops)
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
        with open('passwd.csv', 'wb') as f:
            write_passwd = csv.writer(f, dialect='excel')
            with open('mailmerge.csv', 'wb') as f2:
                mailmerge = csv.writer(f2,  dialect='excel')
                mailmerge.writerow(['id', 'naam', 'ww','email'])

                reader.next() # skip first row (legend)
                for row in reader:
                    #print row
                    leerlingnummer = int(row[0])
                    klas = int(row[5][0])
                    email = row[4]

                    password = generate_password(10)
                    salt = generate_password(64)

                    # create the salted hash form password
                    m = hashlib.sha1()
                    m.update(salt+password)
                    hashedpassword = m.hexdigest()  # the salted hash

                    naam = unicode((row[2]+' '+row[3]).decode('utf-8','ignore')) # strip illegal chars
                    voornaam = naam.split(' ')[0]

                    print [leerlingnummer, voornaam, klas, email]

                    write_passwd.writerow([leerlingnummer, naam, hashedpassword, salt, klas, 0])
                    mailmerge.writerow([leerlingnummer,voornaam, password, email, naam])

def create_userdb():

    usertable = []

    with open('passwd.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # copy CSV file tot usertable list
        for row in reader:
            print row
            usertable.append(row)

    db = MySQLdb.connect(host='mysql.server', user='tomkooij', db='tomkooij$aanmeldr', passwd='geheim123')

    with db:

        cur = db.cursor()

        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("CREATE TABLE users(id INT, naam TEXT, wachtwoord TEXT, salt TEXT, klas INT, keuze INT )")
        cur.executemany("INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s)", usertable)
        db.commit()

def sel():

  db = MySQLdb.connect(host='mysql.server', user='tomkooij', db='tomkooij$aanmeldr', passwd='geheim123')

  with db:
      cur = db.cursor()

      cur.execute("select naam,wachtwoord,salt,keuze,klas from users where id = 2651")
      db.commit()

      row = cur.fetchone()
      print row
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
    print "This is db_tools.py!\n"
    print "Setup database:"
    print "read_users_and_write_passwords() reads users.csv and writes output.csv"
    print "create_userdb() writes user/pass from output.csv to the database"
    print "write_workshops() writes the workshops to the database"
    print "\nprint_db() to dump the database"
