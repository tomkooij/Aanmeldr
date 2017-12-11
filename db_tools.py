# several function used for development of aanmeldr
#   should be replaced by a toolchain for setting up the database
#
import MySQLdb
import MySQLdb.cursors

import sys
import hashlib, os  # crypto voor wachtwoorden
import random
import csv
import random

# configuration.py bevat MYSQLSERVER, MYSQLPASS e.d.
from configuration import *

# ToDo: Haal dit uit user table:
AANTAL_LLN = 602


klas1 = 2**1  # doet niet mee!!!
klas2 = 2**2
klas3 = 2**3
klas4 = 2**4
klas5 = 2**5
klas6 = 2**6

# LET OP!!! KLAS 1 doet niet mee!!
onderbouw = klas2+klas3
bovenbouw = klas4+klas5+klas6
alles = onderbouw+bovenbouw


workshops_invoer = [ ("Geen keuze ", 100000, alles),
# klas 2
    ("Sport in de Mammoet ", 40 , klas2),
    ("Circus in Mammoet ", 10, klas2),
    ("Workshop Powertape", 14, klas2),
    ("Workshop Theater ", 18, klas2),
    ("Workshop Musical ", 18, klas2),
    ("Workshop Striptekenen ", 16, klas2),
    ("Vogels kijken ", 4, klas2),
    ("Schaken ", 5, klas2),
# klas 3
    ("Sport in Mammoet ", 40, klas3),
    ("Circus in Mammoet ", 10, klas3),
    ("Freerunning Mammoet Jaap Oostrom", 3, klas3),
    ("Fotografie (garenspinnerij)", 10, klas3),
    ("Popzang (garenspinnerij)", 15, klas3),
    ("Djembe en ritme (garenspinnerij)", 15, klas3),
    ("Streetdance (garenspinnerij) ", 10, klas3),
    ("Vogels kijken ", 5, klas3),
    ("Muziek: Workshop Messiah (Om) ", 5, klas3),
    ("Schaken", 7, klas3),
    ("Yoga/mediteren ", 7, klas3),
# klas 4
    ("Step by Step ", 40, klas4),
    ("Freerunning Mammoet Jaap Oostrom", 10, klas4),
    ("Bootcamp met Noor ", 10, klas4),
    ("Streetdance (garenspinnerij)", 10, klas4),
    ("3D-pen tekenen (garenspinnerij)", 3, klas4),
    ("Animatiefilm (garenspinnerij)", 3, klas4),
    ("Fotografie (garenspinnerij)", 5, klas4),
    ("Muziek: Workshop Messiah (Om) ", 12, klas4),
    ("Vogels kijken", 5, klas4),
    ("Schaken", 6, klas4),
    ("Yoga/mediteren ", 5, klas4),
    ("D&D", 4, klas4),
# klas 5+6
    ("Film Premiere: Wonder Cinema Gouda", 197, klas5+klas6),
    ("Freerunning Mammoet Jaap Oostrom", 5, klas5+klas6),
    ("3D-pen tekenen (garenspinnerij)", 7, klas5+klas6),
    ("Animatiefilm (garenspinnerij)", 7, klas5+klas6),
    ("Muziek: Workshop Messiah (Om) ", 7, klas5+klas6),
    ("Vogels kijken", 3, klas5+klas6),
    ("Schaken", 2, klas5+klas6),
    ("D&D", 5, klas5+klas6),
    ("Yoga/mediteren ", 3, klas5+klas6)
    ]

workshops = []
for idx, workshop in enumerate(workshops_invoer):
    titel, plaatsen, filter_ = workshop
    wkshop = (idx, titel, plaatsen, filter_)
    workshops.append(wkshop)


def get_db():
    return MySQLdb.connect(host=MYSQLSERVER, user=MYSQLUSER,
                           db=MYSQLDB, passwd=MYSQLPASS)


def print_db():
    db = get_db()

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM users")

        rows = cur.fetchall()

        for i, row in enumerate(rows):
            print i, row


def print_workshops():
    db = get_db()

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM workshops")

        rows = cur.fetchall()

    for row in rows:
        print row


