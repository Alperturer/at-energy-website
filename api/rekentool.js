// Vercel Serverless Function — /api/rekentool
// GET  → huidige prijzen/modellen van de rekentool (uit Supabase)
// POST → nieuwe instellingen opslaan; vereist het beheerwachtwoord
//
// Omgevingsvariabelen in Vercel (Settings → Environment Variables):
//   SUPABASE_URL               – https://utlasambuxlkggwydnlv.supabase.co
//   SUPABASE_SERVICE_ROLE_KEY  – geheime server-sleutel uit Supabase (nooit in de browser of GitHub)
//   REKENTOOL_WACHTWOORD       – zelfgekozen wachtwoord voor het beheerscherm (minimaal 10 tekens)

const crypto = require("crypto");

const TABLE = "rekentool_instellingen";
const GROEPEN = { batterijen: "pakketten", panelen: "types", warmtepompen: "modellen", aircos: "modellen" };
const pogingen = new Map(); // eenvoudige rem op wachtwoord raden (per serverinstantie)

function supa(path, init = {}) {
  const { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY } = process.env;
  return fetch(`${SUPABASE_URL.replace(/\/$/, "")}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
}

function gelijk(a, b) {
  const x = crypto.createHash("sha256").update(String(a)).digest();
  const y = crypto.createHash("sha256").update(String(b)).digest();
  return crypto.timingSafeEqual(x, y);
}

function controleer(cfg) {
  if (!cfg || typeof cfg !== "object" || Array.isArray(cfg)) return "Ongeldige instellingen.";
  for (const k of ["btwBatterij", "btwPanelen", "btwWarmtepomp", "btwAirco"])
    if (typeof cfg[k] !== "number" || cfg[k] < 0 || cfg[k] > 1) return `Ongeldig btw-tarief: ${k}.`;
  for (const [g, lijst] of Object.entries(GROEPEN)) {
    if (typeof cfg[g] !== "object" || cfg[g] === null) return `Groep ontbreekt: ${g}.`;
    for (const m of Object.values(cfg[g])) {
      if (!m || typeof m.naam !== "string" || !Array.isArray(m[lijst])) return `Ongeldig merk in ${g}.`;
      for (const it of m[lijst]) if (typeof it.prijs !== "number" || it.prijs < 0 || it.prijs > 1e6) return `Ongeldige prijs bij ${m.naam}.`;
    }
  }
  if (typeof cfg.warmtefonds !== "object" || cfg.warmtefonds === null) return "Warmtefonds-gegevens ontbreken.";
  return null;
}

module.exports = async function handler(req, res) {
  const { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REKENTOOL_WACHTWOORD } = process.env;
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return res.status(503).json({ error: "Database is nog niet gekoppeld." });

  if (req.method === "GET") {
    const r = await supa(`${TABLE}?id=eq.1&select=config,updated_at`);
    if (!r.ok) return res.status(502).json({ error: "Prijzen konden niet worden geladen." });
    const rows = await r.json();
    if (!rows.length) return res.status(404).json({ error: "Nog geen instellingen opgeslagen." });
    res.setHeader("Cache-Control", "public, s-maxage=30, stale-while-revalidate=300");
    return res.status(200).json({ config: rows[0].config, bijgewerkt: rows[0].updated_at });
  }

  if (req.method === "POST") {
    if (!REKENTOOL_WACHTWOORD || REKENTOOL_WACHTWOORD.length < 10)
      return res.status(503).json({ error: "Stel eerst REKENTOOL_WACHTWOORD in bij Vercel (minimaal 10 tekens)." });
    const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0] || "?";
    const p = pogingen.get(ip) || { n: 0, t: Date.now() };
    if (Date.now() - p.t > 15 * 60 * 1000) { p.n = 0; p.t = Date.now(); }
    if (p.n >= 10) return res.status(429).json({ error: "Te veel pogingen. Probeer het over 15 minuten opnieuw." });

    const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : (req.body || {});
    if (!gelijk(body.wachtwoord || "", REKENTOOL_WACHTWOORD)) {
      p.n += 1; pogingen.set(ip, p);
      return res.status(401).json({ error: "Wachtwoord klopt niet." });
    }
    const fout = controleer(body.config);
    if (fout) return res.status(422).json({ error: fout });

    const r = await supa(`${TABLE}?on_conflict=id`, {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({ id: 1, config: body.config, updated_at: new Date().toISOString() }),
    });
    if (!r.ok) { console.error("Rekentool opslaan:", r.status); return res.status(502).json({ error: "Opslaan is niet gelukt." }); }
    return res.status(200).json({ ok: true });
  }

  res.setHeader("Allow", "GET, POST");
  return res.status(405).json({ error: "Methode niet toegestaan." });
};
