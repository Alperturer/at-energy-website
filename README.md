# Website AT Energy Solutions

Statische site (losse HTML-bestanden) + één serverless functie voor het contactformulier. Gemaakt voor Vercel.

## Structuur
- `build.py` — bron van alle pagina's. Teksten aanpassen → `python3 build.py` → HTML wordt opnieuw gegenereerd (ook sitemap.xml en robots.txt).
- `assets/css/style.css`, `assets/js/main.js` — styling en kleine scripts (geen frameworks, geen externe scripts).
- `api/contact.js` — verwerkt het contactformulier server-side en mailt via Resend.
- `vercel.json` — nette URL's (/zonnepanelen i.p.v. /zonnepanelen.html), beveiligingsheaders, caching.

## Handmatig nog te doen vóór livegang
1. **Open punten** — zoek in `build.py` op `TODO` (telefoonnummer `PHONE`, reviews `REVIEWS`). Zijn ze leeg, dan verbergt de site die onderdelen automatisch (telefoon, openingstijden, plaatsen in het werkgebied, lokale projecten, review, oprichtingsverhaal, auteur, F-gassen, garantie, offertekosten, reactietermijn). Daarna `python3 build.py`.
2. **Foto's** — de site gebruikt echte foto's van Unsplash (gratis voor commercieel gebruik, geen naamsvermelding nodig). Ze worden nu geladen vanaf images.unsplash.com. Draai één keer `python3 download_images.py` en daarna `python3 build.py` om ze zelf te hosten. Eigen projectfoto's? Zet ze als `assets/img/<naam>.jpg` (namen staan in `PHOTOS` in build.py) en draai `python3 build.py`.
