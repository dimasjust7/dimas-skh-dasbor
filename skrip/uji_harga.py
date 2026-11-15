"""Uji jalur harga A1: Panel Harga Bapanas tingkat kabupaten, level Konsumen (level_harga_id=3).

Meniru permintaan dari tangkapan pemilik (referensi/harga/panelharga_sukoharjo.txt):
tanpa Cookie/Authorization, maksimal 2 percobaan. Hasil dinormalisasi ke skema 6.4.7
dan ditulis ke _tmp/contoh_harga.json.

Pemakaian:
  python skrip/uji_harga.py            # panggil API
  python skrip/uji_harga.py --berkas   # pakai respons tangkapan pemilik (tanpa jaringan)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
URL = ("https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-informasi"
       "?province_id=13&city_id=196&level_harga_id=3")
HEADER = {
    "Accept": "application/json",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
    "Origin": "https://panelharga.badanpangan.go.id",
    "Referer": "https://panelharga.badanpangan.go.id/",
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"),
}
BERKAS_TANGKAPAN = "referensi/harga/panelharga_konsumen_respons.json"
KELUARAN = "_tmp/contoh_harga.json"
BULAN = {"januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
         "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12}

# id_sumber -> (id internal, kategori, satuan). Sama dengan data/peta_komoditas.csv.
PETA = {
    27: ("beras_premium", "pokok", "kg"),
    28: ("beras_medium", "pokok", "kg"),
    109: ("beras_sphp", "pokok", "kg"),
    165: ("beras_medium_non_sphp", "pokok", "kg"),
    102: ("jagung_peternak", "pokok", "kg"),
    29: ("kedelai_impor", "pokok", "kg"),
    40: ("tepung_terigu_curah", "pokok", "kg"),
    108: ("tepung_terigu_kemasan", "pokok", "kg"),
    30: ("bawang_merah", "bumbu", "kg"),
    31: ("bawang_putih", "bumbu", "kg"),
    32: ("cabai_merah_keriting", "bumbu", "kg"),
    126: ("cabai_merah_besar", "bumbu", "kg"),
    33: ("cabai_rawit_merah", "bumbu", "kg"),
    107: ("garam", "bumbu", "kg"),
    34: ("daging_sapi", "protein", "kg"),
    35: ("daging_ayam_ras", "protein", "kg"),
    36: ("telur_ayam_ras", "protein", "kg"),
    104: ("ikan_kembung", "protein", "kg"),
    105: ("ikan_tongkol", "protein", "kg"),
    106: ("ikan_bandeng", "protein", "kg"),
    37: ("gula_pasir", "minyak_gula", "kg"),
    38: ("minyak_goreng_kemasan", "minyak_gula", "liter"),
    101: ("minyak_goreng_curah", "minyak_gula", "liter"),
    127: ("minyakita", "minyak_gula", "liter"),
}
# 8 komoditas inti Beranda (rencana 5.3)
INTI = ["beras_medium", "cabai_rawit_merah", "cabai_merah_keriting", "bawang_merah",
        "bawang_putih", "telur_ayam_ras", "minyak_goreng_kemasan", "gula_pasir"]


def ambil(percobaan=2):
    """Satu permintaan GET; ulangi sekali bila gagal. Mengembalikan (json, catatan)."""
    catatan = []
    for i in range(1, percobaan + 1):
        try:
            req = urllib.request.Request(URL, headers=HEADER, method="GET")
            with urllib.request.urlopen(req, timeout=30) as r:
                isi = r.read().decode("utf-8")
                catatan.append(f"percobaan {i}: HTTP {r.status}, {len(isi)} byte")
                return json.loads(isi), catatan
        except urllib.error.HTTPError as e:
            catatan.append(f"percobaan {i}: HTTP {e.code}")
        except Exception as e:  # jaringan, JSON rusak, dsb.
            catatan.append(f"percobaan {i}: {type(e).__name__}: {e}")
        time.sleep(3)
    return None, catatan


def tanggal_indonesia(teks):
    """'15 November 2026' -> '2026-11-15'."""
    h, b, t = teks.split()
    return date(int(t), BULAN[b.lower()], int(h)).isoformat()


def tanggal_strip(teks):
    """'14-11-2026' -> '2026-11-14'."""
    h, b, t = teks.split("-")
    return date(int(t), int(b), int(h)).isoformat()


def normalisasi(resp):
    """Ubah respons API ke skema 6.4.7. Komoditas bernilai 0 dianggap tidak ada data."""
    req = resp["request_data"][0]
    out = []
    for x in resp["data"]:
        if x["id"] not in PETA or not x.get("today"):
            continue
        id_int, kat, sat = PETA[x["id"]]
        out.append({
            "id": id_int, "nama": x["name"], "kategori": kat, "satuan": sat,
            "harga": x["today"], "harga_sebelumnya": x["yesterday"] or None,
            "tanggal_sebelumnya": tanggal_strip(x["yesterday_date"]),
            "ubah_persen": x["gap_percentage"],
            "rata_7h": None, "ubah_7h_persen": None, "acuan": None,
        })
    return {
        "tingkat": "kabupaten",
        "wilayah_label": req["nasional"],
        "label_peringatan": "",
        "tanggal_data": tanggal_indonesia(req["today"]),
        "komoditas": out,
    }


def periksa(data):
    """Kembalikan daftar masalah; kosong berarti lolos (>= 8 komoditas, harga > 0)."""
    m = []
    k = data["komoditas"]
    if len(k) < 8:
        m.append(f"komoditas {len(k)} < 8")
    ada = {x["id"] for x in k}
    m += [f"inti kosong: {i}" for i in INTI if i not in ada]
    m += [f"harga <= 0: {x['id']}" for x in k if not x["harga"] or x["harga"] <= 0]
    return m


def main():
    if "--berkas" in sys.argv:
        resp = json.load(open(BERKAS_TANGKAPAN, encoding="utf-8-sig"))
        catatan = ["sumber: berkas tangkapan pemilik"]
    else:
        resp, catatan = ambil()
    for c in catatan:
        print(c)
    if resp is None or resp.get("status") != "success":
        print("GAGAL: tidak ada respons valid")
        return 1
    data = normalisasi(resp)
    masalah = periksa(data)
    os.makedirs(os.path.dirname(KELUARAN), exist_ok=True)
    with open(KELUARAN, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"tingkat={data['tingkat']} wilayah={data['wilayah_label']} tanggal={data['tanggal_data']}")
    print(f"komoditas bernilai > 0: {len(data['komoditas'])} dari {len(resp['data'])}")
    for x in data["komoditas"][:3]:
        print(" ", x["id"], x["harga"], x["harga_sebelumnya"], x["ubah_persen"])
    print("riwayat: tidak ada di respons (hanya hari ini dan kemarin)")
    print("LOLOS" if not masalah else "TIDAK LOLOS: " + "; ".join(masalah))
    return 0 if not masalah else 2


if __name__ == "__main__":
    sys.exit(main())
