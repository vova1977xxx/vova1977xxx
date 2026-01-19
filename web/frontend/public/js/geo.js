(async () => {
  try {
    const r = await fetch("/geo", { cache: "no-store" });
    const j = await r.json();
    const el = document.getElementById("geoCity");
    if (el) el.textContent = (j.city ? j.city + ", " : "") + (j.country || "");
  } catch (e) {}
})();
