#!/usr/bin/env python3
"""Genereert alle HTML-pagina's, sitemap.xml en robots.txt voor AT Energy Solutions.
Pas teksten hier aan en draai:  python3 build.py
Open punten staan als TODO in dit bestand."""
import json, os, html
from datetime import date

BASE = "https://atenergysolutions.nl"   # TODO: definitieve domeinvariant (met/zonder www) bevestigen
TODAY = date.today().isoformat()
OUT = os.path.dirname(os.path.abspath(__file__))
PAGES = []  # (path, noindex)

EMAIL = "info@atenergysolutions.nl"
KVK = "24401102"
PHONE = ""   # TODO: telefoonnummer invullen, bijv. "010 123 45 67"; verschijnt dan automatisch op de site
PHONE_LI = f'<li><a href="tel:{PHONE.replace(" ", "")}">{PHONE}</a></li>' if PHONE else ''
PHONE_BR = f'<br><a class="link" href="tel:{PHONE.replace(" ", "")}">{PHONE}</a>' if PHONE else ''
PHONE_DL = f'<div><dt>Telefoon</dt><dd><a class="link" href="tel:{PHONE.replace(" ", "")}">{PHONE}</a></dd></div>' if PHONE else ''
REVIEWS = []  # TODO: echte reviews toevoegen als (citaat, naam, plaats) — met toestemming
PH_ADDR = 'Hoofdweg Noord 11, 2913 LB Nieuwerkerk aan den IJssel'
PH_REGIO = 'Nieuwerkerk aan den IJssel en omgeving'

# ---------- Iconen & logo ----------
_UNUSED_LOGO = '''<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="11" fill="currentColor"/><path d="M9 26a11 11 0 0 1 22 0Z" fill="#2ED3C6"/><rect x="7" y="28.5" width="26" height="2.6" rx="1.3" fill="#2ED3C6"/></svg>'''
I = {
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>',
 "shield": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M16 3l11 4v8c0 7-4.7 11.6-11 14-6.3-2.4-11-7-11-14V7z"/><path d="M11 16l3.5 3.5L21 13" stroke-linecap="round"/></svg>',
 "tool": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 4.5a7 7 0 0 0-8.6 9L4 21.4V28h6.6l7.9-7.9a7 7 0 0 0 9-8.6l-4.4 4.4-4.2-1.4-1.4-4.2z"/></svg>',
 "plug": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4v7M21 4v7M7 11h18v5a9 9 0 0 1-18 0zM16 25v4"/></svg>',
 "talk": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M5 7h22v14H14l-6 5v-5H5z"/><path d="M10 13h12M10 17h7" stroke-linecap="round"/></svg>',
 "grow": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 26h24M7 21l6-6 5 4 9-10"/><path d="M21 9h6v6"/></svg>',
}

# Echte foto's (Unsplash-licentie: gratis commercieel gebruik, geen naamsvermelding verplicht).
# Draai download_images.py om ze lokaal te zetten; build.py gebruikt dan automatisch assets/img/<naam>.jpg.
PHOTOS = {
    "hero-woning":   ("flagged/photo-1566838616631-f2618f74a6a2", "Monteur legt zonnepanelen op een pannendak"),
    "zonnepanelen":  ("photo-1635424709870-cdc6e64f0e20", "Zonnepanelen op een pannendak met montagerails en kabels"),
    "thuisbatterij": ("photo-1758101755915-462eddc23f57", "Monteur sluit een thuisbatterijsysteem aan in een garage"),
    "warmtepomp":    ("photo-1776860150305-108ed577d7d4", "Monteur installeert de buitenunit van een warmtepomp"),
    "airco":         ("photo-1762341123870-d706f257a12e", "Monteurs installeren een airco met binnen- en buitenunits"),
    "zakelijk":      ("photo-1713544123580-12096cc9eb12", "Monteur met valbeveiliging op een dak met zonnepanelen"),
    "team":          ("photo-1635424709845-3a85ad5e1f5e", "Monteur werkt aan de buitenunits van een airco"),
}
def photo_src(key, w, h):
    local = os.path.join(OUT, "assets", "img", key + ".jpg")
    if os.path.exists(local):
        return f"/assets/img/{key}.jpg"
    return f"https://images.unsplash.com/{PHOTOS[key][0]}?auto=format&fit=crop&w={w}&h={h}&q=72"
def photo_srcset(key, ratio):
    local = os.path.join(OUT, "assets", "img", key + ".jpg")
    if os.path.exists(local):
        # Responsieve varianten voor mobiel/tablet: kleinere bestanden = snellere pagina
        try:
            from PIL import Image
            im = Image.open(local)
            parts = []
            for w in (480, 800, 1200):
                if w >= im.width: continue
                dst = os.path.join(OUT, "assets", "img", f"{key}-{w}.jpg")
                if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(local):
                    im.convert("RGB").resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(dst, quality=80, optimize=True, progressive=True)
                parts.append(f"/assets/img/{key}-{w}.jpg {w}w")
            parts.append(f"/assets/img/{key}.jpg {im.width}w")
            return 'srcset="' + ", ".join(parts) + '"'
        except ImportError:
            return ""
    return 'srcset="' + ", ".join(f"{photo_src(key, w, int(w*ratio))} {w}w" for w in (640, 960, 1400, 1920)) + '"'

def media(src, alt, ph, eager=False, w=1200, h=800):
    key = src.rsplit(".", 1)[0]
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    if key in PHOTOS:
        r = h / w
        return (f'<div class="media"><img src="{photo_src(key, w, h)}" {photo_srcset(key, r)} '
                f'sizes="(max-width: 760px) 100vw, 50vw" alt="{PHOTOS[key][1]}" width="{w}" height="{h}" {load}></div>')
    return f'<div class="media"><img src="/assets/img/{src}" alt="{alt}" width="{w}" height="{h}" {load}></div>'

def hero_img():
    return (f'<img class="hero-bg" src="{photo_src("hero-woning", 1920, 1080)}" {photo_srcset("hero-woning", 0.5625)} '
            f'sizes="100vw" alt="{PHOTOS["hero-woning"][1]}" width="1408" height="768" fetchpriority="high">')

def crumbs(items):
    lis = ""
    for i, (name, url) in enumerate(items):
        if i < len(items) - 1:
            lis += f'<li><a href="{url}">{name}</a></li>'
        else:
            lis += f'<li aria-current="page">{name}</li>'
    return f'<nav class="crumbs" aria-label="Kruimelpad"><ol>{lis}</ol></nav>'

def crumbs_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + (u if u != "/" else "/")} for i, (n, u) in enumerate(items)]}

def faq_html(qa):
    return '<div class="faq">' + "".join(
        f'<details><summary>{q}</summary><div class="answer">{a}</div></details>' for q, a in qa) + '</div>'

def faq_schema(qa):
    import re
    strip = lambda s: re.sub(r"<[^>]+>", "", s).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]}

ORG = {
    "@context": "https://schema.org", "@type": "Electrician", "@id": BASE + "/#bedrijf",
    "name": "AT Energy Solutions", "url": BASE + "/", "email": EMAIL,
    "logo": {"@type": "ImageObject", "url": BASE + "/assets/logo.png", "width": 422, "height": 112}, "image": BASE + "/assets/og-image.jpg",
    "foundingDate": "2006", "slogan": "Zelf stroom maken, opslaan en slim gebruiken.",
    "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "Erkenning", "name": "InstallQ-erkend installateur elektrotechniek en zonnestroom"}, {"@type": "EducationalOccupationalCredential", "credentialCategory": "Certificaat", "name": "BRL 200"}],
    "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "email": EMAIL, "areaServed": "NL", "availableLanguage": ["nl"]},
    "description": "Al 20 jaar actief in elektra en verduurzaming. InstallQ-erkend elektra- en zonnestroominstallateur uit Nieuwerkerk aan den IJssel voor zonnepanelen, thuisbatterijen, warmtepompen en airco's, voor particulieren en bedrijven.",
    "identifier": {"@type": "PropertyValue", "propertyID": "KvK-nummer", "value": KVK},
    "address": {"@type": "PostalAddress", "streetAddress": "Hoofdweg Noord 11", "postalCode": "2913 LB",
                "addressLocality": "Nieuwerkerk aan den IJssel", "addressRegion": "Zuid-Holland", "addressCountry": "NL"},
    "hasMap": "https://www.google.com/maps/search/?api=1&query=Hoofdweg+Noord+11%2C+2913+LB+Nieuwerkerk+aan+den+IJssel",
    "areaServed": [{"@type": "City", "name": "Nieuwerkerk aan den IJssel"}, {"@type": "AdministrativeArea", "name": "Gemeente Zuidplas"}, {"@type": "Country", "name": "Nederland"}],
    "knowsAbout": ["Zonnepanelen", "Thuisbatterijen", "Warmtepompen", "Airconditioning", "Elektrotechnische installaties"],
    # TODO: voeg 'telephone' toe zodra bevestigd, en 'sameAs' met links naar Google Bedrijfsprofiel/LinkedIn.
}
WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#website", "name": "AT Energy Solutions", "url": BASE + "/", "inLanguage": "nl-NL", "publisher": {"@id": BASE + "/#bedrijf"}}

def service_schema(name, desc, path):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc,
            "serviceType": name, "url": BASE + path, "areaServed": {"@type": "Country", "name": "Nederland"},
            "provider": {"@id": BASE + "/#bedrijf"}}

OG_IMAGE = BASE + "/assets/og-image.jpg"
AUTHOR = "Redactie AT Energy Solutions"
fmt = lambda d: date.fromisoformat(d).strftime("%-d %B %Y").replace("January","januari").replace("February","februari").replace("March","maart").replace("April","april").replace("May","mei").replace("June","juni").replace("July","juli").replace("August","augustus").replace("September","september").replace("October","oktober").replace("November","november").replace("December","december")

# ---------- Layout ----------
PRODUCTS = [("Zonnepanelen", "/zonnepanelen", "Zelf stroom opwekken"), ("Thuisbatterij", "/thuisbatterij", "Zonnestroom bewaren"),
            ("Warmtepomp", "/warmtepomp", "Duurzaam verwarmen"), ("Airco", "/airco", "Koelen en bijverwarmen")]
NAV = [("Home", "/"), ("Zakelijk", "/zakelijk"), ("Over ons", "/over-ons"), ("Kennisbank", "/kennisbank"), ("Veelgestelde vragen", "/veelgestelde-vragen"), ("Contact", "/contact")]

def header(current):
    cur = lambda u: ' aria-current="page"' if current == u else ""
    prod_active = current == "/producten"
    subs = "".join(f'<li><a href="{u}"{cur(u)}><strong>{n}</strong><span>{d}</span></a></li>' for n, u, d in PRODUCTS)
    subs += '<li class="sub-all"><a href="/producten">Alle producten bekijken</a></li>'
    home, rest = NAV[0], NAV[1:]
    items = f'<li><a href="{home[1]}"{cur(home[1])}>{home[0]}</a></li>'
    items += (f'<li class="has-sub"><button class="sub-toggle{" is-active" if prod_active else ""}" type="button" aria-expanded="false" aria-controls="sub-producten">Producten'
              f'<svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>'
              f'<ul id="sub-producten" class="sub">{subs}</ul></li>')
    items += "".join(f'<li><a href="{u}"{cur(u)}>{n}</a></li>' for n, u in rest)
    phone = f'<a href="tel:{PHONE.replace(" ", "")}">{PHONE}</a>' if PHONE else ""
    return f'''<a class="skip" href="#inhoud">Naar de inhoud</a>
<div class="topbar"><div class="wrap topbar-in">
  <ul class="topbar-usp"><li>Al 20 jaar actief in elektra en verduurzaming</li><li>InstallQ-erkend elektra- en zonnestroominstallateur</li><li>BRL 200-gecertificeerd</li></ul>
  <div class="topbar-contact">{phone}<a href="mailto:{EMAIL}">{EMAIL}</a></div>
</div></div>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="/" aria-label="AT Energy Solutions, naar de homepage"><img src="/assets/logo.png" alt="AT Energy Solutions" width="422" height="112"></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-menu" aria-label="Menu openen"><span></span></button>
    <nav id="nav-menu" class="nav-menu" aria-label="Hoofdmenu">
      <ul class="nav-list">{items}
        <li class="nav-cta-li"><a class="btn btn--mint nav-cta" href="/contact">Offerte aanvragen</a></li>
      </ul>
    </nav>
  </div>
</header>'''

