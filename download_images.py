#!/usr/bin/env python3
"""Downloadt de Unsplash-foto's naar assets/img/ zodat de site ze zelf host (sneller en AVG-vriendelijker).
Daarna: python3 build.py  (build.py gebruikt dan automatisch de lokale bestanden).
Optioneel: haal daarna 'https://images.unsplash.com' weg uit img-src in vercel.json."""
import os, urllib.request, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("b", os.path.join(here, "build.py"))
src = open(os.path.join(here, "build.py"), encoding="utf-8").read()
start = src.index("PHOTOS = {"); end = src.index("}", start) + 1
ns = {}; exec(src[start:end], ns)
for key, (pid, _) in ns["PHOTOS"].items():
    w, h = (1920, 1080) if key == "hero-woning" else (1600, 1067)
    url = f"https://images.unsplash.com/{pid}?auto=format&fm=jpg&fit=crop&w={w}&h={h}&q=78"
    dest = os.path.join(here, "assets", "img", key + ".jpg")
    print("↓", key); urllib.request.urlretrieve(url, dest)
print("Klaar. Draai nu: python3 build.py")