def write_workshops():

    # deze functie OVERSCHRIJFT DE DATABASE INCLUSIEF KEUZES!
    print "Let's don't and say we did!"
    return 1

    db = get_db()

    with db:
        cur = db.cursor()

        cur.execute("DROP TABLE IF EXISTS workshops")
        cur.execute("CREATE TABLE workshops(id INT, titel TEXT, plaatsen INT, filter INT )")
        db.commit()
        cur.executemany("INSERT INTO workshops VALUES(%s, %s, %s, %s)", workshops)
        db.commit()

        aantal_plaatsen = 0
        for workshop in workshops:
            aantal_plaatsen += workshop[2]
        print "controleer: %d plaatsen" % aantal_plaatsen


def fix_lastname(s):
    """Kooij, van den --> van den Kooij"""
    parts = s.split(', ')
    if len(parts) == 2:
        return parts[1] + ' ' + parts[0]
    else:
        return s


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
                    # print row
                    leerlingnummer = int(row[0])
                    klas = int(row[5][0])
                    email = row[6]

                    password = generate_password(6)
                    salt = generate_password(64)

                    # create the salted hash form password
                    m = hashlib.sha1()
                    m.update(salt+password)
                    hashedpassword = m.hexdigest()  # the salted hash

                    naam = unicode((row[2]+' '+fix_lastname(row[3])).decode('utf-8','ignore')) # strip illegal chars
                    voornaam = naam.split(' ')[0]

                    print [leerlingnummer, voornaam, klas, email]

                    write_passwd.writerow([leerlingnummer, naam, hashedpassword, salt, klas, 0])
                    mailmerge.writerow([leerlingnummer,voornaam, password, email, naam])