def footer():
    return f'''<div class="mobile-cta" role="region" aria-label="Snel contact"><a class="btn btn--mint" href="/contact">Offerte aanvragen</a><a class="btn btn--line" href="mailto:{EMAIL}">Mail ons</a></div>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <a class="brand" href="/" aria-label="AT Energy Solutions, naar de homepage"><img src="/assets/logo-white.png" alt="AT Energy Solutions" width="422" height="112" loading="lazy"></a>
        <p>Al 20 jaar actief in elektra en verduurzaming. InstallQ-erkend elektra- en zonnestroominstallateur, vanuit Nieuwerkerk aan den IJssel.</p>
      </div>
      <div>
        <h2>Producten</h2>
        <ul><li><a href="/zonnepanelen">Zonnepanelen</a></li><li><a href="/thuisbatterij">Thuisbatterij</a></li><li><a href="/warmtepomp">Warmtepomp</a></li><li><a href="/airco">Airco</a></li><li><a href="/zakelijk">Zakelijk</a></li></ul>
      </div>
      <div>
        <h2>Bedrijf</h2>
        <ul><li><a href="/over-ons">Over ons</a></li><li><a href="/kennisbank">Kennisbank</a></li><li><a href="/veelgestelde-vragen">Veelgestelde vragen</a></li><li><a href="/installateur-nieuwerkerk-aan-den-ijssel">Werkgebied</a></li><li><a href="/contact">Contact</a></li></ul>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          {PHONE_LI}
          <li>{PH_ADDR}</li>
          <li>KvK {KVK}</li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <p class="mb-0">© {date.today().year} AT Energy Solutions</p>
      <ul><li><a href="/privacyverklaring">Privacy</a></li><li><a href="/cookieverklaring">Cookies</a></li><li><a href="/algemene-voorwaarden">Algemene voorwaarden</a></li></ul>
    </div>
  </div>
</footer>'''

def cta(title="Benieuwd wat past bij jouw situatie?", text="Vertel ons kort over je woning of bedrijfspand. We nemen contact op om je situatie door te nemen en sturen daarna een offerte op maat.", dark=False):
    return f'''<section class="sec--tight" aria-labelledby="cta-t"><div class="wrap">
  <div class="cta-panel">
    <div><h2 id="cta-t">{title}</h2><p>{text}</p></div>
    <div class="btn-row"><a class="btn btn--ink" href="/contact">Offerte aanvragen</a><a class="btn btn--line" href="mailto:{EMAIL}">Mail ons</a></div>
  </div>
</div></section>'''

