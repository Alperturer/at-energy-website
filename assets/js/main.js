/* AT Energy Solutions — kleine, afhankelijkheidsvrije scripts */
(function () {
  "use strict";

  // Mobiele navigatie
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("nav-menu");
  if (toggle && menu) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Menu sluiten" : "Menu openen");
      menu.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) { if (mq.matches) setOpen(false); });
  }

  // Header-lijn bij scrollen
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Beeldvlakken zonder (nog) geplaatste foto netjes tonen
  document.querySelectorAll(".media img, .hero-bg").forEach(function (img) {
    var mark = function () { img.parentElement.classList.add("is-empty"); };
    if (img.complete && img.naturalWidth === 0) mark();
    else img.addEventListener("error", mark);
  });

  // Contactformulier
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = document.getElementById("form-status");
  var started = form.querySelector('input[name="t"]');
  if (started) started.value = String(Date.now());

  var messages = {
    naam: "Vul je naam in.",
    email: "Vul een geldig e-mailadres in, bijvoorbeeld naam@voorbeeld.nl.",
    postcode: "Vul een geldige postcode in, bijvoorbeeld 1234 AB.",
    bericht: "Vertel kort waar we je mee kunnen helpen (minimaal 10 tekens)."
  };

  function setError(name, msg) {
    var input = form.elements[name];
    if (!input) return;
    var field = input.closest(".field");
    var err = field.querySelector(".err");
    if (msg) {
      field.setAttribute("data-invalid", "");
      input.setAttribute("aria-invalid", "true");
      if (err) { err.textContent = msg; err.hidden = false; }
    } else {
      field.removeAttribute("data-invalid");
      input.removeAttribute("aria-invalid");
      if (err) { err.textContent = ""; err.hidden = true; }
    }
  }

  function validate() {
    var ok = true, first = null;
    var v = function (n) { return (form.elements[n].value || "").trim(); };
    var checks = {
      naam: v("naam").length >= 2,
      email: /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v("email")),
      postcode: /^[1-9][0-9]{3}\s?[a-zA-Z]{2}$/.test(v("postcode")),
      bericht: v("bericht").length >= 10
    };
    Object.keys(checks).forEach(function (k) {
      setError(k, checks[k] ? "" : messages[k]);
      if (!checks[k]) { ok = false; if (!first) first = form.elements[k]; }
    });
    if (first) first.focus();
    return ok;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.hidden = true;
    if (!validate()) return;

    var btn = form.querySelector('button[type="submit"]');
    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = "Bezig met versturen…";

    fetch(form.action, {
      method: "POST",
      headers: { "Accept": "application/json" },
      body: new URLSearchParams(new FormData(form))
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (res.ok) { window.location.href = "/bedankt"; return; }
        if (res.d && res.d.fields) Object.keys(res.d.fields).forEach(function (k) { setError(k, res.d.fields[k]); });
        throw new Error((res.d && res.d.error) || "Versturen is niet gelukt.");
      })
      .catch(function (err) {
        status.className = "form-status is-error";
        status.textContent = err.message + " Probeer het opnieuw of mail ons op info@atenergysolutions.nl.";
        status.hidden = false;
        btn.disabled = false;
        btn.textContent = label;
      });
  });
})();

/* Productmenu (dropdown) */
(function () {
  var btn = document.querySelector(".sub-toggle");
  if (!btn) return;
  var sub = document.getElementById(btn.getAttribute("aria-controls"));
  var set = function (o) { btn.setAttribute("aria-expanded", String(o)); sub.classList.toggle("is-open", o); };
  btn.addEventListener("click", function () { set(btn.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".has-sub")) set(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && sub.classList.contains("is-open")) { set(false); btn.focus(); } });
  btn.parentElement.addEventListener("focusout", function (e) { if (!btn.parentElement.contains(e.relatedTarget)) set(false); });
})();

/* Rekentool: hoogte van de ingeladen rekentool automatisch aanpassen */
(function () {
  var frame = document.getElementById("rekentool");
  if (!frame) return;
  window.addEventListener("message", function (e) {
    if (e.origin !== location.origin || !e.data || typeof e.data.rekentoolHoogte !== "number") return;
    frame.style.minHeight = "0";
    frame.style.height = Math.ceil(e.data.rekentoolHoogte) + "px";
  });
})();
