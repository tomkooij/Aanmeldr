Aanmeldr -- aanmeldwebsite voor Kerstworkshops

(GPLv3)

Based on Flaskr - Flask example.
Flask is copyright (c) 2013 by Armin Ronacher and contributors. BSD license.

github.com/tomkooij/Aanmeldr

Tom Kooij, oktober 2014

Note @self:
Hoe werkt dit?
- site is tomkooij.pythonanywhere.com. Zet offline: Ga live: tomkooij/Aanmeldr@0fd285f
- vervang secrets in `configuration.py`. Verander het MySQL ww in de webinterface.
- Exporteer leerlingen (klas 2 t/m 6) uit SOMtoday.
- Vervang kolom emailadressen door: =TEKST.SAMENVOEGEN("cg"; A2; "@coornhert-gymnasium.nl")
- sla op als `users.csv` en upload
- `ipython; run db_tools.py; read_users_and_write_passwords();`
- nu worden de ww gegeneerd en `passwd.csv` en `mailmerge.csv` gescherven.
- test het inloggen op tomkooij.pythonanywhere.com
- vul de workshops in in `db_tools.py`.
- gebruik `write_workshops()`
- TEST, TEST, TEST
- Laat cgfix de mailmerge rondsturen.
- Ga live: tomkooij/Aanmeldr@0fd285f
- gebruik `db_tools.py` om te monitoren.