PAGE_TYPES = {"/contact": "ContactPage", "/over-ons": "AboutPage", "/veelgestelde-vragen": "FAQPage", "/kennisbank": "CollectionPage", "/producten": "CollectionPage"}
def page(path, title, desc, body, current=None, schema=None, noindex=False, og_type="website"):
    url = BASE + (path if path != "/" else "/")
    remote = "unsplash" in body
    preload = ('\n<link rel="preconnect" href="https://images.unsplash.com" crossorigin>' if remote else "")
    if path == "/":
        preload += f'\n<link rel="preload" as="image" href="{photo_src("hero-woning", 1920, 1080)}" imagesrcset="{photo_srcset("hero-woning", 0.5625)[8:-1]}" imagesizes="100vw" fetchpriority="high">'
    if not noindex:
        wp = {"@context": "https://schema.org", "@type": PAGE_TYPES.get(path, "WebPage"), "@id": url + "#webpage", "url": url,
              "name": title, "description": desc, "inLanguage": "nl-NL", "dateModified": TODAY,
              "isPartOf": {"@id": BASE + "/#website"}, "publisher": {"@id": BASE + "/#bedrijf"}}
        if PAGE_TYPES.get(path) != "FAQPage":
            schema = [wp] + list(schema or [])
    full_title = title if ("AT Energy" in title or len(title) > 53) else f"{title} | AT Energy"
    ld = "".join(f'\n<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in (schema or []))
    robots = '<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    doc = f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="nl_NL">
<meta property="og:site_name" content="AT Energy Solutions">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1C2124">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" hreflang="nl-NL" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="author" content="AT Energy Solutions">
<meta name="geo.region" content="NL-ZH">
<meta name="geo.placename" content="Nieuwerkerk aan den IJssel">{preload}
<link rel="stylesheet" href="/assets/css/style.css">
<script src="/assets/js/main.js" defer></script>
<!-- Google Search Console: plaats hier de verificatie-metatag OF verifieer via DNS (aanbevolen). -->{ld}
</head>
<body>
{header(current)}
<main id="inhoud">
{body}
</main>
{footer()}
</body>
</html>
'''
    rel = "index.html" if path == "/" else path.strip("/") + ".html"
    fp = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(doc)
    PAGES.append((path, noindex))

# ---------- Homepage ----------
DAYCURVE = '''<figure class="daycurve">
  <svg viewBox="0 0 600 270" role="img" aria-labelledby="dc-t dc-d">
    <title id="dc-t">Illustratie: zonne-opwek en stroomverbruik op een zonnige dag</title>
    <desc id="dc-d">Overdag wekken zonnepanelen meer op dan het huis verbruikt; dat overschot gaat de thuisbatterij in. In de avond, als het verbruik piekt, levert de batterij die stroom weer aan het huis.</desc>
    <g stroke="#3A4246" stroke-width="1"><line x1="30" y1="225" x2="580" y2="225"/></g>
    <g fill="#A9B3B6" font-size="18"><text x="70" y="252">06</text><text x="286" y="252">12</text><text x="490" y="252">18</text><text x="556" y="252">22</text></g>
    <path class="dc-fill" d="M80 225 C170 225 215 45 300 45 C385 45 430 225 520 225 Z" fill="#2ED3C6" fill-opacity=".16"/>
    <path class="dc-sun" d="M80 225 C170 225 215 45 300 45 C385 45 430 225 520 225" fill="none" stroke="#2ED3C6" stroke-width="4" stroke-linecap="round"/>
    <path class="dc-use" d="M30 185 C90 180 115 160 150 165 C210 175 250 188 300 188 C355 188 395 178 440 125 C470 92 505 98 580 160" fill="none" stroke="#F8F7F3" stroke-width="3" stroke-linecap="round"/>
    <g class="dc-label" font-size="19" font-weight="700">
      <text x="300" y="150" text-anchor="middle" fill="#2ED3C6">Overschot naar batterij</text>
      <text x="440" y="70" fill="#F8F7F3">Batterij levert</text>
      <text x="440" y="93" fill="#F8F7F3">’s avonds</text>
    </g>
  </svg>
  <figcaption>Illustratief voorbeeld, geen meetgegevens. Groen: opwek. Wit: verbruik.</figcaption>
</figure>'''

home_faq = [
 ("Wat verandert er als de salderingsregeling stopt?", "<p>Vanaf 1 januari 2027 mag je teruggeleverde zonnestroom niet meer wegstrepen tegen de stroom die je afneemt. Je krijgt dan een terugleververgoeding van je energieleverancier. Stroom die je zelf direct gebruikt of opslaat, wordt daardoor relatief waardevoller. Lees meer in <a class=\"link\" href=\"/kennisbank/salderingsregeling-stopt\">ons artikel over het einde van de salderingsregeling</a>.</p>"),
 ("Werken jullie ook voor bedrijven?", "<p>Ja. We installeren voor particulieren en voor bedrijven, van een zonnestroominstallatie op een bedrijfsdak tot het aanpassen van de elektrische installatie. Bekijk <a class=\"link\" href=\"/zakelijk\">onze zakelijke oplossingen</a>.</p>"),
 ("Kan ik meerdere oplossingen combineren?", "<p>Ja, en vaak is dat juist verstandig. Zonnepanelen, een thuisbatterij en een warmtepomp of airco beïnvloeden elkaar. Omdat we zelf elektrotechnisch installateur zijn, bekijken we ook of je meterkast en aansluiting het geheel aankunnen.</p>"),
 ("Hoe snel kunnen jullie installeren?", f"<p>Dat hangt af van de oplossing, de beschikbaarheid van materialen en de planning op dat moment. Je hoort de verwachte installatiedatum bij de offerte.</p>"),
]

ADDR_LINE = "Hoofdweg Noord 11, 2913 LB Nieuwerkerk aan den IJssel"
MAPS = "https://www.google.com/maps/search/?api=1&query=Hoofdweg+Noord+11%2C+2913+LB+Nieuwerkerk+aan+den+IJssel"
Q = {
 "sun": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="5" y="12" width="22" height="14" rx="2"/><path d="M5 19h22M12.3 12v14M19.7 12v14M16 3v4M9 5l1.5 2.5M23 5l-1.5 2.5"/></svg>',
 "bat": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="5" width="16" height="24" rx="3"/><path d="M13 3h6M17 11l-3 6h4l-3 6"/></svg>',
 "heat": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="3" y="7" width="26" height="18" rx="3"/><circle cx="20" cy="16" r="5.5"/><path d="M20 10.5v11M14.5 16h11M7 12h4M7 16h4M7 20h4"/></svg>',
 "air": '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="3" y="7" width="26" height="10" rx="3"/><path d="M7 13h18M10 21c0 2-2 2-2 4M16 21v4M22 21c0 2 2 2 2 4"/></svg>',
}
DAYCURVE_STATIC = DAYCURVE.replace('<figure class="daycurve">', '<figure class="daycurve daycurve--static">').replace("Groen: opwek.", "Turquoise: opwek.")

REVIEW_BLOCK = (f'<figure class="quote"><blockquote><p class="mb-0">{REVIEWS[0][0]}</p></blockquote><figcaption>{REVIEWS[0][1]}, {REVIEWS[0][2]}</figcaption></figure>' if REVIEWS else
  '<div class="quote"><p class="quote-lead">Erkend door InstallQ</p><p>InstallQ beheert de erkenningsregelingen in de installatiebranche. Met een erkenning laat een installateur zien dat hij voldoet aan eisen voor vakmanschap en kwaliteit. Wij zijn erkend voor elektrotechniek en zonnestroom, en hebben daarnaast een BRL 200-certificaat.</p><a class="link" href="https://www.installq.nl" rel="noopener" target="_blank">Meer over InstallQ</a></div>')
home = f'''<div class="hero-shell"><section class="hero-photo" aria-labelledby="hero-t">
  {hero_img()}
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <h1 id="hero-t">Zelf stroom maken, opslaan en slim gebruiken.</h1>
      <p class="lead">Al 20 jaar actief in elektra en verduurzaming. Als InstallQ-erkend elektra- en zonnestroominstallateur installeren we zonnepanelen, thuisbatterijen, warmtepompen en airco’s voor woningen en bedrijven in Nieuwerkerk aan den IJssel en omgeving.</p>
      <div class="btn-row">
        <a class="btn btn--mint" href="/contact">Vraag een offerte aan</a>
        <a class="btn btn--glass" href="/producten">Bekijk onze producten</a>
      </div>
    </div>
  </div>
</section></div>

<section class="quick-wrap" aria-label="Kies een oplossing">
  <div class="wrap">
    <ul class="quick">
      <li><a href="/zonnepanelen"><span class="q-ico">{Q["sun"]}</span><span><strong>Zonnepanelen</strong><span>Zelf stroom opwekken</span></span></a></li>
      <li><a href="/thuisbatterij"><span class="q-ico">{Q["bat"]}</span><span><strong>Thuisbatterij</strong><span>Zonnestroom bewaren</span></span></a></li>
      <li><a href="/warmtepomp"><span class="q-ico">{Q["heat"]}</span><span><strong>Warmtepomp</strong><span>Duurzaam verwarmen</span></span></a></li>
      <li><a href="/airco"><span class="q-ico">{Q["air"]}</span><span><strong>Airco</strong><span>Koelen en bijverwarmen</span></span></a></li>
    </ul>
  </div>
</section>

<section class="sec-band" aria-labelledby="exp-t">
  <div class="wrap exp">
    <div class="exp-years" aria-hidden="true"><span>20</span>jaar</div>
    <div class="exp-text">
      <h2 id="exp-t">Al 20 jaar actief in elektra en verduurzaming</h2>
      <p>Twintig jaar ervaring met elektrische installaties en duurzame energie. Die ervaring zit in elk project: van een nieuwe groep in de meterkast tot een complete installatie met zonnepanelen, batterij en warmtepomp.</p>
    </div>
    <ul class="exp-creds">
      <li><strong>InstallQ-erkend</strong><span>Elektra- en zonnestroominstallateur</span></li>
      <li><strong>BRL 200</strong><span>Gecertificeerd</span></li>
      <li><strong>Particulier én zakelijk</strong><span>Woningen en bedrijfspanden</span></li>
    </ul>
  </div>
</section>

<section class="sec sec--alt" aria-labelledby="svc-t">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="svc-t">Alles voor een duurzaam huis, van één installateur</h2>
      <p class="lead muted">Elk onderdeel werkt los, maar samen haal je er het meeste uit. Wij ontwerpen het als één systeem, inclusief de meterkast.</p>
    </div>
    <ul class="cards">
      <li><a class="card" href="/zonnepanelen">{media("zonnepanelen.svg", "Illustratie van zonnepanelen op een pannendak", "zonnepanelen op dak")}<div class="card-body"><h3>Zonnepanelen</h3><p>Stroom opwekken op je eigen dak, met een ontwerp dat past bij je dakvlak, schaduw en verbruik.</p><span class="link">Over zonnepanelen</span></div></a></li>
      <li><a class="card" href="/thuisbatterij">{media("thuisbatterij.svg", "Illustratie van een thuisbatterij met omvormer naast de meterkast", "thuisbatterij in woning")}<div class="card-body"><h3>Thuisbatterij</h3><p>Overdag opgewekte stroom bewaren en ’s avonds zelf gebruiken. Extra relevant nu de salderingsregeling stopt.</p><span class="link">Over thuisbatterijen</span></div></a></li>
      <li><a class="card" href="/warmtepomp">{media("warmtepomp.svg", "Illustratie van de buitenunit van een warmtepomp tegen een bakstenen gevel", "buitenunit warmtepomp")}<div class="card-body"><h3>Warmtepomp</h3><p>Verwarmen met warmte uit de buitenlucht, hybride naast je cv-ketel of volledig elektrisch.</p><span class="link">Over warmtepompen</span></div></a></li>
      <li><a class="card" href="/airco">{media("airco.svg", "Illustratie van een airco boven een bank in een woonkamer", "binnenunit airco")}<div class="card-body"><h3>Airco</h3><p>Koelen in de zomer en efficiënt bijverwarmen in het voor- en najaar, per ruimte geregeld.</p><span class="link">Over airco’s</span></div></a></li>
    </ul>
  </div>
</section>

<section class="sec sec--dark" aria-labelledby="dc-h">
  <div class="wrap band">
    <div>
      <h2 id="dc-h">Na 2027 telt elke zelf gebruikte kilowattuur</h2>
      <p class="lead muted">Op 1 januari 2027 stopt de salderingsregeling. Zonnestroom die je teruglevert, levert dan minder op dan stroom die je inkoopt. Een thuisbatterij bewaart je overschot van overdag voor de avond.</p>
      <div class="btn-row mt-2"><a class="btn btn--mint" href="/thuisbatterij">Meer over thuisbatterijen</a><a class="btn btn--line" href="/kennisbank/salderingsregeling-stopt">Wat verandert er?</a></div>
    </div>
    {DAYCURVE_STATIC}
  </div>
</section>

<section class="sec" aria-labelledby="why-t">
  <div class="wrap split">
    <div>
      <h2 id="why-t">Installateur, niet alleen verkoper</h2>
      <p class="lead muted">Als elektrotechnisch installateur kijken we verder dan het product alleen. Eerst de installatie goed, dan de rest.</p>
      <a class="btn btn--ink mt-2" href="/over-ons">Over AT Energy Solutions</a>
    </div>
    <ul class="reasons">
      <li>{I["shield"]}<div><h3>InstallQ-erkend elektra- en zonnestroominstallateur</h3><p>Onze erkenning laat zien dat we voldoen aan de eisen voor vakmanschap en kwaliteit in elektrotechniek en zonnestroom. Daarnaast zijn we BRL 200-gecertificeerd.</p></div></li>
      <li>{I["plug"]}<div><h3>De meterkast hoort erbij</h3><p>Een batterij, warmtepomp of laadpunt vraagt iets van je elektrische installatie. Dat beoordelen en regelen we zelf, zonder extra partij.</p></div></li>
      <li>{I["grow"]}<div><h3>Al 20 jaar in elektra en verduurzaming</h3><p>Twintig jaar ervaring met elektrische installaties en duurzame energie, voor particuliere én zakelijke klanten.</p></div></li>
      <li>{I["talk"]}<div><h3>Advies dat bij je situatie past</h3><p>We kijken naar je verbruik, je dak en je plannen, en adviseren alleen wat daar zinvol bij is.</p></div></li>
    </ul>
  </div>
</section>

<section class="sec sec--dark" aria-labelledby="how-t">
  <div class="wrap">
    <div class="sec-head"><h2 id="how-t">Zo verloopt het</h2><p class="muted">Van je eerste vraag tot een werkende installatie.</p></div>
    <ol class="steps">
      <li><h3>Aanvraag</h3><p>Je vult het formulier in of mailt ons. Dat kost een paar minuten.</p></li>
      <li><h3>Kennismaking</h3><p>We bespreken je situatie, verbruik en wensen, telefonisch of bij je thuis.</p></li>
      <li><h3>Offerte op maat</h3><p>Je krijgt een concreet voorstel met de gekozen materialen en de planning.</p></li>
      <li><h3>Installatie</h3><p>We installeren en testen alles, en leggen uit hoe het werkt.</p></li>
      <li><h3>Nazorg</h3><p>Na oplevering blijven we je aanspreekpunt voor vragen en service.</p></li>
    </ol>
  </div>
</section>

<section class="sec" aria-labelledby="proof-t">
  <div class="wrap">
    <div class="sec-head"><h2 id="proof-t">Wat je van ons mag verwachten</h2></div>
    <div class="proof">
      {REVIEW_BLOCK}
      <ul class="certs" aria-label="Erkenningen en bedrijfsgegevens">
        <li><strong>InstallQ</strong><span>Erkend installateur elektra en zonnestroom</span></li>
        <li><strong>BRL 200</strong><span>Gecertificeerd</span></li>
        <li><strong>Ervaring</strong><span>20 jaar</span></li>
        <li><strong>KvK</strong><span>{KVK}</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="sec sec--alt" aria-labelledby="biz-t">
  <div class="wrap band">
    {media("zakelijk.svg", "Illustratie van een bedrijfspand met zonnepanelen op het platte dak", "zonnepanelen op bedrijfsdak")}
    <div>
      <h2 id="biz-t">Ook voor ondernemers in de regio</h2>
      <p class="lead muted">Een bedrijfsdak, een werkplaats met hoog stroomverbruik of een pand dat van het gas af moet. We denken mee over opwek, opslag en de capaciteit van je aansluiting.</p>
      <a class="btn btn--ink mt-2" href="/zakelijk">Bekijk zakelijke oplossingen</a>
    </div>
  </div>
</section>

<section class="sec" aria-labelledby="loc-t">
  <div class="wrap local">
    <div>
      <h2 id="loc-t">Gevestigd in Nieuwerkerk aan den IJssel</h2>
      <p class="lead muted">Vanuit onze vestiging aan de Hoofdweg Noord werken we voor huishoudens en bedrijven in Nieuwerkerk aan den IJssel en omgeving.</p>
      <a class="link" href="/installateur-nieuwerkerk-aan-den-ijssel">Over ons werkgebied</a>
    </div>
    <address class="addr-card">
      <strong>AT Energy Solutions</strong><br>
      Hoofdweg Noord 11<br>2913 LB Nieuwerkerk aan den IJssel<br>
      <a class="link" href="mailto:{EMAIL}">{EMAIL}</a><br>
      <a class="link" href="{MAPS}" rel="noopener" target="_blank">Route in Google Maps</a>
    </address>
  </div>
</section>

<section class="sec sec--alt" aria-labelledby="faq-t">
  <div class="wrap">
    <div class="sec-head"><h2 id="faq-t">Veelgestelde vragen</h2></div>
    {faq_html(home_faq)}
    <p class="mt-2"><a class="link" href="/veelgestelde-vragen">Alle veelgestelde vragen</a></p>
  </div>
</section>
{cta()}'''
page("/", "Zonnepanelen en thuisbatterij in Nieuwerkerk | AT Energy",
     "InstallQ-erkend installateur van zonnepanelen, thuisbatterijen, warmtepompen en airco’s in Nieuwerkerk aan den IJssel e.o. 20 jaar ervaring. Vraag een offerte aan.",
     home, current="/", schema=[ORG, WEBSITE, faq_schema(home_faq)])

# ---------- Dienstpagina's ----------
SERVICES = {
 "zonnepanelen": dict(
  name="Zonnepanelen", img="zonnepanelen.svg", alt="Illustratie van zonnepanelen op een pannendak", ph="zonnepanelen op dak",
  title="Zonnepanelen laten installeren", desc="Zonnepanelen laten plaatsen door een InstallQ-erkend installateur. Ontwerp op maat van je dak en verbruik, aansluiting in de meterkast geregeld.",
  h1="Zonnepanelen, ontworpen voor jouw dak", lead="Hoeveel je opwekt, hangt af van je dakvlak, de ligging, schaduw en de gekozen techniek. We ontwerpen de installatie daarop en sluiten alles veilig aan op je meterkast.",
  facts=[("Ontwerp op maat", "We bekijken oriëntatie, hellingshoek, schaduw en de draagkracht van je dak voordat we een indeling voorstellen."),
         ("Juiste omvormer", "Een centrale omvormer, optimizers of micro-omvormers: de keuze hangt af van schaduw en dakvorm."),
         ("Netjes aangesloten", "Een aparte groep in de meterkast en, waar nodig, aanpassingen aan je installatie.")],
  body=f'''<h2>Hoe zonnepanelen werken</h2>
<p>Zonnepanelen zetten zonlicht om in gelijkstroom. Een omvormer maakt daar wisselstroom van, die je in huis direct kunt gebruiken. Wat je op dat moment niet verbruikt, gaat naar het net of naar een thuisbatterij.</p>
<h2>Waar we op letten</h2>
<ul><li><strong>Dak en constructie:</strong> pannendak, plat dak of staaldak vraagt elk een ander montagesysteem.</li>
<li><strong>Schaduw:</strong> een schoorsteen of boom kan de opbrengst van een hele reeks panelen drukken. Optimizers of micro-omvormers kunnen dan uitkomst bieden.</li>
<li><strong>Je verbruik nu en straks:</strong> plan je een warmtepomp, airco of elektrische auto, dan houden we daar rekening mee.</li>
<li><strong>Meterkast:</strong> we controleren of er ruimte is voor een extra groep en of je installatie in orde is.</li></ul>
<h2>Btw en saldering</h2>
<p>Voor zonnepanelen op of bij woningen geldt sinds 1 januari 2023 een btw-nultarief op levering en installatie. De salderingsregeling stopt op 1 januari 2027. Daarna wordt zelf verbruiken of opslaan van je zonnestroom belangrijker. <a href="/kennisbank/salderingsregeling-stopt">Lees wat dat voor je betekent</a>.</p>
<h2>Na de installatie</h2>
<p>We testen de installatie, laten je zien hoe je de opbrengst volgt en melden je installatie aan via energieleveren.nl, of helpen je daarbij.</p>''',
  faq=[("Is mijn dak geschikt voor zonnepanelen?", "<p>De meeste daken zijn geschikt, maar oriëntatie, schaduw en constructie bepalen hoeveel je opwekt. Dat beoordelen we bij de kennismaking, eventueel op basis van foto’s en luchtbeelden.</p>"),
       ("Hoeveel zonnepanelen heb ik nodig?", "<p>Dat hangt af van je jaarverbruik, je beschikbare dakoppervlak en je toekomstplannen. We rekenen het voor je situatie uit in de offerte.</p>"),
       ("Moet ik mijn zonnepanelen aanmelden?", "<p>Ja. Zonnepanelen meld je aan bij je netbeheerder via energieleveren.nl. We helpen je daarbij.</p>")]),
 "thuisbatterij": dict(
  name="Thuisbatterij", img="thuisbatterij.svg", alt="Illustratie van een thuisbatterij met omvormer naast de meterkast", ph="thuisbatterij in woning",
  title="Thuisbatterij laten installeren", desc="Thuisbatterij bij je zonnepanelen: bewaar zonnestroom voor de avond nu de salderingsregeling stopt. Advies, plaatsing en aansluiting door een erkend installateur.",
  h1="Je zonnestroom bewaren voor de avond", lead="Zonnepanelen leveren het meest rond het middaguur, terwijl je de meeste stroom ’s avonds gebruikt. Een thuisbatterij overbrugt dat verschil.",
  facts=[("Passende capaciteit", "We kijken naar je opwek en verbruik, zodat je niet betaalt voor capaciteit die je niet gebruikt."),
         ("Veilig geplaatst", "Een geschikte plek met voldoende ventilatie, volgens de voorschriften van de fabrikant."),
         ("Slim aangestuurd", "Afhankelijk van de batterij kun je laden en ontladen afstemmen op je energiecontract.")],
  body='''<h2>Waarom een thuisbatterij nu</h2>
<p>Tot en met 2026 mag je teruggeleverde stroom nog salderen. Vanaf 1 januari 2027 stopt die regeling. Teruggeleverde stroom levert dan een lagere vergoeding op dan wat je betaalt voor stroom van het net, en veel leveranciers rekenen terugleverkosten. Zelf opgewekte stroom opslaan en later gebruiken wordt daardoor interessanter.</p>
<div class="note"><p>Of een batterij voor jou rendabel is, hangt af van je opwek, verbruikspatroon en energiecontract. We rekenen dat eerlijk voor je door in plaats van een vast besparingspercentage te beloven.</p></div>
<h2>Soorten aansluitingen</h2>
<ul><li><strong>Hybride omvormer:</strong> één omvormer voor panelen en batterij. Logisch bij een nieuwe installatie of als je omvormer aan vervanging toe is.</li>
<li><strong>AC-gekoppelde batterij:</strong> een batterij met eigen omvormer naast je bestaande zonnepanelen. Je bestaande installatie blijft dan ongewijzigd.</li></ul>
<h2>Waar we op letten</h2>
<ul><li>De plaatsingslocatie: temperatuur, ventilatie en bereikbaarheid.</li>
<li>De capaciteit van je meterkast en hoofdaansluiting.</li>
<li>Of de batterij kan samenwerken met je bestaande omvormer en eventuele warmtepomp.</li></ul>''',
  faq=[("Kan ik een thuisbatterij bij mijn bestaande zonnepanelen laten plaatsen?", "<p>Meestal wel. Met een AC-gekoppelde batterij hoeft je bestaande installatie niet aangepast te worden. Is je omvormer oud, dan kan een hybride omvormer handiger zijn.</p>"),
       ("Hoe groot moet mijn thuisbatterij zijn?", "<p>Dat hangt af van hoeveel stroom je overdag overhoudt en ’s avonds gebruikt. Te groot is zonde van het geld, te klein benut je overschot niet. We berekenen het op basis van je verbruik.</p>"),
       ("Waar wordt een thuisbatterij geplaatst?", "<p>Meestal in een berging, bijkeuken, garage of meterkastruimte. De fabrikant schrijft voor welke temperatuur en ventilatie nodig is; we kiezen daar samen een geschikte plek op.</p>")]),
 "warmtepomp": dict(
  name="Warmtepomp", img="warmtepomp.svg", alt="Illustratie van de buitenunit van een warmtepomp tegen een bakstenen gevel", ph="buitenunit warmtepomp",
  title="Warmtepomp laten installeren", desc="Hybride of volledig elektrische warmtepomp. Advies over isolatie, afgiftesysteem en aansluiting door een InstallQ-erkend installateur.",
  h1="Verwarmen met warmte uit de buitenlucht", lead="Een warmtepomp haalt warmte uit de buitenlucht en verwarmt daarmee je huis. Welke soort past, hangt vooral af van de isolatie en het afgiftesysteem van je woning.",
  facts=[("Hybride of all-electric", "Een hybride warmtepomp werkt samen met je cv-ketel. Een volledig elektrische vervangt hem."),
         ("Eerst de woning", "Isolatie en radiatoren of vloerverwarming bepalen hoe efficiënt een warmtepomp werkt."),
         ("Elektrisch op orde", "Een warmtepomp vraagt een eigen groep en soms een zwaardere aansluiting. Dat regelen we zelf.")],
  body='''<h2>Hybride of volledig elektrisch?</h2>
<p>Een <strong>hybride warmtepomp</strong> neemt het grootste deel van de verwarming over en laat de cv-ketel bijspringen op koude dagen en voor warm tapwater. Dat werkt ook in matig geïsoleerde woningen. Een <strong>volledig elektrische warmtepomp</strong> vervangt de cv-ketel helemaal. Daarvoor moet de woning goed geïsoleerd zijn en geschikt zijn voor verwarmen op lage temperatuur. <a href="/kennisbank/hybride-of-volledige-warmtepomp">Lees het verschil uitgebreid</a>.</p>
<h2>Waar we op letten</h2>
<ul><li><strong>Isolatie en afgifte:</strong> kunnen je radiatoren of vloerverwarming de woning warm krijgen met lagere watertemperatuur?</li>
<li><strong>Plaatsing buitenunit:</strong> een plek met voldoende luchtstroom, met oog voor geluid richting buren en de geldende regels.</li>
<li><strong>Elektrische installatie:</strong> een aparte groep, en soms een verzwaring van de aansluiting.</li>
<li><strong>Combinatie met zonnepanelen:</strong> eigen zonnestroom gebruiken voor de warmtepomp.</li></ul>
<h2>Subsidie</h2>
<p>Voor warmtepompen is vaak subsidie mogelijk via de ISDE-regeling van de Rijksdienst voor Ondernemend Nederland (RVO). Bedragen en voorwaarden wijzigen periodiek; kijk voor de actuele situatie op rvo.nl. We vermelden in de offerte of het voorgestelde toestel op de meldcodelijst staat.</p>''',
  faq=[("Is mijn huis geschikt voor een warmtepomp?", "<p>Voor een hybride warmtepomp zijn de meeste woningen geschikt. Voor een volledig elektrische warmtepomp is goede isolatie nodig. We beoordelen dit bij de kennismaking.</p>"),
       ("Maakt een warmtepomp geluid?", "<p>De buitenunit maakt geluid, vooral bij hoge belasting. Daarom kiezen we zorgvuldig de plaats en houden we rekening met de afstand tot buren en de geldende geluidsregels.</p>"),
       ("Krijg ik subsidie op een warmtepomp?", "<p>Vaak wel, via de ISDE-regeling van RVO. Voorwaarden en bedragen veranderen, dus check rvo.nl voor de actuele situatie.</p>")]),
 "airco": dict(
  name="Airco", img="airco.svg", alt="Illustratie van een airco boven een bank in een woonkamer", ph="binnenunit airco",
  title="Airco laten installeren", desc="Airco laten installeren voor koelen en bijverwarmen. Split-unit of multi-split, netjes weggewerkt en aangesloten op een eigen groep.",
  h1="Koel in de zomer, comfortabel in het tussenseizoen", lead="Een moderne airco koelt niet alleen. Het is een lucht-lucht-warmtepomp die ook efficiënt kan bijverwarmen, per ruimte geregeld.",
  facts=[("Per ruimte", "Een split-unit voor één ruimte of een multi-split voor meerdere ruimtes op één buitenunit."),
         ("Netjes weggewerkt", "Leidingen en afvoer zoveel mogelijk uit het zicht, met aandacht voor de afwerking."),
         ("Eigen groep", "Aangesloten op een aparte groep in de meterkast, zodat je installatie niet overbelast raakt.")],
  body=f'''<h2>Koelen en verwarmen</h2>
<p>Een airco verplaatst warmte: in de zomer van binnen naar buiten, in de winter andersom. Daardoor is hij ook een efficiënte manier om bij te verwarmen, bijvoorbeeld in een zolderkamer of thuiswerkplek.</p>
<h2>Waar we op letten</h2>
<ul><li><strong>Capaciteit per ruimte:</strong> afgestemd op oppervlak, isolatie en zoninstraling.</li>
<li><strong>Plaats binnen- en buitenunit:</strong> goede luchtverdeling binnen, voldoende luchtstroom en beperkt geluid buiten.</li>
<li><strong>Afwerking:</strong> leidingen en condensafvoer zo kort en onopvallend mogelijk, met een nette doorvoer door de gevel.</li></ul>''',
  faq=[("Kan een airco ook verwarmen?", "<p>Ja. De meeste moderne airco’s zijn lucht-lucht-warmtepompen en kunnen efficiënt verwarmen, vooral in het voor- en najaar.</p>"),
       ("Hoeveel ruimtes kan ik op één buitenunit aansluiten?", "<p>Met een multi-split-systeem kunnen meerdere binnenunits op één buitenunit. Hoeveel precies, hangt af van het model en de benodigde capaciteit.</p>"),
       ("Heb ik toestemming nodig voor een buitenunit?", "<p>Vaak niet, maar in een appartementencomplex (VvE), bij een monument of bij plaatsing aan de voorgevel kunnen regels gelden. Check dit vooraf bij je VvE of gemeente.</p>")]),
}

SEO_TITLES = {"zonnepanelen": "Zonnepanelen laten plaatsen in Nieuwerkerk a/d IJssel", "thuisbatterij": "Thuisbatterij installeren in Nieuwerkerk a/d IJssel",
              "warmtepomp": "Warmtepomp installeren in Nieuwerkerk a/d IJssel", "airco": "Airco laten installeren in Nieuwerkerk a/d IJssel"}
TLDR = {
 "zonnepanelen": "AT Energy Solutions installeert zonnepanelen op pannendaken, platte daken en staaldaken in Nieuwerkerk aan den IJssel en omgeving. We ontwerpen de installatie op basis van je dak en verbruik, sluiten hem aan op een aparte groep in de meterkast en helpen bij de aanmelding. Voor woningen geldt een btw-nultarief; de salderingsregeling stopt op 1 januari 2027.",
 "thuisbatterij": "Een thuisbatterij slaat overdag opgewekte zonnestroom op, zodat je die ’s avonds zelf gebruikt. Na het einde van de salderingsregeling op 1 januari 2027 wordt dat interessanter. We bepalen de capaciteit op basis van je opwek en verbruik en plaatsen de batterij naast je bestaande installatie of met een hybride omvormer.",
 "warmtepomp": "Een lucht-water-warmtepomp verwarmt je huis met warmte uit de buitenlucht. Een hybride warmtepomp werkt samen met je cv-ketel en past in de meeste woningen; een volledig elektrische vraagt goede isolatie en verwarmen op lage temperatuur. Subsidie is vaak mogelijk via de ISDE-regeling van RVO.",
 "airco": "Een moderne airco is een lucht-lucht-warmtepomp die koelt én efficiënt bijverwarmt. We installeren split- en multi-split-systemen, afgestemd op de ruimte, netjes weggewerkt en aangesloten op een eigen groep in de meterkast.",
}
def tldr_box(text):
    return f'<section class="sec--tight pt-0" aria-labelledby="kort-t"><div class="wrap"><div class="tldr"><h2 id="kort-t">In het kort</h2><p>{text}</p></div></div></section>'

ORDER = ["zonnepanelen", "thuisbatterij", "warmtepomp", "airco"]
for slug in ORDER:
    s = SERVICES[slug]
    path = "/" + slug
    trail = [("Home", "/"), ("Producten", "/producten"), (s["name"], path)]
    facts = "".join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in s["facts"])
    others = "".join(f'<li><a href="/{o}">{SERVICES[o]["name"]}</a></li>' for o in ORDER if o != slug)
    body = f'''<section class="page-head"><div class="wrap">
  {crumbs(trail)}
  <div class="svc-hero">
    <div><h1>{s["h1"]}</h1><p class="lead">{s["lead"]}</p>
      <div class="btn-row mt-2"><a class="btn btn--ink" href="/contact">Vraag een offerte aan</a><a class="btn btn--line" href="#vragen">Veelgestelde vragen</a></div></div>
    {media(s["img"], s["alt"], s["ph"], eager=True)}
  </div>
</div></section>
{tldr_box(TLDR[slug])}
<section class="sec--tight" aria-label="Kernpunten"><div class="wrap"><ul class="facts">{facts}</ul></div></section>
<section class="sec pt-0"><div class="wrap"><div class="prose">{s["body"]}<p class="article-meta">Laatst bijgewerkt: <time datetime="{TODAY}">{fmt(TODAY)}</time>, door de redactie van AT Energy Solutions</p></div></div></section>
<section class="sec sec--alt" id="vragen" aria-labelledby="sfaq-t"><div class="wrap">
  <div class="sec-head"><h2 id="sfaq-t">Vragen over {s["name"].lower()}</h2></div>
  {faq_html(s["faq"])}
  <!--RELATED:{slug}-->
  <h2 class="mt-3 h-small">Combineer met</h2>
  <ul class="related">{others}<li><a href="/zakelijk">Zakelijke oplossingen</a></li></ul>
</div></section>
{cta()}'''
    page(path, SEO_TITLES[slug], s["desc"], body, current="/producten",
         schema=[service_schema(s["name"], s["desc"], path), crumbs_schema(trail), faq_schema(s["faq"])])

# ---------- Oplossingen ----------
sol_items = ""
short = {"zonnepanelen": "Stroom opwekken op je eigen dak, ontworpen voor je dakvlak en verbruik.",
         "thuisbatterij": "Zonnestroom bewaren voor de avond. Extra relevant nu de salderingsregeling stopt.",
         "warmtepomp": "Verwarmen met buitenlucht: hybride naast je cv-ketel of volledig elektrisch.",
         "airco": "Koelen en efficiënt bijverwarmen, per ruimte geregeld."}
for slug in ORDER:
    s = SERVICES[slug]
    sol_items += f'<li><a href="/{slug}">{media(s["img"], s["alt"], s["ph"])}<h2>{s["name"]}</h2><p>{short[slug]}</p><span class="link">Meer over {s["name"].lower()}</span></a></li>'
trail = [("Home", "/"), ("Producten", "/producten")]
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Onze producten</h1>
  <p class="lead">Van opwekken tot opslaan en duurzaam verwarmen of koelen. Elke oplossing werkt zelfstandig, en we zorgen dat ze samenwerken als je ze combineert.</p>
</div></section>
<section class="sec pt-1"><div class="wrap"><ul class="solutions">{sol_items}</ul></div></section>
<section class="sec sec--dark"><div class="wrap band">
  <div><h2>Voor bedrijven</h2><p class="lead muted">Zonnestroom op een bedrijfsdak, opslag voor piekverbruik en een elektrische installatie die de groei aankan.</p><a class="btn btn--mint mt-2" href="/zakelijk">Zakelijke oplossingen</a></div>
  {media("zakelijk.svg", "Illustratie van een bedrijfspand met zonnepanelen op het platte dak", "zonnepanelen op bedrijfsdak")}
</div></section>
{cta()}'''
page("/producten", "Producten: zonnepanelen, thuisbatterij, warmtepomp, airco",
     "Overzicht van alle producten van AT Energy Solutions: zonnepanelen, thuisbatterijen, warmtepompen, airco’s en zakelijke installaties.",
     body, current="/producten", schema=[crumbs_schema(trail), {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + "/" + o, "name": SERVICES[o]["name"]} for i, o in enumerate(ORDER)]}])

