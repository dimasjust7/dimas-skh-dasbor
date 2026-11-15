// Titik masuk: router hash, kecamatan, tema, lembar pemilih kecamatan.
import { KECAMATAN, rute, muat } from "./data.js";
import { esc, ikon, keadaan, kerangka, spanduk, bukaLembar, tutupLembar, toast } from "./komponen.js";

const NAMA = { beranda: "Beranda", harga: "Harga", cuaca: "Cuaca", wilayah: "Wilayah", layanan: "Layanan", tentang: "Tentang", status: "Status", cari: "Cari" };
const TAMPILAN = { "": "beranda", harga: "harga", cuaca: "cuaca", wilayah: "wilayah", layanan: "layanan", tentang: "tentang", status: "status", cari: "cari" };
const isi = document.getElementById("isi");
let nomor = 0;

/** Kecamatan aktif: ?kec= di hash (disimpan), kalau tidak ada pakai localStorage. */
export function kecamatanAktif() {
  const ada = (s) => KECAMATAN.some((k) => k.slug === s);
  const q = rute().param.kec;
  try {
    if (ada(q)) { localStorage.setItem("kec", q); return q; }
    const s = localStorage.getItem("kec");
    return ada(s) ? s : null;
  } catch (e) { return ada(q) ? q : null; }
}

// ---- Tautan: parameter contoh dan tema ikut terbawa antarhalaman ----
function bawa() {
  const q = rute().param;
  return ["contoh", "tema"].filter((k) => q[k]).map((k) => k + "=" + encodeURIComponent(q[k])).join("&");
}
const href = (r) => "#/" + r + (bawa() ? "?" + bawa() : "");

function sinkronNav(nama) {
  document.querySelectorAll("[data-rute]").forEach((a) => {
    const r = a.dataset.rute;
    a.href = href(r === "beranda" ? "" : r);
    if (r === nama) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
}

// ---- Tema ----
const temaSekarang = () => document.documentElement.dataset.tema ||
  (matchMedia("(prefers-color-scheme: dark)").matches ? "gelap" : "terang");

function tampilkanTema() {
  const gelap = temaSekarang() === "gelap";
  const t = document.getElementById("tombol-tema");
  t.innerHTML = ikon(gelap ? "sun" : "moon");
  t.setAttribute("aria-label", gelap ? "Ganti ke tema terang" : "Ganti ke tema gelap");
}

function gantiTema() {
  const baru = temaSekarang() === "gelap" ? "terang" : "gelap";
  document.documentElement.dataset.tema = baru;
  try { localStorage.setItem("tema", baru); } catch (e) { /* abaikan */ }
  tampilkanTema();
}

// ---- Kecamatan ----
function perbaruiChip() {
  const k = KECAMATAN.find((x) => x.slug === kecamatanAktif());
  document.getElementById("tombol-kec").innerHTML =
    ikon("map-pin", 16) + `<span>${k ? "Kec. " + esc(k.nama) : "Pilih kecamatan"}</span>` + ikon("chevron-down", 16);
}

function pilihKecamatan() {
  const p = bukaLembar("Pilih kecamatan",
    `<input class="isian" id="cari-kec" type="search" placeholder="Cari kecamatan" aria-label="Cari kecamatan" autocomplete="off">` +
    `<ul class="daftar" id="daftar-kec"></ul>`);
  const ul = p.querySelector("#daftar-kec"), inp = p.querySelector("#cari-kec");
  const gambar = () => {
    const q = inp.value.trim().toLowerCase(), aktif = kecamatanAktif();
    const h = KECAMATAN.filter((k) => k.nama.toLowerCase().includes(q));
    ul.innerHTML = h.length
      ? h.map((k) => `<li><button class="baris${k.slug === aktif ? " baris--pilih" : ""}" type="button" data-slug="${esc(k.slug)}">` +
          `<span class="baris__teks">${esc(k.nama)}</span>${k.slug === aktif ? `<span class="lencana lencana--info">Dipilih</span>` : ""}</button></li>`).join("")
      : `<li>${keadaan("kosong", "Kecamatan tidak ditemukan")}</li>`;
  };
  inp.addEventListener("input", gambar);
  ul.addEventListener("click", (e) => {
    const b = e.target.closest("[data-slug]");
    if (!b) return;
    const k = KECAMATAN.find((x) => x.slug === b.dataset.slug);
    try { localStorage.setItem("kec", k.slug); } catch (_) { /* abaikan */ }
    const [jalur, q = ""] = (location.hash.replace(/^#/, "") || "/").split("?");
    const u = new URLSearchParams(q);
    tutupLembar();
    toast("Kecamatan: " + k.nama);
    if (u.has("kec")) { u.set("kec", k.slug); location.hash = "#" + jalur + "?" + u; } else render();
  });
  gambar();
}

// ---- Router ----
async function render() {
  const saya = ++nomor;
  const { segmen, param } = rute();
  document.body.dataset.siap = "0";
  if (param.tema === "gelap" || param.tema === "terang") document.documentElement.dataset.tema = param.tema;
  tampilkanTema();
  perbaruiChip();
  const nama = TAMPILAN[segmen[0] || ""];
  sinkronNav(nama || "");
  if (!nama) {
    document.title = "Tidak ditemukan · Dasbor Sukoharjo";
    isi.innerHTML = keadaan("kosong", "Halaman tidak ditemukan", "Alamat yang dibuka tidak ada.");
    document.body.dataset.siap = "1";
    return;
  }
  document.title = NAMA[nama] + " · Dasbor Sukoharjo";
  isi.innerHTML = kerangka(3);
  let modul = null;
  try { modul = await import(`./tampilan/${nama}.js`); } catch (e) { modul = null; }
  if (saya !== nomor) return;
  try {
    if (modul && modul.render) {
      await modul.render(isi, { rute: segmen.slice(1), param, kec: kecamatanAktif(), muat, ulang: render });
    } else {
      isi.innerHTML = `<h1 class="judul-halaman">${esc(NAMA[nama])}</h1>` + keadaan("kosong", "Segera hadir", "Halaman ini sedang disiapkan.");
    }
  } catch (e) {
    if (saya !== nomor) return;
    console.error(e);
    isi.innerHTML = keadaan("galat", "Gagal menampilkan halaman", "Terjadi kesalahan saat memuat data.");
  }
  if (saya !== nomor) return;
  window.scrollTo(0, 0);
  document.body.dataset.siap = "1";
}

function statusLuring() {
  document.getElementById("spanduk").innerHTML = navigator.onLine ? ""
    : spanduk("peringatan", "Anda sedang luring. Data yang tampil adalah salinan terakhir.");
}

document.getElementById("tombol-kec").addEventListener("click", pilihKecamatan);
document.getElementById("tombol-tema").addEventListener("click", gantiTema);
document.getElementById("tombol-cari").addEventListener("click", () => { location.hash = href("cari"); });
isi.addEventListener("click", (e) => { if (e.target.closest("[data-ulang]")) render(); });
addEventListener("hashchange", render);
addEventListener("online", statusLuring);
addEventListener("offline", statusLuring);
statusLuring();
render();
