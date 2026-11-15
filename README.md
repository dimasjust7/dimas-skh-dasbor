# Dasbor Kabupaten Sukoharjo

- **Status:** berjalan (mulai 2026-11-15)
- **Tenggat:** -

## Tujuan
-

## Aturan penting
<!-- ringkas dari referensi/: format, batas ukuran/durasi, cara pengumpulan -->
-

## Sumber data
<!-- untuk tiap berkas di data/mentah/: asal (URL), tanggal unduh, cara unduh ulang -->
-

## Cara menjalankan
```
python <skrip>.py
```

## Cara cek
```
python cek_<x>.py
```

## Hasil
<!-- daftar berkas final di hasil/ dan ke mana diserahkan -->
-

## Tujuan
Dasbor warga Kabupaten Sukoharjo (mandiri, tanpa pemerintah): cuaca, harga pangan, profil 12 kecamatan, peta fasilitas.
Rencana arsitektur: situs statis (GitHub Pages) + GitHub Actions terjadwal yang menulis `data/*.json`.

## Sumber data (hasil cek tahap 1)
- Cuaca: `https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=<kode>` berfungsi tanpa kunci. Kode adm3 Weru = 33.11.01. Perlu daftar kode adm4 tiap kecamatan.
- Harga pangan: `siskaperbapo.jatengprov.go.id` tidak bisa di-resolve (domain salah/mati). Panel Harga Badan Pangan (`panelharga.badanpangan.go.id`) memakai API `https://api-panelhargav2.badanpangan.go.id/api`; endpoint `front/harga-peta-provinsi` merespons tetapi butuh `komoditas_id`; `front/komoditas` butuh autentikasi (401). Daftar endpoint kabupaten belum ditemukan. Alternatif: PIHPS BI (`bi.go.id/hargapangan`, perlu cek cakupan Sukoharjo).
- Situs resmi: `sukoharjokab.go.id` dapat diakses.

## Status sumber
Hasil Tahap 0, diuji 2026-11-15 (satu percobaan per URL, tanpa coba ulang). Rincian: `referensi/uji_jaringan_lokal.txt` dan `referensi/uji_jaringan_actions.txt`.

| Sumber | Lokal (PC) | GitHub Actions | Catatan |
|---|---|---|---|
| BMKG prakiraan (`adm4=33.11.01.2001`) | 200, 842 ms, 7550 B | 200, 482 ms, 7566 B | Dapat dipakai dari Actions. |
| BMKG autogempa | 200, 141 ms | 200, 445 ms | Dapat dipakai dari Actions. |
| Open-Meteo forecast | 200, 983 ms | 200, 135 ms | Dapat dipakai. |
| Open-Meteo air-quality | 200, 781 ms | 200, 480 ms | Dapat dipakai. |
| Overpass (POST) | 502, server penuh | ERR, timeout 25 s | Gagal di kedua sisi. Perlu uji ulang di T-fasilitas, dengan coba ulang dan mungkin server cadangan. |
| Panel Harga (`harga-peta-provinsi`) | 200, isi galat 400 "period date tidak boleh kosong" | ERR, timeout 25 s | Berfungsi dari PC, timeout dari Actions. Kemungkinan IP runner luar negeri tidak dijangkau. Penentu keputusan jalur harga di T1. |
| PIHPS (`bi.go.id/hargapangan`) | 200, 3141 ms, 313 KB HTML | 200, 4655 ms, 313 KB HTML | Mengembalikan halaman HTML, belum terbukti ada API data. |
| Wikipedia (REST summary) | 200, 108 ms | 200, 107 ms | Dapat dipakai. |

Kesimpulan: BMKG tidak diblokir dari Actions, jadi Rencana Jaringan B tidak diperlukan untuk cuaca dan gempa. Harga otomatis dari Panel Harga belum bisa dipastikan di Actions dan harus diputuskan di T1.

## Catatan teknis
- `alat\proyek_baru.ps1` gagal bila dijalankan tanpa `-Root` (`$PSScriptRoot` kosong); pakai `-Root (Get-Location).Path`.
- Set `$ProgressPreference='SilentlyContinue'` pada skrip uji agar keluaran terminal tidak berantakan.
