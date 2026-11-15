"""Uji jangkauan sumber data. Satu percobaan per URL, tanpa coba ulang.
Pakai: python skrip/uji_jaringan.py --keluaran <path>"""
import argparse
import os
import platform
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
UA = "DasborSukoharjo/1.0 (uji jaringan)"
OM = "latitude=-7.68&longitude=110.84"

# (label, metode, url, data)
DAFTAR = [
    ("bmkg_prakiraan", "GET", "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=33.11.01.2001", None),
    ("bmkg_autogempa", "GET", "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json", None),
    ("openmeteo_forecast", "GET", "https://api.open-meteo.com/v1/forecast?%s&hourly=temperature_2m" % OM, None),
    ("openmeteo_airquality", "GET", "https://air-quality-api.open-meteo.com/v1/air-quality?%s&hourly=pm2_5" % OM, None),
    ("overpass", "POST", "https://overpass-api.de/api/interpreter", "data=%5Bout%3Ajson%5D%3Bnode%281%29%3Bout%3B"),
    ("panel_harga", "GET", "https://api-panelhargav2.badanpangan.go.id/api/front/harga-peta-provinsi", None),
    ("pihps", "GET", "https://www.bi.go.id/hargapangan", None),
    ("wikipedia", "GET", "https://id.wikipedia.org/api/rest_v1/page/summary/Kabupaten_Sukoharjo", None),
]


def uji(label, metode, url, data):
    badan = data.encode("utf-8") if data else None
    kepala = {"User-Agent": UA, "Accept": "*/*"}
    if badan:
        kepala["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=badan, headers=kepala, method=metode)
    mulai = time.monotonic()
    kode, isi = "ERR", b""
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            kode, isi = r.status, r.read()
    except urllib.error.HTTPError as e:
        kode = e.code
        try:
            isi = e.read()
        except Exception:
            isi = b""
    except Exception as e:
        isi = ("%s: %s" % (type(e).__name__, e)).encode("utf-8")
    ms = int((time.monotonic() - mulai) * 1000)
    cuplik = isi[:100].decode("utf-8", "replace").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return "%s\t%s\t%d ms\t%d B\t%s" % (label, kode, ms, len(isi), cuplik)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keluaran", required=True)
    a = ap.parse_args()
    baris = ["# uji_jaringan %s | %s | python %s | GITHUB_ACTIONS=%s" % (
        datetime.now(WIB).isoformat(timespec="seconds"), platform.platform(),
        platform.python_version(), os.environ.get("GITHUB_ACTIONS", "tidak"))]
    baris.append("# label\tkode\twaktu\tukuran\t100 karakter pertama")
    for item in DAFTAR:
        b = uji(*item)
        print(b[:160])
        baris.append(b)
        time.sleep(1.5)
    os.makedirs(os.path.dirname(os.path.abspath(a.keluaran)), exist_ok=True)
    with open(a.keluaran, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(baris) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
