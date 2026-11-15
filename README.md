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

## Catatan teknis
- `alat\proyek_baru.ps1` gagal bila dijalankan tanpa `-Root` (`$PSScriptRoot` kosong); pakai `-Root (Get-Location).Path`.
- Set `$ProgressPreference='SilentlyContinue'` pada skrip uji agar keluaran terminal tidak berantakan.
