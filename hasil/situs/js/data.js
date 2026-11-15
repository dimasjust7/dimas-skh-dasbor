// Pemuatan data JSON, kesegaran, mode contoh, dan pemuat skrip malas.
export const KECAMATAN = [
  ["weru", "Weru"], ["bulu", "Bulu"], ["tawangsari", "Tawangsari"], ["sukoharjo", "Sukoharjo"],
  ["nguter", "Nguter"], ["bendosari", "Bendosari"], ["polokarto", "Polokarto"],
  ["mojolaban", "Mojolaban"], ["grogol", "Grogol"], ["baki", "Baki"], ["gatak", "Gatak"],
  ["kartasura", "Kartasura"],
].map(([slug, nama]) => ({ slug, nama }));

/** Baca rute dan query dari hash: "#/harga/x?contoh=1" -> {segmen:["harga","x"], param:{contoh:"1"}} */
export function rute() {
  const h = location.hash.replace(/^#/, "") || "/";
  const [p, q = ""] = h.split("?");
  return { segmen: p.split("/").filter(Boolean), param: Object.fromEntries(new URLSearchParams(q)) };
}

export const modeContoh = () => rute().param.contoh === "1";

/** muat(nama) -> amplop JSON dari data/<nama>.json (atau data/contoh/ bila ?contoh=1).
 *  Jaringan gagal: pakai salinan localStorage (ditandai _salinan) bila ada, kalau tidak lempar galat. */
export async function muat(nama) {
  const contoh = modeContoh();
  const url = (contoh ? "data/contoh/" : "data/") + nama + ".json";
  const kunci = "dasbor:" + (contoh ? "contoh:" : "") + nama;
  try {
    const r = await fetch(url, { cache: "no-cache" });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    try { localStorage.setItem(kunci, JSON.stringify(j)); } catch (e) { /* penyimpanan penuh atau dimatikan */ }
    return j;
  } catch (e) {
    let salinan = null;
    try { salinan = JSON.parse(localStorage.getItem(kunci)); } catch (_) { /* abaikan */ }
    if (salinan) { salinan._salinan = true; return salinan; }
    throw e;
  }
}

/** kesegaran(amplop, ambang={segar:6, lama:36} dalam jam) -> {tingkat:"segar"|"lama"|"basi", jam} */
export function kesegaran(amplop, ambang = { segar: 6, lama: 36 }) {
  const t = Date.parse(amplop && amplop.diperbarui);
  if (Number.isNaN(t)) return { tingkat: "basi", jam: Infinity };
  const jam = (Date.now() - t) / 36e5;
  return { tingkat: jam <= ambang.segar ? "segar" : jam <= ambang.lama ? "lama" : "basi", jam };
}

const dimuat = {};
/** muatSkrip(src) -> Promise; setiap berkas dimuat sekali. */
export function muatSkrip(src) {
  if (!dimuat[src]) {
    dimuat[src] = new Promise((ok, gagal) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = ok;
      s.onerror = () => { delete dimuat[src]; gagal(new Error("Gagal memuat " + src)); };
      document.head.append(s);
    });
  }
  return dimuat[src];
}

/** muatCss(href): tambah stylesheet sekali. */
export function muatCss(href) {
  if (document.querySelector('link[href="' + href + '"]')) return;
  const l = document.createElement("link");
  l.rel = "stylesheet";
  l.href = href;
  document.head.append(l);
}
