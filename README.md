Aanmeldr -- aanmeldwebsite voor Kerstworkshops

(GPLv3)

Based on Flaskr - Flask example.
Flask is copyright (c) 2013 by Armin Ronacher and contributors. BSD license.

github.com/tomkooij/Aanmeldr

Tom Kooij, oktober 2014

Note @self:
Hoe werkt dit?

**Dit is inelkaar gehackt tijdens de zwemlessen van Femke in oktober 2014**
**DO NOT USE THIS CODE**

site is tomkooij.pythonanywhere.com. 

workflow:
- Zet site offline: zie commit tomkooij/Aanmeldr@0fd285f
- vervang secrets in `configuration.py`. Verander het MySQL ww in de webinterface.
- Exporteer leerlingen (klas 2 t/m 6) uit SOMtoday.
- Vervang kolom emailadressen door: =TEKST.SAMENVOEGEN("cg"; A2; "@coornhert-gymnasium.nl")
- sla op als `users.csv` en upload naar mysite/Aanmeldr
- `cd mysite/Aanmeldr`
- `ipython; run db_tools.py; read_users_and_write_passwords();`
- nu worden de ww gegeneerd en `passwd.csv` en `mailmerge.csv` gescherven.
- test het inloggen op tomkooij.pythonanywhere.com
- vul de workshops in in `db_tools.py`.
- gebruik `write_workshops()` (verwijder '`return 1` in de buurt van "let's don't and say we did")
- TEST, TEST, TEST
- Laat cgfix de mailmerge rondsturen.
- **DOEN: Deactiveer:** `write_workshops()` en `create_userdb()` dmv "let's don't and say we did"
- `ipython; run db_tools.py; write_workshops(); write_userdb();` Werkte dit??? Ga terug naar AF!
- TEST, TEST, TEST
- Zet `AANTAL_LLN` in `db_tools.py` en `process_workshop_keuzes()`
- Ga live: tomkooij/Aanmeldr@0fd285f
- gebruik `db_tools.py` om te monitoren: `process_workshop_keuzes()`

Achteraf:
- commit en push! 

