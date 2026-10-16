// Vercel Serverless Function — POST /api/contact
// Slaat aanvragen op in Supabase en/of mailt ze via Resend. Zet in Vercel (Settings → Environment Variables):
//   SUPABASE_URL               – bijv. https://xxxx.supabase.co
//   SUPABASE_SERVICE_ROLE_KEY  – geheime server-sleutel (nooit in de browser of in GitHub!)
//   RESEND_API_KEY, CONTACT_TO, CONTACT_FROM – optioneel: e-mailnotificatie
// Minstens één van beide (Supabase of Resend) moet ingesteld zijn.

const INTERESTS = ["zonnepanelen", "thuisbatterij", "warmtepomp", "airco", "anders"];
const TYPES = ["particulier", "zakelijk"];

const clean = (v, max) => String(v == null ? "" : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, " ").trim().slice(0, max);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function parse(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string") return Object.fromEntries(new URLSearchParams(req.body));
  return {};
}

async function saveToSupabase(data) {
  const { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, VERCEL_ENV } = process.env;
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return null; // niet geconfigureerd
  const r = await fetch(`${SUPABASE_URL.replace(/\/$/, "")}/rest/v1/aanvragen`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify({ ...data, omgeving: VERCEL_ENV || "development" }),
  });
  if (!r.ok) throw new Error(`Supabase ${r.status}`);
  return true;
}

async function sendMail(data) {
  const { RESEND_API_KEY, CONTACT_TO, CONTACT_FROM, VERCEL_ENV } = process.env;
  if (!RESEND_API_KEY || !CONTACT_TO || !CONTACT_FROM) return null;
  const rows = [["Naam", data.naam], ["E-mail", data.email], ["Telefoon", data.telefoon || "–"], ["Postcode", data.postcode],
    ["Type", data.type], ["Interesse", data.interesse.join(", ") || "–"]];
  const html = `<h2>Nieuwe aanvraag via de website</h2><table cellpadding="6">` +
    rows.map(([k, v]) => `<tr><td><strong>${k}</strong></td><td>${esc(v)}</td></tr>`).join("") +
    `</table><p><strong>Bericht</strong></p><p>${esc(data.bericht).replace(/\n/g, "<br>")}</p>`;
  const prefix = VERCEL_ENV && VERCEL_ENV !== "production" ? "[TEST] " : "";
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: CONTACT_FROM, to: [CONTACT_TO], reply_to: data.email,
      subject: `${prefix}Aanvraag ${data.type}: ${data.interesse.join(", ") || "algemeen"} – ${data.naam}`, html }),
  });
  if (!r.ok) throw new Error(`Resend ${r.status}`);
  return true;
}

module.exports = async function handler(req, res) {
  const wantsJson = String(req.headers.accept || "").includes("application/json");
  const reply = (code, payload, redirect) => {
    if (!wantsJson && redirect) { res.statusCode = 303; res.setHeader("Location", redirect); return res.end(); }
    res.status(code).json(payload);
  };
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return reply(405, { error: "Methode niet toegestaan." }); }

  const b = parse(req);
  if (clean(b.website, 200)) return reply(200, { ok: true }, "/bedankt"); // honeypot
  const t = Number(b.t);
  if (t && Date.now() - t < 3000) return reply(400, { error: "Het formulier werd te snel verstuurd." }, "/contact?fout=1");

  const data = {
    naam: clean(b.naam, 100),
    email: clean(b.email, 160).toLowerCase(),
    telefoon: clean(b.telefoon, 30) || null,
    postcode: clean(b.postcode, 8).toUpperCase().replace(/^(\d{4})\s?([A-Z]{2})$/, "$1 $2"),
    type: TYPES.includes(b.type) ? b.type : "particulier",
    interesse: [].concat(b.interesse || []).filter((i) => INTERESTS.includes(i)),
    bericht: clean(b.bericht, 3000),
  };

  const fields = {};
  if (data.naam.length < 2) fields.naam = "Vul je naam in.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) fields.email = "Vul een geldig e-mailadres in.";
  if (!/^[1-9][0-9]{3} [A-Z]{2}$/.test(data.postcode)) fields.postcode = "Vul een geldige postcode in.";
  if (data.bericht.length < 10) fields.bericht = "Vertel kort waar we je mee kunnen helpen.";
  if (data.telefoon && !/^[0-9+()\s-]{8,20}$/.test(data.telefoon)) fields.telefoon = "Vul een geldig telefoonnummer in.";
  if (Object.keys(fields).length) return reply(422, { error: "Controleer de gemarkeerde velden.", fields }, "/contact?fout=1");

  const results = await Promise.allSettled([saveToSupabase(data), sendMail(data)]);
  const ok = results.some((r) => r.status === "fulfilled" && r.value === true);
  results.forEach((r) => { if (r.status === "rejected") console.error("Contactformulier:", r.reason.message); }); // geen persoonsgegevens loggen
  if (ok) return reply(200, { ok: true }, "/bedankt");
  const configured = results.some((r) => r.status === "rejected");
  return reply(configured ? 502 : 500, { error: configured ? "Versturen is niet gelukt." : "Het formulier is nog niet geconfigureerd." }, "/contact?fout=1");
};