def create_userdb():
    """
    Lees passwd.csv en maak user table
    """

    # Overschrijf de database!!!!!
    #print "Let's don't and say we did!"
    #return 1

    usertable = []

    with open('passwd.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # copy CSV file tot usertable list
        for row in reader:
            print row
            usertable.append(row)

    db = get_db()

    with db:
        cur = db.cursor()

        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("CREATE TABLE users(id INT, naam TEXT, wachtwoord TEXT, salt TEXT, klas INT, keuze INT )")
        cur.executemany("INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s)", usertable)
        db.commit()


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

def sort_name(s):
    """ Jan van der Belt --> Belt. Jan van der"""
    parts = s.rsplit(' ', 1)
    return parts[1]+'. '+parts[0]


def process_workshop_keuzes():

    #
    # Maak een tabel van ingeschreven leerlingen (en sla op als CSV ofzo)
    #
    ingeschreven = [] # de grote inshrijf lijst

    db = get_db()

    with db:
        cur = db.cursor()
        cur.execute("SELECT id,naam, klas, keuze FROM users")

        rows = cur.fetchall()
        print "Dit is een CSV file! Kopieer naar Atom. Save. Importeer daarna in Excel"
        for workshop in workshops:
            print "\"workshop: ", workshop[1],"\""
            lijst_deze_workshop = [workshop[0], workshop[1], workshop[2]]
            tellertje = 1
            for row in rows:
                if (row[3] == workshop[0]):  # user heeft deze workshop gekozen
                    print " %d , ingeschreven:, %s, %d, %d, %d, %s " % (tellertje, sort_name(row[1].replace(',',' ')), row[0], row[2], workshop[0], workshop[1])
                    tellertje += 1 # oh nee wat een hack
                    lijst_deze_workshop.append(row[0])
            lijst_deze_workshop.append(tellertje) # laatste item is aantal ingeschreven... brrrr hack
            ingeschreven.append(lijst_deze_workshop)

    #
    # ER ZIT EEN ENORME BUG IN DEZE CODE. Direct na inschrijven ontstaat er een database error volgens print_workshops() en ingeschreven = [] bevat dan
    # meerdere kopien van de lijst
    #

    print_workshop_keuzes(ingeschreven)
    #write_ingeschreven(ingeschreven)


def write_ingeschreven(ingeschreven):
    """schrijf ingescherven lln + keuzes naar CSV"""
    print "writing: ingeschreven.csv"
    with open('ingeschreven.csv', 'wb') as f:
        mailmerge = csv.writer(f,  dialect='excel')
        for row in ingeschreven:
            mailmerge.writerow(row)


def save_db_to_csv():
    """Maak backup.csv"""
    db = get_db()

    with db:
        cur = db.cursor()
        cur.execute("SELECT id,naam, klas, keuze FROM users")

        rows = cur.fetchall()
        with open('backup.csv', 'wb') as f:
            csvbackup = csv.writer(f, dialect='excel')

            for row in rows:
                csvbackup.writerow(row)


def print_workshop_keuzes(ingeschreven):

    db = get_db()

    plaatsen = {}

    with db:
        cur = db.cursor()
        cur.execute("SELECT id,plaatsen FROM workshops")

        workshops_db = cur.fetchall()

        for row in workshops_db:
            plaatsen[row[0]]=row[1]

    nog_vrij = 0

    #print "DEBUG: ingeschreven (global list)=",ingeschreven

    for workshop in ingeschreven:
        #print "Workshop: ",workshop[0], workshop[1]

        if (workshop[0]>0):
            aantal_ingeschreven = len(workshop)-4 # haal er drie af, dat is de workshop info (3) en de teller (eind)
            plaatsen_over = plaatsen[workshop[0]]
            totaal_plaatsen = workshop[2]
            aantal_lln_ingeschreven = workshop[-1] # laatste item in lijst is aantal

            nog_vrij += plaatsen_over

            if (plaatsen_over)>0:
                print "%d.\tIngeschreven %d van %d Nog over: %d \t %s " % (workshop[0],aantal_ingeschreven, totaal_plaatsen, plaatsen_over,workshop[1] )
            else:
                print "%d. VOL\tIngeschreven %d van %d Nog over: %d \t %s " % (workshop[0],aantal_ingeschreven, totaal_plaatsen, plaatsen_over,workshop[1] )

            if (aantal_lln_ingeschreven != aantal_ingeschreven+1):
                print "LET OP!!!! DATABASE ERROR"
                print "aantal ingeschreven is %d (getelt in table users) en %d (in table workshops)" % (aantal_lln_ingeschreven, aantal_ingeschreven)

            if (plaatsen_over != (totaal_plaatsen - aantal_ingeschreven)):
                print "LET OP!!!! DATABASE ERROR"
                print "plaatsen moet %d zijn" % (totaal_plaatsen - aantal_ingeschreven)

    print "\n%d leerlingen ingeschreven" % (AANTAL_LLN-(len(ingeschreven[0])-3))
    print "Nog %d te gaan" % (len(ingeschreven[0])-3)
    print "Er zijn nog %d plaatsen beschikbaar" % nog_vrij


def set_plaatsen(workshop_id, plaatsen):
    """HACK voor database errors"""
    print "Ik zet workshop %d op %d" % (workshop_id, plaatsen)

    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute("UPDATE workshops set plaatsen = %s where id = %s ", [plaatsen, workshop_id])
        db.commit()

def set_desc(workshop_id, omschrijving):
    print "Ik zet workshop %d titel op %s" % (workshop_id, omschrijving)

    db = get_db()
    with db:
        cur = db.cursor()
        cur.execute("UPDATE workshops set titel = %s where id = %s ",
                            [omschrijving, workshop_id])
        db.commit()


def hotfix_NIETGEBRUIKEN():
    """HACK Voor het toegoegen van een (vergeten) workshop"""
    print "NIET GEBRUIKEN!!!"
    print "Let's don't and say we did...!?"
    return 0

    db = get_db()
    # heb je deze ook al in de workshops lijst toegevoegd!?!?!?!?
    temp = ((32,"EXTRA: bordspellen",20,bovenbouw),
    (33,"EXTRA: schaken (alleen bovenbouw)",20,bovenbouw))

    print "Ik ga een regel toevoegen in table workshops. Staat deze ook al in de lijst workshops in de code?", temp
    with db:

        cur = db.cursor()

        cur.executemany("INSERT INTO workshops VALUES(%s, %s, %s, %s)", temp)
        db.commit()
    print "Ik hoop dat je dit niet in een live productieomgeving hebt gebruikt.\n Je test het toch nog wel even?"


if __name__=='__main__':
    print "db_tools.py!"
    print ""
    print "Setup database:"
    print "read_users_and_write_passwords() reads users.csv and writes output.csv"
    print "create_userdb() writes user/pass from output.csv to the database"
    print "write_workshops() writes the workshops to the database"
    print ""
    print "print_db() to dump the database"
    print ""
    print "process_workshop_keuzes() geeft output"
    print "print workshops geeft workshops zoals ingevoerd"
    print "set_plaatsen() GEVAARLIJK kan gebruikt worden om "
    print "aantal plaatsen per workshop te fixen"
    print "save_db_to_csv() maakt een reservekopie van de DB"