# ---------- Zakelijk ----------
biz_faq = [
 ("Wat als er netcongestie is in mijn regio?", "<p>Op veel plekken in Nederland is het stroomnet vol, waardoor een zwaardere aansluiting of teruglevering beperkt kan zijn. We kijken dan naar oplossingen binnen je bestaande aansluiting, zoals meer eigen verbruik en opslag.</p>"),
 ("Is er fiscaal voordeel mogelijk?", "<p>Voor bepaalde energiebesparende investeringen kunnen ondernemers gebruikmaken van regelingen zoals de Energie-investeringsaftrek (EIA) of de kleinschaligheidsinvesteringsaftrek (KIA). Voorwaarden staan op rvo.nl; overleg ook met je boekhouder.</p>"),
]
trail = [("Home", "/"), ("Zakelijk", "/zakelijk")]
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <div class="svc-hero">
    <div><h1>Energie voor je bedrijf, goed geregeld</h1><p class="lead">Voor ondernemers in {PH_REGIO} en daarbuiten. Van zonnepanelen op een bedrijfsdak tot een elektrische installatie die klaar is voor elektrificatie.</p>
    <div class="btn-row mt-2"><a class="btn btn--ink" href="/contact">Plan een zakelijk gesprek</a></div></div>
    {media("zakelijk.svg", "Illustratie van een bedrijfspand met zonnepanelen op het platte dak", "zonnepanelen op bedrijfsdak", eager=True)}
  </div>
