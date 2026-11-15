"""Unduh pustaka front-end ke hasil/situs/vendor/ dan susun ikon/sprite.svg.

Leaflet 1.9.4 (unpkg), Chart.js 4.x UMD (jsDelivr, versi dikunci dari listing),
ikon Lucide (lucide-static, versi dikunci dari listing). Mencatat versi dan sha256
di vendor/VERSI.txt. Hanya stdlib.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITUS = os.path.join(AKAR, "hasil", "situs")
VENDOR = os.path.join(SITUS, "vendor")
LEAFLET = "https://unpkg.com/leaflet@1.9.4/dist/"
GAMBAR_LEAFLET = ["layers.png", "layers-2x.png", "marker-icon.png",
                  "marker-icon-2x.png", "marker-shadow.png"]
IKON = ("house shopping-basket cloud-sun map life-buoy search sun moon cloud cloud-rain "
        "cloud-drizzle cloud-lightning cloud-fog haze wind droplets thermometer trending-up "
        "trending-down minus triangle-alert info clock map-pin navigation phone external-link "
        "chevron-right chevron-down x refresh-cw activity leaf sunrise sunset moon-star "
        "calendar hospital pill graduation-cap bus train-front store briefcase fuel landmark "
        "share-2 locate").split()
# Pengganti bila nama tidak ada di paket.
GANTI = {"triangle-alert": "alert-triangle", "haze": "cloud-fog", "locate": "crosshair",
         "train-front": "train", "moon-star": "moon", "hospital": "building-2",
         "share-2": "share", "life-buoy": "lifebuoy"}
UA = {"User-Agent": "dasbor-sukoharjo-vendor/1.0"}
CATATAN = []


def unduh(url, coba=2):
    """Ambil byte dari url; gagal setelah `coba` percobaan mengembalikan None."""
    for i in range(coba):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            galat = str(e)
            time.sleep(1)
    CATATAN.append("GAGAL %s: %s" % (url, galat))
    return None


def tulis(path, isi):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(isi)


def sha(isi):
    return hashlib.sha256(isi).hexdigest()


def versi_terbaru(paket, awalan=""):
    """Versi terbaru paket npm dari listing jsDelivr (opsional dibatasi awalan)."""
    b = unduh("https://data.jsdelivr.com/v1/packages/npm/" + paket)
    if not b:
        return None
    j = json.loads(b.decode("utf-8"))
    daftar = []
    for v in j.get("versions", []):
        daftar.append(v["version"] if isinstance(v, dict) else v)
    if not awalan and j.get("tags", {}).get("latest"):
        return j["tags"]["latest"]
    for v in daftar:  # urut terbaru dulu
        if v.startswith(awalan) and "-" not in v:
            return v
    return None


def ambil_leaflet(baris):
    for nama in ("leaflet.js", "leaflet.css"):
        b = unduh(LEAFLET + nama)
        if b:
            tulis(os.path.join(VENDOR, "leaflet", nama), b)
            baris.append("leaflet 1.9.4 %s sha256=%s" % (nama, sha(b)))
    for nama in GAMBAR_LEAFLET:
        b = unduh(LEAFLET + "images/" + nama, coba=1)
        if b:
            tulis(os.path.join(VENDOR, "leaflet", "images", nama), b)
            baris.append("leaflet 1.9.4 images/%s sha256=%s" % (nama, sha(b)))
        else:
            CATATAN.append("Gambar Leaflet dilewati: " + nama)


def ratakan(simpul, awalan):
    """Ratakan pohon berkas jsDelivr (direktori bersarang atau daftar datar)."""
    hasil = []
    for x in simpul:
        nama = x["name"] if x["name"].startswith("/") else awalan + "/" + x["name"]
        if x.get("type") == "directory":
            hasil += ratakan(x.get("files", []), nama)
        else:
            hasil.append(nama)
    return hasil


def ambil_chart(baris):
    b = unduh("https://data.jsdelivr.com/v1/packages/npm/chart.js")
    if not b:
        return
    semua = [x["version"] for x in json.loads(b.decode("utf-8")).get("versions", [])]
    kandidat = [x for x in semua if x.startswith("4.") and "-" not in x][:8]
    v = pilih = None
    for k in kandidat:
        b = unduh("https://data.jsdelivr.com/v1/packages/npm/chart.js@" + k)
        berkas = ratakan(json.loads(b.decode("utf-8")).get("files", []), "") if b else []
        pilih = next((n for n in ("/dist/chart.umd.min.js", "/dist/chart.umd.js")
                      if n in berkas), None)
        if pilih:
            v = k
            break
        CATATAN.append("Chart.js %s tanpa berkas UMD di listing; dilewati" % k)
    if not pilih:
        return
    isi = unduh("https://cdn.jsdelivr.net/npm/chart.js@%s%s" % (v, pilih))
    if isi:
        tulis(os.path.join(VENDOR, "chartjs", "chart.umd.js"), isi)
        baris.append("chart.js %s (%s) -> chartjs/chart.umd.js sha256=%s" % (v, pilih, sha(isi)))


def bangun_sprite(baris):
    v = versi_terbaru("lucide-static")
    if not v:
        return False
    simbol, ganti, hilang = [], [], []
    for nama in IKON:
        b = unduh("https://unpkg.com/lucide-static@%s/icons/%s.svg" % (v, nama), coba=1)
        pakai = nama
        if b is None and nama in GANTI:
            b = unduh("https://unpkg.com/lucide-static@%s/icons/%s.svg" % (v, GANTI[nama]), coba=1)
            if b:
                pakai = GANTI[nama]
                ganti.append("%s->%s" % (nama, pakai))
        if b is None:
            hilang.append(nama)
            continue
        s = b.decode("utf-8")
        s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
        dalam = re.search(r"<svg[^>]*>(.*)</svg>", s, flags=re.S).group(1)
        dalam = re.sub(r">\s+<", "><", dalam.strip())
        simbol.append('<symbol id="i-%s" viewBox="0 0 24 24">%s</symbol>' % (nama, dalam))
    if len(simbol) < 10:
        return False
    sprite = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">'
              + "".join(simbol) + "</svg>")
    tulis(os.path.join(SITUS, "ikon", "sprite.svg"), sprite.encode("utf-8"))
    baris.append("lucide-static %s -> ikon/sprite.svg (%d ikon, %d byte) sha256=%s" %
                 (v, len(simbol), len(sprite.encode("utf-8")), sha(sprite.encode("utf-8"))))
    if ganti:
        baris.append("pengganti ikon: " + ", ".join(ganti))
    if hilang:
        baris.append("ikon tidak ada: " + ", ".join(hilang))
    return True


def main():
    baris = []
    ambil_leaflet(baris)
    ambil_chart(baris)
    ok = bangun_sprite(baris)
    if not ok:
        CATATAN.append("Sprite gagal diunduh: buat 10 ikon inti manual.")
    baris += ["CATATAN: " + c for c in CATATAN]
    tulis(os.path.join(VENDOR, "VERSI.txt"), ("\n".join(baris) + "\n").encode("utf-8"))
    print("\n".join(b[:140] for b in baris))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
