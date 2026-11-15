"""Fungsi bersama untuk semua skrip dasbor_sukoharjo (hanya stdlib)."""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_STATUS = os.path.join(AKAR, "hasil", "situs", "data", "status.json")
URL_REPO = os.environ.get("URL_REPO", "https://github.com/OWNER/dasbor_sukoharjo")
USER_AGENT = "DasborSukoharjo/1.0 (+%s)" % URL_REPO
TIMEOUT = 20
JEDA_ULANG = (2, 4, 8)
JEDA_HOST = 1.5

_terakhir_host = {}


def sekarang_wib():
    """Waktu sekarang di WIB (UTC+7), sadar zona waktu."""
    return datetime.now(WIB)


def _tunggu_host(url):
    host = urllib.parse.urlparse(url).netloc
    selisih = time.monotonic() - _terakhir_host.get(host, -1e9)
    if selisih < JEDA_HOST:
        time.sleep(JEDA_HOST - selisih)
    _terakhir_host[host] = time.monotonic()


def ambil_teks(url, params=None, metode="GET", data=None, header=None):
    """Ambil teks dari URL. Coba ulang 3 kali (jeda 2, 4, 8 detik). Error terakhir dilempar."""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    badan = None
    if data is not None:
        if isinstance(data, dict):
            badan = urllib.parse.urlencode(data).encode("utf-8")
        elif isinstance(data, str):
            badan = data.encode("utf-8")
        else:
            badan = data
    kepala = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if badan is not None and metode.upper() == "POST":
        kepala["Content-Type"] = "application/x-www-form-urlencoded"
    if header:
        kepala.update(header)
    galat = None
    for percobaan in range(len(JEDA_ULANG) + 1):
        try:
            _tunggu_host(url)
            req = urllib.request.Request(url, data=badan, headers=kepala, method=metode.upper())
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError, UnicodeDecodeError) as e:
            galat = e
            if percobaan < len(JEDA_ULANG):
                time.sleep(JEDA_ULANG[percobaan])
    raise galat


def ambil_json(url, params=None, metode="GET", data=None, header=None):
    """Seperti ambil_teks, hasilnya di-parse sebagai JSON."""
    return json.loads(ambil_teks(url, params, metode, data, header))


def amplop(modul, data, sumber, status, catatan=""):
    """Bungkus data sesuai amplop bersama (rencana 6.4.1)."""
    return {
        "versi_skema": 1,
        "modul": modul,
        "diperbarui": sekarang_wib().isoformat(timespec="seconds"),
        "status": status,
        "catatan": catatan,
        "sumber": sumber,
        "contoh": False,
        "data": data,
    }


def tulis_json(path, obj):
    """Tulis JSON ringkas secara atomik (.tmp lalu os.replace), UTF-8 tanpa BOM."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, path)


def baca_json(path, bawaan=None):
    """Baca JSON; kembalikan `bawaan` bila berkas tidak ada atau rusak."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return bawaan


def ambil_versi_live(nama):
    """Ambil SITUS_URL/data/<nama>.json (versi yang sedang tayang). None bila gagal/tak diset."""
    dasar = os.environ.get("SITUS_URL", "").rstrip("/")
    if not dasar:
        return None
    try:
        return ambil_json("%s/data/%s.json" % (dasar, nama))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


def catat_status(modul, status, pesan="", ambang=None, path=PATH_STATUS):
    """Perbarui entri modul di status.json (rencana 6.4.2)."""
    sekarang = sekarang_wib().isoformat(timespec="seconds")
    isi = baca_json(path, None) or {"versi_skema": 1, "modul": {}}
    isi["dibangun"] = sekarang
    isi["pemicu"] = os.environ.get("GITHUB_EVENT_NAME", "lokal")
    lama = isi.setdefault("modul", {}).get(modul, {})
    sukses = sekarang if status in ("ok", "sebagian") else lama.get("terakhir_sukses")
    isi["modul"][modul] = {
        "status": status,
        "terakhir_sukses": sukses,
        "terakhir_coba": sekarang,
        "pesan": pesan,
        "ambang_jam": list(ambang) if ambang else lama.get("ambang_jam"),
    }
    tulis_json(path, isi)
    return isi["modul"][modul]
