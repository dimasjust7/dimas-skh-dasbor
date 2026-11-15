// Pemformat angka, tanggal, dan waktu (lokal id-ID, zona WIB).
const ID = "id-ID";
const ZONA = "Asia/Jakarta";
const kosong = (n) => n == null || Number.isNaN(Number(n));

/** angka(n, desimal=0) -> "1.234,5" */
export const angka = (n, d = 0) =>
  kosong(n) ? "–" : Number(n).toLocaleString(ID, { minimumFractionDigits: d, maximumFractionDigits: d });

/** rupiah(n) -> "Rp 14.900" */
export const rupiah = (n) => (kosong(n) ? "–" : "Rp " + angka(Math.round(n)));

/** persen(n, desimal=1) -> "4,7%" (tanpa tanda; tanda ditangani lencanaUbah) */
export const persen = (n, d = 1) => (kosong(n) ? "–" : angka(n, d) + "%");

/** tanggal(iso, opsi) -> "15 November 2026" */
export function tanggal(iso, opsi = { day: "numeric", month: "long", year: "numeric" }) {
  const t = new Date(iso);
  return Number.isNaN(t.getTime()) ? "–" : t.toLocaleDateString(ID, { timeZone: ZONA, ...opsi });
}

/** waktuRelatif(iso, sekarang) -> "5 menit lalu" */
export function waktuRelatif(iso, sekarang = Date.now()) {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return "–";
  const d = (sekarang - t) / 1000;
  if (d < 60) return "baru saja";
  if (d < 3600) return Math.floor(d / 60) + " menit lalu";
  if (d < 86400) return Math.floor(d / 3600) + " jam lalu";
  if (d < 30 * 86400) return Math.floor(d / 86400) + " hari lalu";
  return tanggal(iso);
}

/** wib(iso) -> "15 Nov 2026, 23.57 WIB" */
export function wib(iso) {
  const t = new Date(iso);
  if (Number.isNaN(t.getTime())) return "–";
  const s = t.toLocaleString(ID, {
    timeZone: ZONA, day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", hour12: false,
  });
  return s + " WIB";
}
