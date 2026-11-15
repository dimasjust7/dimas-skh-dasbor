"""Uji unit kecil untuk fungsi murni di umum.py. Jalankan: python skrip/uji_umum.py"""
import json
import os
import tempfile
import unittest

import umum


class UjiUmum(unittest.TestCase):
    def test_amplop(self):
        a = umum.amplop("cuaca", {"x": 1}, [{"nama": "BMKG"}], "ok", "12/12")
        self.assertEqual(a["versi_skema"], 1)
        self.assertEqual(a["modul"], "cuaca")
        self.assertEqual(a["status"], "ok")
        self.assertEqual(a["catatan"], "12/12")
        self.assertFalse(a["contoh"])
        self.assertEqual(a["data"], {"x": 1})
        self.assertTrue(a["diperbarui"].endswith("+07:00"))

    def test_tulis_json_atomik_ringkas(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "t.json")
            umum.tulis_json(p, {"a": "é", "b": [1, 2]})
            with open(p, "rb") as f:
                mentah = f.read()
            self.assertFalse(mentah.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(mentah.decode("utf-8"), '{"a":"é","b":[1,2]}')
            self.assertFalse(os.path.exists(p + ".tmp"))
            self.assertEqual(json.loads(mentah), {"a": "é", "b": [1, 2]})

    def test_baca_json_bawaan(self):
        self.assertEqual(umum.baca_json("tidak_ada.json", {"k": 0}), {"k": 0})

    def test_sekarang_wib(self):
        t = umum.sekarang_wib()
        self.assertEqual(t.utcoffset().total_seconds(), 7 * 3600)

    def test_catat_status(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "status.json")
            umum.catat_status("cuaca", "ok", "12/12", (9, 24), path=p)
            umum.catat_status("cuaca", "gagal", "timeout", path=p)
            m = umum.baca_json(p)["modul"]["cuaca"]
            self.assertEqual(m["status"], "gagal")
            self.assertIsNotNone(m["terakhir_sukses"])
            self.assertEqual(m["ambang_jam"], [9, 24])


if __name__ == "__main__":
    unittest.main()
