// Pembangun HTML kecil: semua teks dari luar harus lewat esc().
import { kesegaran } from "./data.js";
import { persen, waktuRelatif } from "./format.js";

const PETA = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
/** esc(teks) -> teks aman untuk HTML */
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => PETA[c]);

/** ikon(nama, ukuran=20) -> <svg> yang merujuk ikon/sprite.svg#i-<nama> */
export const ikon = (nama, u = 20) =>
  `<svg class="ikon" width="${u}" height="${u}" aria-hidden="true"><use href="ikon/sprite.svg#i-${esc(nama)}"/></svg>`;

/** kartu({judul, ikon, isi (HTML), meta (HTML), kelas, id}) -> HTML kartu */
export function kartu({ judul, ikon: nm = "", isi = "", meta = "", kelas = "", id = "" }) {
  return `<article class="kartu ${esc(kelas)}"${id ? ` id="${esc(id)}"` : ""}>` +
    `<div class="kartu__kepala">${nm ? `<span class="kartu__ikon">${ikon(nm)}</span>` : ""}` +
    `<h2 class="kartu__judul">${esc(judul)}</h2></div>` +
    `<div class="kartu__isi">${isi}</div>` +
    (meta ? `<div class="kartu__meta">${meta}</div>` : "") + `</article>`;
}

/** lencanaUbah(persenUbah, desimal=1): naik ▲ (merah), turun ▼ (hijau), tetap – */
export function lencanaUbah(p, d = 1) {
  if (p == null || Number.isNaN(Number(p))) return `<span class="lencana lencana--tetap">–</span>`;
  const n = Number(p);
  if (Math.abs(n) < 0.05) return `<span class="lencana lencana--tetap">– ${persen(0, 0)}</span>`;
  const naik = n > 0;
  return `<span class="lencana lencana--${naik ? "naik" : "turun"}">${naik ? "▲" : "▼"} ${persen(Math.abs(n), d)}</span>`;
}

/** metaSumber(amplop, ambang): titik kesegaran, waktu, nama sumber, lencana CONTOH */
export function metaSumber(a, ambang) {
  const k = kesegaran(a, ambang);
  const waktu = waktuRelatif(a.diperbarui);
  const teks = k.tingkat === "basi" ? "Data " + waktu : "Diperbarui " + waktu;
  const sumber = (a.sumber || []).map((s) => esc(s.nama)).join(", ");
  return `<span class="segar segar--${k.tingkat}"></span><span>${esc(teks)}</span>` +
    (sumber ? `<span>· ${sumber}</span>` : "") +
    (a._salinan ? `<span>· salinan tersimpan</span>` : "") +
    (a.contoh ? `<span class="lencana lencana--contoh">CONTOH</span>` : "");
}

const IKON_KEADAAN = { kosong: "info", galat: "triangle-alert", luring: "cloud" };
/** keadaan(jenis: "kosong"|"galat"|"luring", judul, teks, coba=jenis==="galat") */
export function keadaan(jenis, judul, teks = "", coba = jenis === "galat") {
  return `<div class="keadaan keadaan--${esc(jenis)}">${ikon(IKON_KEADAAN[jenis] || "info", 32)}` +
    `<p class="keadaan__judul">${esc(judul)}</p>${teks ? `<p>${esc(teks)}</p>` : ""}` +
    (coba ? `<button class="tombol tombol--sekunder" type="button" data-ulang>Coba lagi</button>` : "") + `</div>`;
}

/** kerangka(jumlah=1, tinggi=96) -> blok skeleton */
export const kerangka = (n = 1, tinggi = 96) =>
  Array.from({ length: n }, () => `<div class="kerangka" aria-hidden="true" style="height:${Number(tinggi) | 0}px"></div>`).join("");

/** spanduk(jenis: "info"|"peringatan"|"bahaya", teks) */
export const spanduk = (jenis, teks) =>
  `<div class="spanduk spanduk--${esc(jenis)}" role="status">${ikon(jenis === "info" ? "info" : "triangle-alert")}<span>${esc(teks)}</span></div>`;

// ---- Lembar bawah dan toast ----
const wadah = document.getElementById("lembar");
let pemicu = null;

/** bukaLembar(judul, isiHtml) -> elemen .lembar. Tutup: Esc, ketuk latar, atau tombol ×. */
export function bukaLembar(judul, isi) {
  pemicu = document.activeElement;
  wadah.innerHTML = `<div class="lembar" role="dialog" aria-modal="true" aria-labelledby="lembar-judul">` +
    `<div class="lembar__kepala"><h2 class="lembar__judul" id="lembar-judul">${esc(judul)}</h2>` +
    `<button class="tombol tombol--ikon" type="button" data-tutup aria-label="Tutup">${ikon("x")}</button></div>${isi}</div>`;
  wadah.hidden = false;
  document.body.style.overflow = "hidden";
  const p = wadah.querySelector(".lembar");
  (p.querySelector("input") || p.querySelector("button")).focus();
  return p;
}

export function tutupLembar() {
  if (wadah.hidden) return;
  wadah.hidden = true;
  wadah.innerHTML = "";
  document.body.style.overflow = "";
  if (pemicu && pemicu.focus) pemicu.focus();
}

if (wadah) {
  wadah.addEventListener("click", (e) => {
    if (e.target === wadah || e.target.closest("[data-tutup]")) tutupLembar();
  });
  document.addEventListener("keydown", (e) => {
    if (wadah.hidden) return;
    if (e.key === "Escape") return tutupLembar();
    if (e.key !== "Tab") return;
    const f = [...wadah.querySelectorAll("button,input,a[href]")].filter((x) => !x.disabled);
    if (!f.length) return;
    const awal = f[0], akhir = f[f.length - 1];
    if (e.shiftKey && document.activeElement === awal) { e.preventDefault(); akhir.focus(); }
    else if (!e.shiftKey && document.activeElement === akhir) { e.preventDefault(); awal.focus(); }
  });
}

let waktuToast = 0;
/** toast(teks): tampil 3 detik di atas nav. */
export function toast(teks) {
  const el = document.getElementById("toast");
  el.textContent = teks;
  el.classList.add("tampil");
  clearTimeout(waktuToast);
  waktuToast = setTimeout(() => el.classList.remove("tampil"), 3000);
}
