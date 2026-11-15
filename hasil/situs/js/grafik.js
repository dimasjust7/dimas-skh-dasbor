// Sparkline SVG dan pemuat malas Chart.js.
import { muatSkrip } from "./data.js";

const WARNA = { naik: "var(--bahaya)", turun: "var(--sukses)", tetap: "var(--teks-2)" };

/** sparkline(nilai[], {lebar=96, tinggi=28, arah}) -> SVG; warna menurut arah perubahan
 *  (naik = merah, turun = hijau, karena bagi pembeli harga naik itu buruk). */
export function sparkline(nilai, { lebar = 96, tinggi = 28, arah } = {}) {
  const v = (nilai || []).filter((n) => typeof n === "number" && !Number.isNaN(n));
  if (v.length < 2) return "";
  const min = Math.min(...v), rentang = Math.max(...v) - min || 1, p = 2;
  const titik = v.map((n, i) => [p + (i * (lebar - 2 * p)) / (v.length - 1), tinggi - p - ((n - min) / rentang) * (tinggi - 2 * p)]);
  const a = arah || (v[v.length - 1] > v[0] ? "naik" : v[v.length - 1] < v[0] ? "turun" : "tetap");
  const [x, y] = titik[titik.length - 1];
  return `<svg class="sparkline" width="${lebar}" height="${tinggi}" viewBox="0 0 ${lebar} ${tinggi}" role="img" aria-label="Tren ${a}">` +
    `<polyline fill="none" stroke="${WARNA[a]}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="${titik.map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" ")}"/>` +
    `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" fill="${WARNA[a]}"/></svg>`;
}

/** muatChart() -> kelas Chart (dimuat malas dari vendor/chartjs/). */
export async function muatChart() {
  if (!window.Chart) await muatSkrip("vendor/chartjs/chart.umd.js");
  return window.Chart;
}
