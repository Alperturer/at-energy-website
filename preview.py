#!/usr/bin/env python3
"""Maakt één klikbaar voorbeeldbestand (preview.html) van de hele site, handig om op telefoon te bekijken."""
import re, glob, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1] if len(sys.argv) > 1 else "preview.html"
css = re.sub(r'@font-face\s*{[^}]*}', '', open('assets/css/style.css').read())
pages = {}
for f in glob.glob('**/*.html', recursive=True):
    if f == out or f.startswith('preview'): continue
    s = open(f, encoding='utf-8').read()
    route = '/' if f == 'index.html' else '/' + f[:-5]
    pages[route] = (re.search(r'<title>(.*?)</title>', s).group(1), re.search(r'<main id="inhoud">(.*)</main>', s, re.S).group(1))
idx = open('index.html', encoding='utf-8').read()
header = re.search(r'(<a class="skip".*?</header>)', idx, re.S).group(1)
footer = re.search(r'(<div class="mobile-cta".*?</footer>)', idx, re.S).group(1)
tpls = "".join(f'<template data-route="{r}" data-title="{t}">{re.sub(r" srcset=\"[^\"]*\"", "", m).replace(chr(32)+'src="/assets/img/', chr(32)+'data-psrc="/assets/img/')}</template>' for r, (t, m) in pages.items())
import base64, json
imgs = {"/assets/"+os.path.basename(f): "data:image/png;base64,"+base64.b64encode(open(f,'rb').read()).decode() for f in ['assets/logo.png','assets/logo-white.png']}
imgs.update({"/assets/img/"+os.path.basename(f): "data:image/jpeg;base64,"+base64.b64encode(open(f,'rb').read()).decode() for f in glob.glob('assets/img/*.jpg') if not re.search(r'-\d+\.jpg$', f)})
js = "var IMGS="+json.dumps(imgs)+";" + r'''(function(){
var main=document.getElementById('inhoud');
function markImgs(){document.querySelectorAll('img[data-psrc]').forEach(function(i){var k=i.getAttribute('data-psrc');i.loading='eager';i.src=IMGS[k]||k;i.removeAttribute('data-psrc');});document.querySelectorAll('img').forEach(function(i){var k=i.getAttribute('src');if(IMGS[k]){i.loading='eager';i.src=IMGS[k];}});document.querySelectorAll('.media img, .hero-bg').forEach(function(img){var m=function(){img.parentElement.classList.add('is-empty')};if(img.complete&&img.naturalWidth===0)m();else img.addEventListener('error',m);});}
var toggle=document.querySelector('.nav-toggle'),menu=document.getElementById('nav-menu');
function closeNav(){toggle.setAttribute('aria-expanded','false');menu.classList.remove('is-open');document.body.classList.remove('nav-open');}
function go(path){var hash='';var i=path.indexOf('#');if(i>-1){hash=path.slice(i+1);path=path.slice(0,i)||'/';}
 var t=document.querySelector('template[data-route="'+path+'"]')||document.querySelector('template[data-route="/404"]');
 main.innerHTML=t.innerHTML;document.title=t.dataset.title;
 var svc=['/zonnepanelen','/thuisbatterij','/warmtepomp','/airco'];
 var pt=document.querySelector('.sub-toggle');if(pt)pt.classList.toggle('is-active',svc.indexOf(path)>-1||path==='/producten');document.querySelectorAll('.sub').forEach(function(u){u.classList.remove('is-open')});if(pt)pt.setAttribute('aria-expanded','false');document.querySelectorAll('.nav-list a').forEach(function(a){var h=a.getAttribute('href');var cur=!a.classList.contains('nav-cta')&&(h===path||(false)||(h==='/kennisbank'&&path.indexOf('/kennisbank')===0));if(cur)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 closeNav();markImgs();var el=hash&&document.getElementById(hash);if(el)el.scrollIntoView();else window.scrollTo(0,0);}
document.addEventListener('click',function(e){var b=e.target.closest('.sub-toggle');var subs=document.querySelectorAll('.sub');if(b){var o=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(o));document.getElementById(b.getAttribute('aria-controls')).classList.toggle('is-open',o);return;}if(!e.target.closest('.has-sub')){subs.forEach(function(u){u.classList.remove('is-open')});var t=document.querySelector('.sub-toggle');if(t)t.setAttribute('aria-expanded','false');}},true);toggle.addEventListener('click',function(){var o=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(o));menu.classList.toggle('is-open',o);document.body.classList.toggle('nav-open',o);});
document.addEventListener('click',function(e){var a=e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
 if(h.charAt(0)==='/'){e.preventDefault();go(h);}else if(h.charAt(0)==='#'){var el=document.getElementById(h.slice(1));if(el){e.preventDefault();el.scrollIntoView({behavior:'smooth'});}}});
document.addEventListener('submit',function(e){e.preventDefault();var s=document.getElementById('form-status');if(s){s.className='form-status is-ok';s.textContent='Voorbeeldweergave: het formulier verstuurt pas echt na publicatie op Vercel met Resend ingesteld.';s.hidden=false;}});
var hd=document.querySelector('.site-header');window.addEventListener('scroll',function(){hd.classList.toggle('is-scrolled',scrollY>8)},{passive:true});
document.querySelectorAll('header img, footer img').forEach(function(i){var k=i.getAttribute('src');if(IMGS[k])i.src=IMGS[k];});go('/');})();'''
doc = f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AT Energy Solutions – voorbeeld</title><style>{css}</style></head><body>{header}<main id="inhoud"></main>{footer}{tpls}<script>{js}</script></body></html>'
open(out, 'w', encoding='utf-8').write(doc)
print(f"Voorbeeld: {out} ({len(pages)} pagina's)")
