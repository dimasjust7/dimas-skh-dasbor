# Keputusan jalur harga pangan (Tahap 1, revisi 2)

## Keputusan
**Jalur A1: Panel Harga Bapanas, tingkat Kab. Sukoharjo, level Konsumen (`level_harga_id=3`).**
Jalur C (`data/harga_manual.csv`) menjadi cadangan dan cek lokal, bukan pengisi komoditas inti.
Revisi ini menggantikan keputusan sebelumnya (level Produsen, `level_harga_id=1`).

## Bukti
- Tangkapan pemilik: `referensi/harga/panelharga_konsumen.txt` (Authorization: tidak, Cookie: tidak) dan `panelharga_konsumen_respons.json`.
- Endpoint: `GET https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-informasi?province_id=13&city_id=196&level_harga_id=3`.
- `request_data.level_harga_desc` = "Konsumen", wilayah "Kab. Sukoharjo", tanggal data 2026-11-15.
- Respons: 27 komoditas, 24 bernilai > 0. `skrip/uji_harga.py --berkas` menghasilkan `_tmp/contoh_harga.json` dan mencetak LOLOS
  (≥ 8 komoditas, semua harga > 0, 8 komoditas inti lengkap).
- Pengujian dari komputer lokal (level 1) sebelumnya: HTTP 200 tanpa autentikasi. Level 3 divalidasi dari berkas tangkapan, belum dipanggil langsung.

## Matriks kandidat
| Kandidat | Cakupan | Komoditas (> 0) | Riwayat | Autentikasi | ToS | Dari Actions |
|---|---|---|---|---|---|---|
| A1 Panel Harga, level Konsumen | Kab. Sukoharjo | 24 dari 27 (8/8 inti) | Tidak ada, hanya hari ini dan kemarin | Tidak perlu | Belum ada berkas ToS dari pemilik | **Gagal: timeout** |
| A1 level Produsen (level 1) | Kab. Sukoharjo | 8 dari 14 (3/8 inti) | Tidak ada | Tidak perlu | sama | Gagal: timeout (host sama) |
| B1/B2, A2, A3 | - | - | - | - | - | Tidak diuji, tidak ada tangkapan |

## Komoditas inti Beranda (5.3) terhadap data level 3
| Inti | id internal | id_sumber | Harga (Rp) |
|---|---|---|---|
| Beras medium | beras_medium | 28 | 12.683 /kg |
| Cabai rawit merah | cabai_rawit_merah | 33 | 61.667 /kg |
| Cabai merah keriting | cabai_merah_keriting | 32 | 53.333 /kg |
| Bawang merah | bawang_merah | 30 | 28.000 /kg |
| Bawang putih | bawang_putih | 31 | 36.667 /kg |
| Telur ayam ras | telur_ayam_ras | 36 | 22.833 /kg |
| Minyak goreng | minyak_goreng_kemasan | 38 | 23.000 /liter |
| Gula pasir | gula_pasir | 37 | 18.000 /kg |

Pemetaan lengkap 24 komoditas ada di `data/peta_komoditas.csv`. Tiga komoditas bernilai 0 (Beras Khusus Lokal,
Daging Kerbau Beku dan Segar) tidak dipetakan. Beras medium memakai id 28 ("Beras Medium"); id 109 (SPHP) dan 165 (non-SPHP)
dipetakan terpisah. Minyak goreng inti memakai varian kemasan; curah dan Minyakita ada sebagai komoditas tambahan.

## Masalah pipeline: Actions tidak bisa menjangkau API
Uji dari Actions timeout. Penyebabnya diduga pemblokiran IP luar negeri, tetapi **belum terbukti** (timeout juga bisa
berasal dari pembatasan lain). Akibatnya jalur "otomatis di GitHub Actions" untuk harga tidak bisa dipakai apa adanya.
Pilihan, berurutan menurut rekomendasi:
1. **Pengambilan lokal terjadwal.** Task Scheduler di PC pemilik menjalankan `skrip/ambil_harga.py` tiap hari, lalu `git push`
   `data/harga.json` dan `data/harga_riwayat.json`. Actions hanya mendeploy. Kelemahan: PC harus menyala.
2. **Runner self-hosted** di perangkat berIP Indonesia (mis. VPS Indonesia). Lebih andal, tetapi ada biaya dan perawatan.
3. **Cadangan di UI:** tampilkan "Terakhir diperbarui <tanggal>" dan label usang bila data > 3 hari. Wajib apa pun opsi di atas.
Jangan memakai proxy publik atau layanan pihak ketiga tanpa kajian ToS dan keamanan.

## Catatan teknis
- Tanpa riwayat dari sumber. Grafik tren dibangun dari snapshot harian (maks. 400 hari). `rata_7h` dan `ubah_7h_persen` `null` sampai ada 7 hari data.
- Satuan dinormalisasi ke `kg` atau `liter`. Tingkat data `kabupaten`, jadi `label_peringatan` kosong.
- Harga di panel berupa rata-rata pantauan, bukan harga di satu pasar tertentu. Beri atribusi "Sumber: Panel Harga Badan Pangan Nasional".

## Belum selesai dan perlu keputusan pemilik
1. Pilih opsi pipeline (1, 2, atau cadangan saja). Tahap berikutnya perlu `skrip/ambil_harga.py` sesuai pilihan.
2. Simpan halaman ketentuan penggunaan Panel Harga ke `referensi/harga/`.
3. Uji panggilan langsung level 3 dari PC lokal (satu kali `python skrip/uji_harga.py`) untuk memastikan responsnya sama dengan tangkapan.