</div></section>
{tldr_box("AT Energy Solutions uit Nieuwerkerk aan den IJssel installeert zonnepanelen, batterijopslag en elektrotechniek voor bedrijven. We vertrekken vanuit je verbruiksprofiel en de capaciteit van je netaansluiting, en verzorgen opwek, opslag en de elektrische installatie als één partij.")}
<section class="sec--tight"><div class="wrap"><ul class="facts">
  <li><h3>Zonnestroom op het dak</h3><p>Platte daken, staaldaken en hellende daken, met een montagesysteem dat bij de constructie past.</p></li>
  <li><h3>Opslag en piekbeperking</h3><p>Een batterij kan pieken in je verbruik afvlakken en meer eigen opwek benutten.</p></li>
  <li><h3>Elektrotechniek</h3><p>Verdeelinrichtingen, groepen en aanpassingen aan de installatie, door ons eigen team.</p></li>
</ul></div></section>
<section class="sec"><div class="wrap prose">
  <h2>Hoe we zakelijke projecten aanpakken</h2>
  <p>We beginnen met je verbruiksprofiel en de capaciteit van je aansluiting. Daarna kijken we naar het dak, de constructie en de plek voor omvormers en eventuele opslag. Je krijgt een voorstel dat aansluit op je bedrijfsvoering, inclusief planning zodat je werk zo min mogelijk stilligt.</p>
  <h2>Waarom ondernemers voor ons kiezen</h2>
  <ul><li>InstallQ-erkend installateur voor elektra en zonnestroom, met BRL 200-certificaat.</li>
  <li>20 jaar ervaring met particuliere en zakelijke installaties.</li>
  <li>Eén partij voor opwek, opslag én de elektrische installatie.</li></ul>
</div></section>
<section class="sec sec--alt" aria-labelledby="bfaq-t"><div class="wrap"><div class="sec-head"><h2 id="bfaq-t">Vragen van ondernemers</h2></div>{faq_html(biz_faq)}<!--RELATED:zakelijk--></div></section>
{cta("Een zakelijk project bespreken?", "Stuur ons je vraag met wat informatie over je pand en verbruik. We plannen een gesprek en kijken wat haalbaar is.")}'''
page("/zakelijk", "Zakelijke zonnepanelen en energie-installaties",
     "Zonnepanelen, batterijopslag en elektrotechniek voor bedrijven. AT Energy Solutions is InstallQ-erkend en heeft 20 jaar ervaring met zakelijke installaties.",
     body, current="/zakelijk", schema=[service_schema("Zakelijke energie-installaties", "Zonnepanelen, opslag en elektrotechniek voor bedrijven.", "/zakelijk"), crumbs_schema(trail), faq_schema(biz_faq)])

# ---------- Over ons ----------
trail = [("Home", "/"), ("Over ons", "/over-ons")]
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Al 20 jaar actief in elektra en verduurzaming</h1>
  <p class="lead">AT Energy Solutions is een InstallQ-erkend elektra- en zonnestroominstallateur uit Nieuwerkerk aan den IJssel. We helpen particulieren en bedrijven met zonnepanelen, thuisbatterijen, warmtepompen en airco’s.</p>
</div></section>
<section class="sec pt-1"><div class="wrap band">
  {media("team.svg", "Illustratie van een servicebus van AT Energy Solutions", "team bij de bedrijfsbus (echte teamfoto)")}
  <div class="prose">
    <h2>Ons verhaal</h2>
    <p>We bestaan 20 jaar. In die tijd bouwden we veel ervaring op met elektrotechniek en zonnestroom, en breidden we uit naar thuisbatterijen, warmtepompen en airco’s.</p>
    <p>Die elektrotechnische achtergrond merk je in ons werk. Een zonnestroominstallatie, batterij of warmtepomp is zo goed als de installatie waarop hij is aangesloten. Daarom kijken we altijd ook naar je meterkast.</p>
  </div>
</div></section>
<section class="sec sec--dark"><div class="wrap split">
  <div><h2>Waar we voor staan</h2></div>
  <ul class="reasons">
    <li>{I["shield"]}<div><h3>Vakmanschap volgens de norm</h3><p>InstallQ-erkend en BRL 200-gecertificeerd. We werken volgens de geldende normen en voorschriften.</p></div></li>
    <li>{I["talk"]}<div><h3>Eerlijk advies</h3><p>We beloven geen besparing die we niet kunnen onderbouwen. We rekenen met jouw verbruik en jouw situatie.</p></div></li>
  </ul>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>Bedrijfsgegevens</h2></div>
  <ul class="certs narrow">
    <li><strong>Handelsnaam</strong><span>AT Energy Solutions</span></li>
    <li><strong>KvK-nummer</strong><span>{KVK}</span></li>
    <li><strong>Erkenning</strong><span>InstallQ, elektra en zonnestroom</span></li>
    <li><strong>Certificaat</strong><span>BRL 200</span></li>
    <li><strong>E-mail</strong><span><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></span></li>
    <li><strong>Adres</strong><span>{PH_ADDR}</span></li>
  </ul>
</div></section>
{cta()}'''
page("/over-ons", "Over ons", "AT Energy Solutions is al 20 jaar installateur en InstallQ-erkend voor elektra en zonnestroom. Lees wie we zijn en hoe we werken.",
     body, current="/over-ons", schema=[ORG, crumbs_schema(trail)])

