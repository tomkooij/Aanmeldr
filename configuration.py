# configuration.py
# configuration variables
#
#
# local testing
#DATABASE = 'flaskr.db'
#DEBUG = True # SSLify requires DEBUG = False
#SECRET_KEY = 'This should be changed in a production enviroment'
#
# pythonanywhere
DEBUG = True

MYSQLSERVER = 'tomkooij.mysql.pythonanywhere-services.com'
MYSQLDB = 'tomkooij$aanmeldr'
MYSQLUSER = 'tomkooij'

# secrets
SECRET_KEY = 'github'
MYSQLPASS = 'github'

# site open at:
# zet de site NA het 8ste uur open! Er zijn vaak toetsen het 8ste!
SITE_OPEN = '7 Dec 2017 16:15'  # let op hours / min zijn ZERO PADDED!
