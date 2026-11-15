// Pemuat malas Leaflet. Peta SVG kecamatan ditambahkan di T3.
import { muatSkrip, muatCss } from "./data.js";

export const UBIN = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
export const ATRIBUSI = "&copy; kontributor OpenStreetMap";

/** muatLeaflet() -> objek L (CSS dan JS dimuat saat pertama dipanggil). */
export async function muatLeaflet() {
  if (!window.L) {
    muatCss("vendor/leaflet/leaflet.css");
    await muatSkrip("vendor/leaflet/leaflet.js");
  }
  return window.L;
}