# ---------- FAQ ----------
faq_groups = [
 ("Algemeen", home_faq),
 ("Zonnepanelen", SERVICES["zonnepanelen"]["faq"]),
 ("Thuisbatterij", SERVICES["thuisbatterij"]["faq"]),
 ("Warmtepomp", SERVICES["warmtepomp"]["faq"]),
 ("Airco", SERVICES["airco"]["faq"]),
 ("Zakelijk", biz_faq),
 ("Offerte en installatie", [
   ("Welke garantie krijg ik?", "<p>Garantie verschilt per product en fabrikant. In de offerte staat per onderdeel welke product- en installatiegarantie geldt.</p>"),
   ("In welke regio werken jullie?", f"<p>We werken vooral in {PH_REGIO}. Voor grotere projecten komen we ook verder. Neem contact op als je twijfelt.</p>"),
 ]),
]
all_qa = [qa for _, g in faq_groups for qa in g]
trail = [("Home", "/"), ("Veelgestelde vragen", "/veelgestelde-vragen")]
groups_html = "".join(f'<div class="faq-group"><h2>{t}</h2>{faq_html(g)}</div>' for t, g in faq_groups)
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Veelgestelde vragen</h1><p class="lead">Korte, duidelijke antwoorden op wat klanten ons het vaakst vragen. Staat je vraag er niet bij? <a class="link" href="/contact">Stel hem gerust</a>.</p>
</div></section>
<section class="sec pt-1"><div class="wrap">{groups_html}</div></section>
{cta()}'''
page("/veelgestelde-vragen", "Veelgestelde vragen", "Antwoorden op veelgestelde vragen over zonnepanelen, thuisbatterijen, warmtepompen, airco’s, subsidie en het einde van de salderingsregeling.",
     body, current="/veelgestelde-vragen", schema=[faq_schema(all_qa), crumbs_schema(trail)])

# ---------- Kennisbank ----------
ARTICLES = [
 dict(slug="salderingsregeling-stopt", date="2026-10-15",
  title="De salderingsregeling stopt in 2027: wat betekent dat voor jou?",
  desc="Op 1 januari 2027 stopt de salderingsregeling voor zonnepanelen. Wat verandert er, wat is een terugleververgoeding en wanneer is een thuisbatterij zinvol?",
  intro="Op 1 januari 2027 stopt de salderingsregeling. Wie zonnepanelen heeft, merkt dat op de energierekening. Dit zijn de belangrijkste veranderingen.",
  body='''<h2>Wat is salderen?</h2>
<p>Met salderen mag je de stroom die je teruglevert aan het net wegstrepen tegen de stroom die je afneemt. Lever je over het jaar evenveel terug als je afneemt, dan betaal je per saldo vrijwel niets voor die stroom, inclusief energiebelasting.</p>
<h2>Wat verandert er op 1 januari 2027?</h2>
<p>Vanaf die datum mag je niet meer salderen. Je betaalt voor alle stroom die je van het net afneemt, en je krijgt voor teruggeleverde stroom een terugleververgoeding van je energieleverancier. Die vergoeding ligt lager dan de prijs die je voor stroom betaalt. De wet schrijft voor dat de vergoeding van 2027 tot en met 2030 minimaal de helft van het kale leveringstarief is (de prijs zonder energiebelasting en btw). Daarnaast rekenen veel leveranciers terugleverkosten.</p>
<div class="note"><p>Kijk voor de officiële regels en eventuele wijzigingen op rijksoverheid.nl. Regels en tarieven van leveranciers kunnen veranderen.</p></div>
<h2>Wat kun je doen?</h2>
<ul><li><strong>Meer stroom direct gebruiken:</strong> zet apparaten zoals de wasmachine of vaatwasser aan als de zon schijnt.</li>
<li><strong>Stroom opslaan:</strong> met een <a href="/thuisbatterij">thuisbatterij</a> gebruik je overdag opgewekte stroom ’s avonds zelf.</li>
<li><strong>Elektrisch verwarmen met eigen stroom:</strong> een <a href="/warmtepomp">warmtepomp</a> of <a href="/airco">airco</a> kan een deel van je zonnestroom benutten.</li>
<li><strong>Je contract vergelijken:</strong> let op de terugleververgoeding en terugleverkosten.</li></ul>
<h2>Blijven zonnepanelen interessant?</h2>
<p>Ja, zonnestroom die je zelf gebruikt, hoef je niet in te kopen. Hoeveel het oplevert, hangt meer dan voorheen af van hoeveel je zelf direct gebruikt. Bij een nieuwe installatie houden we daar in het ontwerp rekening mee.</p>'''),
 dict(slug="hybride-of-volledige-warmtepomp", date="2026-10-15",
  title="Hybride of volledig elektrische warmtepomp: wat past bij jouw huis?",
  desc="Het verschil tussen een hybride en een volledig elektrische warmtepomp, en hoe isolatie en afgiftesysteem bepalen welke het beste bij je woning past.",
  intro="Een warmtepomp kan naast je cv-ketel werken of hem helemaal vervangen. Welke keuze verstandig is, hangt vooral af van je woning.",
  body='''<h2>Zo werkt een warmtepomp</h2>
<p>Een lucht-water-warmtepomp onttrekt warmte aan de buitenlucht, zelfs als het koud is, en geeft die af aan het water in je verwarmingssysteem. Hoe lager de watertemperatuur die je huis nodig heeft, hoe efficiënter dat gaat.</p>
<h2>Hybride warmtepomp</h2>
<p>Een hybride warmtepomp werkt samen met je cv-ketel. De warmtepomp verwarmt zolang dat efficiënt kan; op koude dagen en voor warm tapwater springt de ketel bij.</p>
<ul><li>Geschikt voor de meeste bestaande woningen, ook bij matige isolatie.</li>
<li>Lagere investering dan een volledig elektrische warmtepomp.</li>
<li>Je blijft een gasaansluiting houden.</li></ul>
<h2>Volledig elektrische warmtepomp</h2>
<p>Een volledig elektrische warmtepomp verzorgt verwarming en warm water zonder cv-ketel, meestal met een boilervat.</p>
<ul><li>Vereist goede isolatie en een afgiftesysteem dat op lage temperatuur werkt, zoals vloerverwarming of ruim bemeten radiatoren.</li>
<li>Je kunt je gasaansluiting laten verwijderen.</li>
<li>Vraagt meer van je elektrische installatie.</li></ul>
<h2>Hoe kies je?</h2>
<p>Begin bij je woning: hoe goed is hij geïsoleerd en hoe wordt de warmte afgegeven? Een goede tussenstap is vaak eerst een hybride warmtepomp, en later all-electric na verdere isolatie. We bekijken dat graag samen met je. Meer informatie vind je op onze pagina over <a href="/warmtepomp">warmtepompen</a>.</p>'''),
 dict(slug="thuisbatterij-plaatsen-waar-op-letten", date="2026-10-15",
  title="Een thuisbatterij plaatsen: hier let je op",
  desc="Waar plaats je een thuisbatterij, welke capaciteit past bij je verbruik en hoe sluit je hem aan op bestaande zonnepanelen? Praktische aandachtspunten.",
  intro="Een thuisbatterij is pas zinvol als capaciteit, plek en aansluiting goed gekozen zijn. Deze punten nemen we mee in ons advies.",
  body='''<h2>1. De juiste capaciteit</h2>
<p>De capaciteit, uitgedrukt in kWh, bepaalt hoeveel stroom de batterij kan opslaan. Die moet passen bij hoeveel zonnestroom je overdag overhoudt en hoeveel je ’s avonds en ’s nachts verbruikt. Te groot betekent dat je betaalt voor capaciteit die je zelden gebruikt.</p>
<h2>2. Een geschikte plek</h2>
<p>Fabrikanten schrijven voor bij welke temperaturen en met welke ventilatie de batterij geplaatst mag worden. Veelgebruikte plekken zijn een berging, bijkeuken of garage. De batterij moet bereikbaar blijven voor onderhoud.</p>
<h2>3. Aansluiten op je zonnepanelen</h2>
<p>Bij bestaande zonnepanelen kan een AC-gekoppelde batterij met eigen omvormer worden toegevoegd. Bij een nieuwe installatie of een verouderde omvormer ligt een hybride omvormer meer voor de hand.</p>
<h2>4. Je meterkast</h2>
<p>Een batterij krijgt een eigen groep en beveiliging. We controleren of je meterkast en hoofdaansluiting daar ruimte voor hebben.</p>
<h2>5. Slimme aansturing</h2>
<p>Met een dynamisch energiecontract kunnen sommige batterijen laden als stroom goedkoop is en ontladen als hij duur is. Of dat voor jou loont, hangt af van je contract en verbruik.</p>
<p>Meer weten? Bekijk onze pagina over <a href="/thuisbatterij">thuisbatterijen</a>.</p>'''),
]

ARTICLES += [
 dict(slug="netcongestie-bedrijf", date="2026-10-15",
  title="Netcongestie: wat betekent een vol stroomnet voor jouw bedrijf?",
  desc="Op veel plekken is het stroomnet vol. Wat netcongestie is, wat het betekent voor je aansluiting en teruglevering, en wat je als ondernemer kunt doen.",
  intro="Wil je als ondernemer verduurzamen, elektrificeren of zonnepanelen leggen, dan kun je tegen netcongestie aanlopen. Dit is wat het betekent en welke mogelijkheden er zijn.",
  body='''<h2>Wat is netcongestie?</h2>
<p>Netcongestie betekent dat het elektriciteitsnet op een bepaalde plek op piekmomenten geen extra stroom meer kan vervoeren. Dat kan gelden voor afname (stroom gebruiken) en voor invoeding (stroom terugleveren). Netbeheerders kunnen dan niet direct een nieuwe of zwaardere aansluiting leveren, of extra teruglevering toestaan.</p>
<h2>Wat merk je ervan als bedrijf?</h2>
<ul><li>Een aanvraag voor een zwaardere aansluiting kan op een wachtlijst komen.</li>
<li>Een grote zonnestroominstallatie mag soms niet volledig terugleveren.</li>
<li>Plannen voor elektrisch verwarmen of laden vragen meer voorbereiding.</li></ul>
<p>Netbeheer Nederland publiceert een capaciteitskaart waarop je per regio ziet hoe vol het net is. Je netbeheerder kan vertellen wat dat voor jouw locatie betekent.</p>
<h2>Wat kun je doen binnen je huidige aansluiting?</h2>
<ul><li><strong>Meer zelf gebruiken:</strong> stem zonnestroom af op je eigen verbruik, zodat je minder teruglevert.</li>
<li><strong>Opslag:</strong> een batterij vangt overschotten op en vlakt pieken in je verbruik af.</li>
<li><strong>Slim sturen:</strong> verschuif verbruik van grote installaties naar momenten met ruimte.</li>
<li><strong>Flexibele afspraken:</strong> netbeheerders bieden steeds vaker contractvormen aan waarbij je op drukke momenten minder afneemt of teruglevert.</li></ul>
<h2>Hoe wij helpen</h2>
<p>Als elektrotechnisch installateur kijken we naar je verbruiksprofiel, de capaciteit van je aansluiting en de mogelijkheden voor opwek en opslag. Zo haal je het meeste uit de ruimte die er wel is. Meer over onze <a href="/zakelijk">zakelijke oplossingen</a>.</p>''',
  sources=[("Netbeheer Nederland", "https://www.netbeheernederland.nl")]),
 dict(slug="zonnepanelen-bedrijfsdak", date="2026-10-15",
  title="Zonnepanelen op een bedrijfsdak: hier let je op",
  desc="Draagkracht, dakbedekking, brandveiligheid, aansluiting en subsidieregelingen: de belangrijkste aandachtspunten voor zonnepanelen op een bedrijfsdak.",
  intro="Een bedrijfsdak is vaak groot en vrij van schaduw, en daarmee geschikt voor zonnepanelen. Toch vraagt een zakelijke installatie meer voorbereiding dan een woning.",
  body='''<h2>1. Constructie en draagkracht</h2>
