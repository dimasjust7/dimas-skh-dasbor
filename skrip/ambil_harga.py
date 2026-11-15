"""Ambil harga pangan Kab. Sukoharjo (Panel Harga Bapanas, level Konsumen).

Menulis hasil/situs/data/harga.json (6.4.7) dan harga_riwayat.json (6.4.8), lalu mencatat status.
Dijalankan dari PC pemilik (Rencana Jaringan B), karena Actions timeout ke API ini.

  python skrip/ambil_harga.py            # ambil dari API
  python skrip/ambil_harga.py --berkas   # pakai berkas tangkapan (uji tanpa jaringan)

Bila pengambilan atau validasi gagal, berkas lama TIDAK diubah dan status dicatat basi/gagal.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import umum
import uji_harga

DIR_DATA = os.path.join(umum.AKAR, "hasil", "situs", "data")
PATH_HARGA = os.path.join(DIR_DATA, "harga.json")
PATH_RIWAYAT = os.path.join(DIR_DATA, "harga_riwayat.json")
MAKS_HARI = 400
MIN_TITIK_7H = 3
SUMBER = [{
    "nama": "Panel Harga Badan Pangan Nasional",
    "url": "https://panelharga.badanpangan.go.id/",
    "lisensi": "Cantumkan Badan Pangan Nasional sebagai sumber",
}]


def perbarui_riwayat(riwayat, data):
    """Sisipkan harga hari ini ke riwayat (ganti bila tanggal sama), batasi MAKS_HARI titik."""
    seri = riwayat.setdefault("seri", {})
    tgl = data["tanggal_data"]
    for k in data["komoditas"]:
        titik = [t for t in seri.get(k["id"], []) if t[0] != tgl]
        titik.append([tgl, k["harga"]])
        titik.sort(key=lambda t: t[0])
        seri[k["id"]] = titik[-MAKS_HARI:]
    riwayat["tingkat"] = data["tingkat"]
    return riwayat


def hitung_7h(data, riwayat):
    """Isi rata_7h dan ubah_7h_persen dari 7 titik terakhir (minimal MIN_TITIK_7H)."""
    seri = riwayat.get("seri", {})
    for k in data["komoditas"]:
        harga7 = [t[1] for t in seri.get(k["id"], [])][-7:]
        if len(harga7) >= MIN_TITIK_7H:
            rata = sum(harga7) / len(harga7)
            k["rata_7h"] = round(rata)
            k["ubah_7h_persen"] = round((k["harga"] - rata) / rata * 100, 1)
    return data


def jalankan(pakai_berkas=False):
    lama = umum.baca_json(PATH_HARGA, None)
    try:
        if pakai_berkas:
            resp = umum.baca_json(uji_harga.BERKAS_TANGKAPAN, None)
            if resp is None:
                raise ValueError("berkas tangkapan tidak terbaca")
        else:
            resp = umum.ambil_json(uji_harga.URL, header=uji_harga.HEADER)
        if resp.get("status") != "success":
            raise ValueError("status respons: %r" % resp.get("status"))
        data = uji_harga.normalisasi(resp)
    except Exception as e:  # jaringan, JSON, skema berubah
        status = "basi" if lama else "gagal"
        umum.catat_status("harga", status, "%s: %s" % (type(e).__name__, e))
        print("GAGAL ambil: %s (%s)" % (e, status))
        return 1

    masalah = uji_harga.periksa(data)
    if len(data["komoditas"]) < 8 or any("harga <= 0" in m for m in masalah):
        umum.catat_status("harga", "basi" if lama else "gagal", "validasi: " + "; ".join(masalah))
        print("GAGAL validasi:", "; ".join(masalah))
        return 1

    if lama and lama.get("data", {}).get("tanggal_data", "") > data["tanggal_data"]:
        umum.catat_status("harga", "basi", "tanggal sumber lebih lama dari data tersimpan")
        print("Dilewati: tanggal sumber lebih lama dari data tersimpan")
        return 0

    riwayat = (umum.baca_json(PATH_RIWAYAT, None) or {}).get("data") or {}
    riwayat = perbarui_riwayat(riwayat, data)
    data = hitung_7h(data, riwayat)

    status = "ok" if not masalah else "sebagian"
    catatan = "; ".join(masalah)
    umum.tulis_json(PATH_HARGA, umum.amplop("harga", data, SUMBER, status, catatan))
    umum.tulis_json(PATH_RIWAYAT, umum.amplop("harga_riwayat", riwayat, SUMBER, status, catatan))
    umum.catat_status("harga", status, catatan)
    titik = max(len(v) for v in riwayat["seri"].values())
    print("OK status=%s tanggal=%s komoditas=%d titik_riwayat_maks=%d"
          % (status, data["tanggal_data"], len(data["komoditas"]), titik))
    return 0


if __name__ == "__main__":
    sys.exit(jalankan("--berkas" in sys.argv))
