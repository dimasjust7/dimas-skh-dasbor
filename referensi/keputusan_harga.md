# Keputusan jalur harga pangan (Tahap 1)

## Keputusan
**Jalur A (A1) dengan syarat, ditambah C untuk komoditas yang tidak tercakup.**
Panel Harga Bapanas menyediakan data tingkat Kab. Sukoharjo tanpa login. Namun level yang ditangkap
pemilik adalah **Produsen** (`level_harga_id=1`), bukan harga eceran pasar. Label UI wajib menyebut
"harga tingkat produsen".

## Bukti
- Tangkapan pemilik: `referensi/harga/panelharga_sukoharjo.txt` (Authorization: tidak, Cookie: tidak) dan `panelharga_cities.txt`.
- Daftar kota (`api/cities?province_id=13`): Kab. Sukoharjo ada, `id=196`, `national_id=33.11`.
- Uji `skrip/uji_harga.py` ke
  `GET /api/front/harga-pangan-informasi?province_id=13&city_id=196&level_harga_id=1`:
  HTTP 200 pada percobaan 1, 4346 byte, `status=success`, tanggal data 2026-11-15.
- 14 komoditas dikembalikan, 8 di antaranya bernilai > 0. `_tmp/contoh_harga.json` lolos (≥ 8 komoditas, harga > 0).

## Matriks kandidat
| Kandidat | Cakupan | Komoditas (harga > 0) | Riwayat | Autentikasi | ToS | Dari Actions |
|---|---|---|---|---|---|---|
| A1 Panel Harga Bapanas, kab/kota, level Produsen | Kab. Sukoharjo | 8 dari 14 | Tidak ada, hanya hari ini dan kemarin | Tidak perlu (terbukti) | Tidak ada berkas ToS dari pemilik; belum diperiksa | Belum terverifikasi (lihat catatan) |
| A1 level lain (konsumen/eceran) | Tidak diketahui | Tidak diketahui | Tidak diketahui | Tidak diketahui | - | Tidak diuji. Nilai `level_harga_id` selain 1 tidak ada di tangkapan, tidak ditebak |
| B2 Panel Harga provinsi (`harga-peta-provinsi`) | Jawa Tengah | - | - | - | - | Tidak diuji. Tidak ada tangkapan |
| A2 SP2KP, A3 SISKAPERBAPO, B1 PIHPS | - | - | - | - | - | Tidak diuji. Tidak ada tangkapan pemilik |

## Komoditas inti (5.3) terhadap data A1
| Komoditas inti | Ada di A1 | Catatan |
|---|---|---|
| Beras medium | ya | 13.350 Rp/kg |
| Bawang merah | ya | 24.000 Rp/kg |
| Telur ayam ras | ya | 22.033 Rp/kg |
| Cabai rawit merah | tidak (0) | perlu jalur C |
| Cabai merah keriting | tidak (0) | perlu jalur C |
| Bawang putih | tidak ada di respons | perlu jalur C |
| Minyak goreng | tidak ada di respons | perlu jalur C |
| Gula pasir | tidak (hanya gula petani/pabrik, 0) | perlu jalur C |

Hanya 3 dari 8 komoditas inti Beranda yang punya angka. Komoditas 8 itu sebagian besar adalah
gabah, jagung, dan ternak hidup, yang kurang berguna bagi warga.

## Catatan teknis
- Respons tidak berisi riwayat. Grafik tren hanya bisa dibangun dengan menyimpan snapshot harian di
  `harga_riwayat.json` lewat Actions (maks. 400 hari). `rata_7h` dan `ubah_7h_persen` bernilai `null` sampai ada 7 hari data.
- Satuan di sumber beragam (`Rp/kg`, `Rp./Kg`); dinormalisasi ke `kg`.
- Komoditas bernilai 0 dianggap "tidak ada data" dan tidak ditulis.
- Pemetaan `id_sumber` ke id internal ada di `data/peta_komoditas.csv`.

## Belum selesai dan perlu keputusan pemilik
1. **Level harga eceran.** Ulangi tangkapan DevTools (5.4) dengan mengganti pilihan tingkat harga di UI
   (produsen, grosir, eceran/konsumen jika ada), lalu simpan cURL tiap level. Dengan itu cabai, bawang putih,
   minyak, dan gula mungkin terisi. Tanpa tangkapan itu, `level_harga_id` lain tidak boleh ditebak.
2. **ToS.** Tidak ada berkas ketentuan penggunaan di `referensi/harga/`. Pemilik perlu menyimpannya (5.4 butir 7).
3. **Uji dari Actions.** Langkah sementara "SEMENTARA uji harga T1" sudah ditambahkan di
   `.github/workflows/uji_jaringan.yml` dan di-commit (8c8ec99). Hasil run belum bisa saya baca karena
   terminal tidak mengembalikan keluaran. Lihat tab Actions, lalu hapus langkah itu.
4. Jalur C (`data/harga_manual.csv`) tetap perlu disiapkan untuk komoditas yang tidak tercakup.