<p>Panelen en montagesysteem voegen gewicht toe, en op platte daken komt daar vaak ballast bij. Laat vooraf beoordelen of de dakconstructie dat kan dragen. Bij lichte staaldaken kan een systeem zonder ballast nodig zijn.</p>
<h2>2. Staat van de dakbedekking</h2>
<p>Panelen liggen er tientallen jaren. Moet de dakbedekking binnen een paar jaar vervangen worden, doe dat dan eerst. Anders moeten de panelen er later tijdelijk weer af.</p>
<h2>3. Brandveiligheid en verzekering</h2>
<p>Verzekeraars stellen steeds vaker eisen aan zonnestroominstallaties op bedrijfsdaken, bijvoorbeeld aan de kabelroutes en de plaats van omvormers. Overleg vooraf met je verzekeraar en kies een gecertificeerde installateur.</p>
<h2>4. Aansluiting en teruglevering</h2>
<p>De grootte van je aansluiting en de beschikbare netcapaciteit bepalen hoeveel je kunt terugleveren. In regio’s met <a href="/kennisbank/netcongestie-bedrijf">netcongestie</a> is het verstandig om de installatie af te stemmen op je eigen verbruik.</p>
<h2>5. Fiscale regelingen en subsidie</h2>
<p>Afhankelijk van je situatie kunnen regelingen als de kleinschaligheidsinvesteringsaftrek (KIA), de energie-investeringsaftrek (EIA) of de SDE++ van toepassing zijn. De voorwaarden verschillen per regeling en per jaar. Check ze op rvo.nl en overleg met je adviseur.</p>
<p>Wil je weten wat er op jouw dak mogelijk is? Bekijk onze <a href="/zakelijk">zakelijke oplossingen</a> of <a href="/contact">neem contact op</a>.</p>''',
  sources=[("RVO: subsidies en financiering", "https://www.rvo.nl/subsidies-financiering")]),
]
SOURCES = {
 "salderingsregeling-stopt": [("Rijksoverheid: salderingsregeling", "https://www.rijksoverheid.nl/onderwerpen/energie-thuis/salderingsregeling")],
 "hybride-of-volledige-warmtepomp": [("RVO: ISDE-subsidie", "https://www.rvo.nl/subsidies-financiering/isde")],
 "thuisbatterij-plaatsen-waar-op-letten": [("Rijksoverheid: salderingsregeling", "https://www.rijksoverheid.nl/onderwerpen/energie-thuis/salderingsregeling")],
}
for a in ARTICLES:
    a.setdefault("sources", SOURCES.get(a["slug"], []))

posts = "".join(f'<li><a href="/kennisbank/{a["slug"]}"><time datetime="{a["date"]}">{fmt(a["date"])}</time><div><h2>{a["title"]}</h2><p>{a["desc"]}</p></div></a></li>' for a in ARTICLES)
trail = [("Home", "/"), ("Kennisbank", "/kennisbank")]
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Kennisbank</h1><p class="lead">Heldere uitleg over zonnepanelen, thuisbatterijen, warmtepompen en de regels die ermee te maken hebben. Geschreven door onze installateurs.</p>
</div></section>
<section class="sec pt-1"><div class="wrap"><ul class="posts">{posts}</ul></div></section>
{cta()}'''
page("/kennisbank", "Kennisbank: zonnepanelen, batterijen, warmtepompen",
     "Praktische artikelen over zonnepanelen, thuisbatterijen, warmtepompen, airco’s en het einde van de salderingsregeling.", body, current="/kennisbank",
     schema=[crumbs_schema(trail)])

def sources_html(src):
    if not src: return ""
    return '<h2>Bronnen</h2><ul class="sources">' + "".join(f'<li><a href="{u}" rel="noopener" target="_blank">{n}</a></li>' for n, u in src) + '</ul>'
for a in ARTICLES:
    path = f'/kennisbank/{a["slug"]}'
    trail = [("Home", "/"), ("Kennisbank", "/kennisbank"), (a["title"], path)]
    body = f'''<article>
<section class="page-head"><div class="wrap">{crumbs(trail)}
  <div class="prose"><h1 class="h1-article">{a["title"]}</h1><p class="lead">{a["intro"]}</p>
  <p class="article-meta">Door de redactie van AT Energy Solutions, gepubliceerd op <time datetime="{a["date"]}">{fmt(a["date"])}</time></p></div>
</div></section>
<section class="sec pt-0"><div class="wrap"><div class="prose">{a["body"]}{sources_html(a["sources"])}</div></div></section>
</article>
{cta()}'''
    art = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
           "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "nl-NL",
           "author": {"@type": "Organization", "name": "AT Energy Solutions", "url": BASE + "/"},
           "publisher": {"@id": BASE + "/#bedrijf"}, "mainEntityOfPage": BASE + path,
           "image": OG_IMAGE, "citation": [u for _, u in a["sources"]]}
    page(path, a["title"], a["desc"], body, current="/kennisbank", schema=[art, crumbs_schema(trail)], og_type="article")

# ---------- Lokale pagina ----------
loc_faq = [
 ("Waar is AT Energy Solutions gevestigd?", "<p>Aan de Hoofdweg Noord 11, 2913 LB Nieuwerkerk aan den IJssel, in de gemeente Zuidplas (Zuid-Holland).</p>"),
 ("Werken jullie ook buiten Nieuwerkerk aan den IJssel?", "<p>Ja. We werken in Nieuwerkerk aan den IJssel en de omliggende plaatsen, en voor grotere of zakelijke projecten ook verder weg.</p>"),
]
trail = [("Home", "/"), ("Werkgebied", "/installateur-nieuwerkerk-aan-den-ijssel")]
svc_links = "".join(f'<li><a href="/{o}">{SERVICES[o]["name"]}</a></li>' for o in ORDER)
body = f"""<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Installateur in Nieuwerkerk aan den IJssel</h1>
  <p class="lead">AT Energy Solutions is een InstallQ-erkend installateur voor zonnepanelen, thuisbatterijen, warmtepompen en airco’s, gevestigd in Nieuwerkerk aan den IJssel.</p>
</div></section>
{tldr_box("AT Energy Solutions (KvK 24401102) is gevestigd aan de Hoofdweg Noord 11 in Nieuwerkerk aan den IJssel, gemeente Zuidplas. Het bedrijf bestaat 20 jaar, is InstallQ-erkend voor elektra en zonnestroom en heeft een BRL 200-certificaat. Het installeert zonnepanelen, thuisbatterijen, warmtepompen en airco’s voor particulieren en bedrijven in de regio.")}
<section class="sec pt-0"><div class="wrap local">
  <div class="prose">
    <h2>Lokaal installateur, korte lijnen</h2>
    <p>Omdat we in de buurt zitten, kunnen we makkelijk langskomen voor een kennismaking of opname, en zijn we snel ter plaatse voor service na de installatie.</p>
    <h2>Wat we doen in de regio</h2>
    <ul><li><a href="/zonnepanelen">Zonnepanelen</a> op pannendaken, platte daken en bedrijfsdaken.</li>
    <li><a href="/thuisbatterij">Thuisbatterijen</a> bij nieuwe of bestaande zonnepanelen.</li>
    <li><a href="/warmtepomp">Warmtepompen</a>, hybride en volledig elektrisch.</li>
    <li><a href="/airco">Airco’s</a> voor koelen en bijverwarmen.</li>
    <li><a href="/zakelijk">Zakelijke installaties</a> en elektrotechniek.</li></ul>
    <h2>Werkgebied</h2>
    <p>We werken in Nieuwerkerk aan den IJssel en de plaatsen eromheen. Voor grotere en zakelijke projecten komen we ook verder.</p>
  </div>
  <address class="addr-card">
    <strong>AT Energy Solutions</strong><br>Hoofdweg Noord 11<br>2913 LB Nieuwerkerk aan den IJssel<br>
    <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>{PHONE_BR}<br>KvK {KVK}<br>
    <a class="link" href="{MAPS}" rel="noopener" target="_blank">Route in Google Maps</a>
  </address>
</div></section>
<section class="sec sec--alt" aria-labelledby="lfaq-t"><div class="wrap"><div class="sec-head"><h2 id="lfaq-t">Vragen over ons werkgebied</h2></div>{faq_html(loc_faq)}
<h2 class="mt-3 h-small">Onze oplossingen</h2><ul class="related">{svc_links}</ul></div></section>
{cta()}"""
page("/installateur-nieuwerkerk-aan-den-ijssel", "Installateur in Nieuwerkerk aan den IJssel",
     "InstallQ-erkend installateur in Nieuwerkerk aan den IJssel (Zuidplas) voor zonnepanelen, thuisbatterijen, warmtepompen en airco’s in de regio.",
     body, schema=[ORG, crumbs_schema(trail), faq_schema(loc_faq)])

# ---------- Contact ----------
choices = "".join(f'<label class="choice"><input type="checkbox" name="interesse" value="{v}"><span>{l}</span></label>'
                  for v, l in [("zonnepanelen","Zonnepanelen"),("thuisbatterij","Thuisbatterij"),("warmtepomp","Warmtepomp"),("airco","Airco"),("anders","Iets anders")])
trail = [("Home", "/"), ("Contact", "/contact")]
body = f'''<section class="page-head"><div class="wrap">{crumbs(trail)}
  <h1>Vraag een offerte aan</h1><p class="lead">Vertel ons kort wat je zoekt. We nemen contact met je op om je situatie door te nemen en sturen daarna een offerte op maat.</p>
</div></section>
<section class="sec pt-1"><div class="wrap contact-grid">
  <form id="contact-form" class="form" action="/api/contact" method="post" novalidate>
    <fieldset class="field"><legend>Ik vraag aan als</legend>
      <div class="choices">
        <label class="choice"><input type="radio" name="type" value="particulier" checked><span>Particulier</span></label>
        <label class="choice"><input type="radio" name="type" value="zakelijk"><span>Zakelijk</span></label>
      </div></fieldset>
    <fieldset class="field"><legend>Waar heb je interesse in? <span class="opt">(meerdere mogelijk)</span></legend><div class="choices">{choices}</div></fieldset>
    <div class="row">
      <div class="field"><label for="f-naam">Naam</label><input id="f-naam" name="naam" autocomplete="name" required maxlength="100" aria-describedby="e-naam"><span class="err" id="e-naam" hidden></span></div>
      <div class="field"><label for="f-email">E-mailadres</label><input id="f-email" name="email" type="email" autocomplete="email" required maxlength="160" aria-describedby="e-email"><span class="err" id="e-email" hidden></span></div>
    </div>
    <div class="row">
      <div class="field"><label for="f-tel">Telefoonnummer <span class="opt">(optioneel)</span></label><input id="f-tel" name="telefoon" type="tel" autocomplete="tel" maxlength="20" aria-describedby="e-telefoon"><span class="err" id="e-telefoon" hidden></span></div>
      <div class="field"><label for="f-postcode">Postcode</label><input id="f-postcode" name="postcode" autocomplete="postal-code" required maxlength="7" placeholder="1234 AB" aria-describedby="e-postcode"><span class="err" id="e-postcode" hidden></span></div>
    </div>
    <div class="field"><label for="f-bericht">Je vraag</label><textarea id="f-bericht" name="bericht" required maxlength="3000" aria-describedby="e-bericht" placeholder="Bijvoorbeeld: ik heb 10 zonnepanelen en wil weten of een thuisbatterij zinvol is."></textarea><span class="err" id="e-bericht" hidden></span></div>
    <div class="hp" aria-hidden="true"><label for="f-website">Laat dit veld leeg</label><input id="f-website" name="website" tabindex="-1" autocomplete="off"></div>
    <input type="hidden" name="t" value="">
    <p class="small mb-0">We gebruiken je gegevens alleen om je aanvraag te beantwoorden. Lees onze <a class="link" href="/privacyverklaring">privacyverklaring</a>.</p>
    <div><button class="btn btn--ink" type="submit">Aanvraag versturen</button></div>
    <div id="form-status" class="form-status" role="alert" hidden></div>
  </form>
  <aside>
    <div class="aside-block"><h2>Direct contact</h2><dl>
      <div><dt>E-mail</dt><dd><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
      {PHONE_DL}
      <div><dt>Adres</dt><dd>Hoofdweg Noord 11<br>2913 LB Nieuwerkerk aan den IJssel<br><a class="link" href="{MAPS}" rel="noopener" target="_blank">Route in Google Maps</a></dd></div>
    </dl></div>
    <div class="aside-block"><h2>Wat gebeurt er hierna?</h2><p class="mb-0">We lezen je aanvraag, nemen contact op om je situatie door te nemen en sturen daarna een offerte op maat.</p></div>
  </aside>
</div></section>'''
page("/contact", "Contact en offerte aanvragen", "Vraag een offerte aan voor zonnepanelen, een thuisbatterij, warmtepomp of airco. AT Energy Solutions, Hoofdweg Noord 11, Nieuwerkerk aan den IJssel.",
     body, current="/contact", schema=[ORG, crumbs_schema(trail)])

