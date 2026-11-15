"""Cek statis situs (hasil/situs/): anggaran ukuran, referensi lokal, URL eksternal,
heuristik innerHTML dan kata Inggris. Galat membuat keluaran 1; peringatan tidak."""
import gzip
import os
import re
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITUS = os.path.join(AKAR, "hasil", "situs")
BATAS_GZIP = 60 * 1024
BATAS_CSS = 18 * 1024
BATAS_SPRITE = 15 * 1024
HOST_BOLEH = ("openstreetmap.org", "www.w3.org")  # tile OSM, atribusi, namespace SVG
PEMBERSIH = ("esc(", "kartu(", "keadaan(", "kerangka(", "spanduk(", "ikon(", "lencanaUbah(",
             "metaSumber(", "sparkline(")
KATA_INGGRIS = re.compile(r"\b(loading|error|search|home|price|weather|retry|submit|cancel|"
                          r"click|please|settings|failed|close|today|yesterday|undefined)\b", re.I)
galat, peringatan = [], []


def baca(rel):
    with open(os.path.join(SITUS, rel), encoding="utf-8") as f:
        return f.read()


def berkas_js(awal_saja=False):
    hasil = []
    for akar, _, nama in os.walk(os.path.join(SITUS, "js")):
        for n in sorted(nama):
            if not n.endswith(".js"):
                continue
            rel = os.path.relpath(os.path.join(akar, n), SITUS).replace("\\", "/")
            if awal_saja and rel.startswith("js/tampilan/") and rel != "js/tampilan/beranda.js":
                continue
            hasil.append(rel)
    return hasil


def cek_ukuran():
    awal = ["index.html", "gaya.css"] + berkas_js(awal_saja=True)
    mentah = "".join(baca(r) for r in awal).encode("utf-8")
    gz = len(gzip.compress(mentah, 9))
    print("gzip awal: %d B dari %d berkas (batas %d)" % (gz, len(awal), BATAS_GZIP))
    if gz > BATAS_GZIP:
        galat.append("gzip awal melebihi batas")
    css = os.path.getsize(os.path.join(SITUS, "gaya.css"))
    print("gaya.css: %d B (batas %d)" % (css, BATAS_CSS))
    if css > BATAS_CSS:
        galat.append("gaya.css melebihi batas")
    sp = os.path.join(SITUS, "ikon", "sprite.svg")
    if os.path.exists(sp) and os.path.getsize(sp) > BATAS_SPRITE:
        galat.append("sprite.svg melebihi batas")
    if not os.path.exists(os.path.join(SITUS, "vendor", "VERSI.txt")):
        galat.append("vendor/VERSI.txt tidak ada")


def lokal_ada(dasar, ref):
    ref = ref.split("#")[0].split("?")[0]
    if not ref:
        return True
    return os.path.exists(os.path.normpath(os.path.join(dasar, ref)))


def cek_referensi():
    html = baca("index.html")
    for ref in re.findall(r'(?:src|href)="([^"]+)"', html):
        if re.match(r"(https?:|#|data:|mailto:|tel:)", ref) or ref.startswith("#"):
            continue
        if not lokal_ada(SITUS, ref):
            galat.append("index.html merujuk berkas yang tidak ada: " + ref)
    sprite = baca("ikon/sprite.svg") if os.path.exists(os.path.join(SITUS, "ikon", "sprite.svg")) else ""
    ada = set(re.findall(r'id="i-([a-z0-9-]+)"', sprite))
    dipakai = set(re.findall(r"#i-([a-z0-9-]+)", html))
    for rel in berkas_js():
        src = baca(rel)
        dasar = os.path.dirname(os.path.join(SITUS, rel))
        for ref in re.findall(r"""(?:from|import)\s*\(?\s*['"](\.[^'"$`]+)['"]""", src):
            if not lokal_ada(dasar, ref):
                galat.append("%s: import tidak ada: %s" % (rel, ref))
        for ref in re.findall(r"""['"]((?:vendor|ikon|data)/[^'"$`]+\.[a-z]+)['"]""", src):
            if not lokal_ada(SITUS, ref) and not ref.startswith("data/"):
                galat.append("%s: berkas tidak ada: %s" % (rel, ref))
        dipakai |= set(re.findall(r"ikon\('([a-z0-9-]+)'", src))
    if sprite:
        for n in sorted(dipakai - ada):
            galat.append("ikon tidak ada di sprite: " + n)


def cek_eksternal():
    berkas = ["index.html", "gaya.css"] + berkas_js()
    for rel in berkas:
        for host in re.findall(r"https?://([^/\s'\"`)<>:?#]+)", baca(rel)):
            if not any(host == h or host.endswith("." + h) for h in HOST_BOLEH):
                galat.append("%s: URL eksternal tidak diizinkan: %s" % (rel, host))


def cek_heuristik():
    for rel in berkas_js():
        src = baca(rel)
        for m in re.finditer(r"innerHTML\s*\+?=\s*([^;]*);", src, re.S):
            ekspr = m.group(1)
            if ("${" in ekspr or "+" in ekspr) and not any(p in ekspr for p in PEMBERSIH):
                baris = src[:m.start()].count("\n") + 1
                peringatan.append("%s:%d innerHTML dengan variabel tanpa esc(" % (rel, baris))
        teks = re.findall(r"""'([^'\n]{4,})'|"([^"\n]{4,})\"""", src)
        kandidat = [a or b for a, b in teks]
        for s in kandidat:
            if " " in s and not s.startswith("http") and KATA_INGGRIS.search(s):
                peringatan.append("%s: kemungkinan teks Inggris: %s" % (rel, s[:50]))
    for t in re.findall(r">([^<>{}]{4,})<", baca("index.html")):
        if " " in t.strip() and KATA_INGGRIS.search(t):
            peringatan.append("index.html: kemungkinan teks Inggris: " + t.strip()[:50])


def main():
    cek_ukuran()
    cek_referensi()
    cek_eksternal()
    cek_heuristik()
    for p in peringatan[:15]:
        print("PERINGATAN", p)
    for g in galat[:20]:
        print("GALAT", g)
    print("Ringkasan: %d galat, %d peringatan -> %s" %
          (len(galat), len(peringatan), "GAGAL" if galat else "LULUS"))
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
