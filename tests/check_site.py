#!/usr/bin/env python3
"""Controleert de gebouwde site: interne links, JSON-LD, één H1, title/description, geen inline styles."""
import re, glob, os, json, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
files = [f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("preview", "node_modules"))]
routes = {"/" if f == "index.html" else "/" + f[:-5] for f in files}
errors = []
for f in files:
    s = open(f, encoding="utf-8").read()
    for h in re.findall(r'href="(/[^"#?]*)', s):
        is_file = h.startswith("/assets") or "." in h.split("/")[-1]
        if (is_file and not os.path.exists(h[1:])) or (not is_file and h not in routes):
            errors.append(f"{f}: kapotte link {h}")
    for src in re.findall(r'src="(/assets/[^"]+)"', s):
        if not os.path.exists(src[1:]): errors.append(f"{f}: ontbrekend bestand {src}")
    for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(j)
        except Exception as e: errors.append(f"{f}: ongeldige JSON-LD ({e})")
    if s.count("<h1") != 1: errors.append(f"{f}: {s.count('<h1')} H1-koppen")
    if 'style="' in s: errors.append(f"{f}: inline style (botst met CSP)")
    if "<title>" not in s or 'name="description"' not in s: errors.append(f"{f}: title/description ontbreekt")
print(f"{len(files)} pagina's gecontroleerd, {len(errors)} fouten")
for e in errors: print(" -", e)
sys.exit(1 if errors else 0)