page("/bedankt", "Bedankt voor je aanvraag", "Je aanvraag is ontvangen.",
     '''<section class="page-head"><div class="wrap prose"><h1>Bedankt, je aanvraag is verstuurd</h1>
<p class="lead">We hebben je aanvraag ontvangen en nemen contact met je op om je situatie door te nemen.</p>
<div class="btn-row mt-2"><a class="btn btn--ink" href="/">Terug naar de homepage</a><a class="btn btn--line" href="/kennisbank">Lees in de kennisbank</a></div></div></section>''', noindex=True)

# ---------- Juridisch ----------
legal_note = '<div class="note"><p><strong>Let op:</strong> dit is een conceptversie. Laat deze tekst controleren en vul de gemarkeerde gegevens aan voordat de site live gaat.</p></div>'
page("/privacyverklaring", "Privacyverklaring", "Hoe AT Energy Solutions omgaat met persoonsgegevens die je via de website deelt.", f'''<section class="page-head"><div class="wrap prose"><h1>Privacyverklaring</h1><p class="lead">Laatst bijgewerkt: {fmt(TODAY)}</p>{legal_note}
<h2>Wie zijn wij</h2><p>AT Energy Solutions, ingeschreven bij de KvK onder nummer {KVK}, gevestigd op {PH_ADDR}, is verantwoordelijk voor de verwerking van persoonsgegevens zoals beschreven in deze verklaring. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Welke gegevens we verwerken</h2><p>Als je het contactformulier invult, verwerken we je naam, e-mailadres, postcode, je bericht, je interesse en, als je dat invult, je telefoonnummer. Als je klant wordt, verwerken we ook gegevens die nodig zijn voor offerte, uitvoering en facturatie, zoals je adres.</p>
<h2>Waarom we die gegevens verwerken</h2><ul><li>Om je aanvraag te beantwoorden en een offerte op te stellen (precontractuele maatregelen / gerechtvaardigd belang).</li><li>Om een overeenkomst uit te voeren (uitvoering overeenkomst).</li><li>Om te voldoen aan wettelijke verplichtingen, zoals de fiscale bewaarplicht.</li></ul>
<h2>Hoe lang we gegevens bewaren</h2><p>Aanvragen die niet leiden tot een opdracht bewaren we maximaal 12 maanden. Klant- en factuurgegevens bewaren we zolang de wet dat voorschrijft (fiscaal in de regel 7 jaar).</p>
<h2>Met wie we gegevens delen</h2><p>We verkopen je gegevens niet. We schakelen dienstverleners in die gegevens namens ons verwerken, zoals onze hostingpartij (Vercel), databasedienst (Supabase, servers in de EU) en e-maildienst (Resend). Met hen sluiten we waar nodig een verwerkersovereenkomst. Deze partijen kunnen gegevens buiten de EU verwerken; dat gebeurt dan op basis van passende waarborgen.</p>
<h2>Cookies</h2><p>Deze website plaatst geen tracking- of marketingcookies. Zie de <a href="/cookieverklaring">cookieverklaring</a>.</p>
<h2>Beveiliging</h2><p>De website werkt uitsluitend via een beveiligde HTTPS-verbinding. Formulierinvoer wordt aan de serverzijde gecontroleerd en niet in de browser opgeslagen.</p>
<h2>Jouw rechten</h2><p>Je hebt het recht om je gegevens in te zien, te laten corrigeren of verwijderen, de verwerking te beperken, bezwaar te maken en je gegevens over te dragen. Stuur je verzoek naar <a href="mailto:{EMAIL}">{EMAIL}</a>. Je hebt ook het recht een klacht in te dienen bij de Autoriteit Persoonsgegevens.</p>
</div></section>''')

page("/cookieverklaring", "Cookieverklaring", "Welke cookies de website van AT Energy Solutions gebruikt.", f'''<section class="page-head"><div class="wrap prose"><h1>Cookieverklaring</h1><p class="lead">Laatst bijgewerkt: {fmt(TODAY)}</p>
<p>Deze website gebruikt geen analytische, tracking- of marketingcookies en laadt geen externe scripts, lettertypen of video’s van derden. Daarom vragen we geen cookietoestemming.</p>
<h2>Wijzigingen</h2><p>Voegen we in de toekomst bijvoorbeeld websitestatistieken of ingesloten video’s toe, dan passen we deze verklaring aan en vragen we vooraf toestemming waar de wet dat vereist.</p>
<p>Vragen? Mail naar <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>''')

page("/algemene-voorwaarden", "Algemene voorwaarden", "Algemene voorwaarden van AT Energy Solutions.", f'''<section class="page-head"><div class="wrap prose"><h1>Algemene voorwaarden</h1>
<p class="lead">Wil je onze algemene voorwaarden inzien? Mail ons, dan sturen we ze direct toe.</p>
<p>Vragen over onze voorwaarden? Mail naar <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>''', noindex=True)

# 404 (Vercel gebruikt 404.html automatisch)
page("/404", "Pagina niet gevonden", "Deze pagina bestaat niet (meer).", '''<section class="page-head"><div class="wrap prose"><h1>Deze pagina bestaat niet</h1>
<p class="lead">Misschien is de link verouderd of zit er een typfout in het adres.</p>
<div class="btn-row mt-2"><a class="btn btn--ink" href="/">Naar de homepage</a><a class="btn btn--line" href="/producten">Bekijk onze producten</a></div></div></section>''', noindex=True)


# ---------- Gerelateerde artikelen injecteren ----------
RELATED = {"zonnepanelen": ["salderingsregeling-stopt", "zonnepanelen-bedrijfsdak"], "thuisbatterij": ["salderingsregeling-stopt", "thuisbatterij-plaatsen-waar-op-letten"],
           "warmtepomp": ["hybride-of-volledige-warmtepomp"], "airco": ["hybride-of-volledige-warmtepomp"], "zakelijk": ["netcongestie-bedrijf", "zonnepanelen-bedrijfsdak"]}
by_slug = {a["slug"]: a for a in ARTICLES}
for key, slugs in RELATED.items():
    fp = os.path.join(OUT, key + ".html")
    links = "".join(f'<li><a href="/kennisbank/{x}">{by_slug[x]["title"]}</a></li>' for x in slugs)
    block = f'<h2 class="mt-3 h-small">Lees ook</h2><ul class="readmore">{links}</ul>'
    h = open(fp, encoding="utf-8").read().replace(f"<!--RELATED:{key}-->", block)
    open(fp, "w", encoding="utf-8").write(h)

# ---------- Manifest, security.txt, llms-full.txt ----------
open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps({
    "name": "AT Energy Solutions", "short_name": "AT Energy", "lang": "nl", "start_url": "/", "display": "browser",
    "background_color": "#F8F7F3", "theme_color": "#1C2124",
    "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2))
os.makedirs(os.path.join(OUT, ".well-known"), exist_ok=True)
open(os.path.join(OUT, ".well-known", "security.txt"), "w").write(f"Contact: mailto:{EMAIL}\nPreferred-Languages: nl, en\nCanonical: {BASE}/.well-known/security.txt\nExpires: {date.today().year + 1}-12-31T23:00:00.000Z\n")
import re as _re
def _text(path):
    rel = "index.html" if path == "/" else path.strip("/") + ".html"
    h = open(os.path.join(OUT, rel), encoding="utf-8").read()
    m = _re.search(r'<main id="inhoud">(.*)</main>', h, _re.S).group(1)
    m = _re.sub(r"<(script|style|svg|nav)[^>]*>.*?</\1>", " ", m, flags=_re.S)
    m = _re.sub(r"</(h[1-3])>", "\n\n", m); m = _re.sub(r"<(h[1-3])[^>]*>", "\n## ", m)
    m = _re.sub(r"<li[^>]*>", "\n- ", m); m = _re.sub(r"</p>", "\n\n", m)
    m = html.unescape(_re.sub(r"<[^>]+>", " ", m))
    m = _re.sub(r"[ \t]+", " ", m); m = _re.sub(r"\n\s*\n\s*\n+", "\n\n", m)
    return m.strip()
full = "# AT Energy Solutions – volledige tekst\n\n" + "\n\n---\n\n".join(f"URL: {BASE}{p if p != '/' else '/'}\n\n{_text(p)}" for p, ni in PAGES if not ni)
open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf-8").write(full)

# ---------- Sitemap & robots ----------
urls = [p for p, ni in PAGES if not ni]
prio = lambda p: "1.0" if p == "/" else "0.8" if p.count("/") == 1 else "0.6"
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f'  <url><loc>{BASE}{p if p != "/" else "/"}</loc><lastmod>{TODAY}</lastmod></url>\n' for p in urls) + '</urlset>\n'
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"]
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nDisallow: /api/\n\n" + "".join(f"User-agent: {b}\nAllow: /\nDisallow: /api/\n\n" for b in AI_BOTS) + f"Sitemap: {BASE}/sitemap.xml\n")
# llms.txt (voorgestelde standaard, geen garantie op AI-vermeldingen; kost niets en schaadt niet)
llms = f"""# AT Energy Solutions

> Al 20 jaar actief in elektra en verduurzaming. InstallQ-erkend elektra- en zonnestroominstallateur (BRL 200-gecertificeerd). Installeert zonnepanelen, thuisbatterijen, warmtepompen en airco's voor particulieren en bedrijven. Gevestigd aan Hoofdweg Noord 11, 2913 LB Nieuwerkerk aan den IJssel (gemeente Zuidplas). KvK {KVK}. Contact: {EMAIL}.

## Oplossingen
- [Zonnepanelen]({BASE}/zonnepanelen): ontwerp, installatie en aanmelding
- [Thuisbatterij]({BASE}/thuisbatterij): opslag van zonnestroom, relevant na einde saldering (1 januari 2027)
- [Warmtepomp]({BASE}/warmtepomp): hybride en volledig elektrisch
- [Airco]({BASE}/airco): koelen en bijverwarmen
- [Zakelijk]({BASE}/zakelijk): zonnestroom, opslag en elektrotechniek voor bedrijven

## Bedrijf
- [Over ons]({BASE}/over-ons)
- [Werkgebied Nieuwerkerk aan den IJssel]({BASE}/installateur-nieuwerkerk-aan-den-ijssel)
- [Veelgestelde vragen]({BASE}/veelgestelde-vragen)
- [Contact]({BASE}/contact)

## Kennisbank
""" + "".join(f"- [{a['title']}]({BASE}/kennisbank/{a['slug']}): {a['desc']}\n" for a in ARTICLES)
open(os.path.join(OUT, "llms.txt"), "w").write(llms)
print(f"{len(PAGES)} pagina's gegenereerd, {len(urls)} in sitemap.")
