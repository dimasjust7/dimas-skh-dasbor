# Rencana Dashboard Warga Kabupaten Sukoharjo

**Status dokumen:** rencana; T0 dan T1 sudah dieksekusi (lihat "Catatan revisi" di bawah dan status tahap di 8.0). Simpan sebagai `dasbor_sukoharjo/referensi/rencana_dasbor.md` sebelum Tahap 0. Prompt Sonnet di bagian 8 membaca bagian tertentu dari berkas ini, jadi judul bagian jangan diubah.

**Label kepastian yang dipakai di seluruh dokumen:**

- **[T] Terverifikasi:** sudah dicek oleh pemilik (lihat "Status riset sumber data").
- **[D] Dugaan:** kemungkinan ada atau benar, tetapi perlu dicek. URL atau perilaku bertanda [D] wajib diuji sebelum dipakai.
- **[?] Tidak diketahui:** belum ada dasar yang cukup.
- **[U] Usulan:** keputusan desain dari perencana. Boleh diubah pemilik.

## Catatan revisi (diperbarui 2026-11-16)
Keputusan yang berubah setelah T0 dan T1. Bila bertentangan dengan bagian lain, catatan ini yang berlaku.
1. **Harga [T]:** jalur A1 = Panel Harga Bapanas level **Konsumen** (`level_harga_id=3`, `province_id=13`, `city_id=196`). 24 komoditas bernilai > 0, 8 dari 8 komoditas inti tercakup. Level Produsen (`level_harga_id=1`) hanya mengisi 3 dari 8 komoditas inti dan tidak dipakai. Jalur C menjadi cadangan opsional.
2. **Harga diambil dari PC pemilik, bukan Actions [T]:** API Bapanas timeout dari Actions. Rencana Jaringan B (10.1) dijalankan untuk harga: `skrip/ambil_harga.py` dan `skrip/jadwal_harga.ps1`, tugas Task Scheduler `DasborHarga` (tiap 3 jam, saat PC menyala), push ke `main`. Cabang `data` seperti di 10.1 belum dibuat; putuskan di T4 (deploy).
3. **Penyebab timeout belum terbukti [?]:** panggilan dari PC lokal juga timeout pada 2026-11-16 00:03-00:05 (setelah sukses 23:57). Dugaan "IP luar negeri diblokir" melemah; API mungkin lambat atau berkala. Uji banding Actions dan PC pada jam yang sama masih terbuka.
4. **Overpass [?]:** menurut laporan pemilik, Overpass timeout dari Actions. T3 dan T7 sebaiknya mengambil data Overpass dari PC lalu meng-commit hasilnya. Isi T3 dan T7 belum disesuaikan; lakukan saat tahap itu disiapkan.
5. **Sumber harga tanpa riwayat [T]:** hanya hari ini dan kemarin. Riwayat dibangun dari snapshot harian (`harga_riwayat.json`, maks. 400 hari). `rata_7h` dan `ubah_7h_persen` bernilai `null` sampai ada 3 titik.
6. **Skema 6.4.7:** `satuan` boleh `kg` atau `liter`. Pemetaan kategori: garam = `bumbu`; ikan, daging, telur = `protein`; beras, jagung, kedelai, tepung = `pokok`; gula dan minyak goreng = `minyak_gula`; bawang dan cabai = `bumbu`. Pemetaan lengkap ada di `data/peta_komoditas.csv`.
7. **T2 dipecah** menjadi T2A (fondasi) dan T2B (tampilan dan alat cek visual). Total BATAS 60 alat, bukan 45.
8. **BLOK UMUM (8.0.1)** diperbarui: kalimat pembuka, aturan 1, 3, 4, 6, 9, 12, dan aturan 14 baru berisi fakta T0-T1.
9. **Masih terbuka:** ToS Panel Harga belum disimpan di `referensi/harga/`; keputusan cabang `data`; uji banding Actions dan PC; bukti push otomatis dari tugas `DasborHarga`.

---

## 1. Visi dan pengguna

### 1.1 Visi [U]
Warga cukup membuka satu halaman yang ringan di HP untuk tahu cuaca di kecamatannya, harga kebutuhan pokok, jadwal ibadah dan hari pasaran, nomor darurat, letak layanan terdekat, dan kondisi wilayahnya. Setiap angka mencantumkan sumber dan waktu pembaruannya. Nama kerja: **"Sukoharjo Hari Ini"**. Nama final diputuskan pemilik (K2).

### 1.2 Pengguna dan masalahnya

| Pengguna | Masalah nyata | Yang paling dibutuhkan |
|---|---|---|
| Ibu rumah tangga | Harga cabai dan bawang naik turun. Tidak tahu harga wajar sebelum ke pasar. | Harga hari ini dan tren, hari pasaran, cuaca untuk menjemur |
| Pedagang pasar dan UMKM kuliner | Perlu memperkirakan harga beli dan stok | Tren harga 30–90 hari, perbandingan dengan pekan lalu |
| Petani (padi, palawija) | Butuh perkiraan hujan untuk tanam, semprot, panen, dan menjemur gabah | Hujan 3–7 hari per kecamatan, kelembapan, angin |
| Pekerja komuter (ke Solo, Solo Baru, Kartasura) | Hujan di jalan, info transportasi | Cuaca per jam, KRL, BST, bandara |
| Pelajar dan orang tua | Info sekolah, libur, cuaca berangkat | Kalender libur, lokasi sekolah, cuaca pagi |
| Warga lansia dan keluarganya | Fasilitas kesehatan dan nomor darurat | Puskesmas atau RS terdekat, tombol telepon, kualitas udara |
| Pendatang dan mahasiswa | Belum kenal wilayah | Profil kecamatan, peta layanan publik |
| Warga umum | Gempa terasa, ingin kepastian | Gempa terkini dan jaraknya dari Sukoharjo |

### 1.3 Prinsip desain [U]
1. **Jawab dalam 5 detik.** Beranda menampilkan informasi yang paling sering dicari untuk kecamatan pilihan pengguna, tanpa perlu mengetuk apa pun.
2. **Jujur soal data.** Setiap kartu menampilkan sumber, waktu pembaruan, dan cakupan (misalnya "harga tingkat provinsi, bukan Sukoharjo"). Data yang basi diberi tanda, bukan disembunyikan.
3. **Ringan.** Tanpa web font, tanpa framework, dan pustaka berat hanya dimuat saat dibutuhkan. Muatan awal di bawah 100 KB (terkompresi).
4. **Lokal.** Pemilih kecamatan, hari pasaran Jawa, dan istilah setempat.
5. **Bisa dirawat satu orang.** Data otomatis bila sumbernya stabil. Data manual memakai CSV kecil yang mudah diisi dan diberi tanggal verifikasi.
6. **Bukan situs resmi.** Pernyataan ini tampil jelas di footer dan halaman Tentang. Situs tidak memakai lambang daerah.

---

## 2. Katalog modul

**Skala:** Nilai 1–5 (manfaat bagi warga), Biaya 1–5 (biaya eksekusi dan perawatan). **Skor prioritas = Nilai × (6 − Biaya)**, rentang 1–25. P1 ≥ 16, P2 10–15, P3 < 10.

### 2.1 Ekonomi dan harga

| ID | Modul | Tujuan dan pengguna | Data dan sumber kandidat (status) | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M01 | Harga kebutuhan pokok | Harga harian dan tren cabai, bawang, beras, telur, minyak, gula, daging. Untuk ibu rumah tangga, pedagang, UMKM. | Panel Harga Bapanas: API `front/harga-peta-provinsi` [T merespons, butuh `komoditas_id`]. Tingkat kabupaten [?]. SP2KP Kemendag [D]. PIHPS BI [T bisa diakses, cakupan Sukoharjo ?]. SISKAPERBAPO Jateng [T tidak bisa diakses dari lingkungan uji]. Input manual [U]. | Harian (otomatis) atau mingguan (manual) | 4 (sumber belum pasti) / 2 bila jalur C | Sumber tidak ada, berubah, atau ToS melarang | 5 | 10 → **inti**, lihat bagian 5 |
| M16 | BBM dan LPG | Harga BBM Pertamina dan HET LPG 3 kg | Situs Pertamina, SK HET LPG [D], input manual | Bulanan | 1 | Perubahan tidak tercatat | 3 | 15 |
| M18 | Kerja: UMK, lowongan resmi | UMK Sukoharjo tahun berjalan, tautan Karirhub Kemnaker [D], BLK | SK Gubernur Jateng soal UMK [D], input manual | Tahunan | 1 | Angka usang | 3 | 15 |
| M19 | Direktori UMKM dan produk unggulan | Promosi usaha lokal | Kurasi manual dan formulir warga [U] | Bulanan | 4 | Kurasi berat, data pribadi | 3 | 6 |

### 2.2 Cuaca dan kebencanaan

| ID | Modul | Tujuan dan pengguna | Data dan sumber kandidat (status) | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M02 | Prakiraan cuaca per kecamatan | Cuaca per 3 jam selama 3 hari untuk semua orang | BMKG `https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=<kode>` [T]. Nama bidang [D], lihat 6.4.3. Batas laju [D]. | 3 jam | 2 | Diblokir dari IP luar negeri [?], skema berubah | 5 | **20** |
| M06 | Hujan 7 hari (agro-cuaca) | Jendela tanam, semprot, dan jemur untuk petani | Open-Meteo forecast `https://api.open-meteo.com/v1/forecast` [D], harian `precipitation_sum`, `precipitation_probability_max` [D] | 3 jam | 2 | Data model, bukan BMKG (perlu label) | 4 | **16** |
| M04 | Gempa terkini dan dirasakan | Kepastian saat terasa getaran | BMKG `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json` dan `gempadirasakan.json` [D] | 3 jam (tertunda) | 1 | Tertunda hingga 3 jam (perlu label) | 3 | 15 |
| M05 | Kualitas udara dan UV | Kelompok sensitif, aktivitas luar ruang | Open-Meteo Air Quality `https://air-quality-api.open-meteo.com/v1/air-quality` [D]: `pm2_5`, `pm10`, `us_aqi`, `uv_index` [D]. ISPU KLHK stasiun Sukoharjo [?]. | 3 jam | 2 | Model global beresolusi kasar | 3 | 12 |
| M03 | Peringatan dini cuaca BMKG | Hujan lebat dan angin kencang | Feed peringatan dini atau CAP BMKG [?] | Jam-an | 3 | Format tidak diketahui | 4 | 12, spike ≤ 4 alat |
| M23 | Banjir Bengawan Solo dan risiko bencana | Warga bantaran (perlu dicek kecamatan mana) | Tinggi muka air BBWS Bengawan Solo [?], InaRISK BNPB [D] | — | 4 | Tidak ada API publik | 4 | 8, ditunda |

### 2.3 Ibadah, waktu, dan kalender

| ID | Modul | Tujuan | Data dan sumber | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M07 | Jadwal sholat, imsak, terbit, terbenam | Ibadah harian | **Dihitung sendiri** dengan parameter Kemenag (Subuh 20°, Isya 18°, Asar bayangan 1×, ihtiyat ±2 menit [D]), divalidasi terhadap jadwal Bimas Islam Kemenag [D] | Dibangun setahun sekali | 1 | Selisih menit (diuji) | 4 | **20** |
| M08 | Kalender: pasaran Jawa, Hijriah, libur | Hari pasaran untuk pasar tradisional, libur sekolah dan kerja | Pasaran dihitung dari tanggal jangkar (diverifikasi 2 referensi). Hijriah dari `Intl` peramban kalender `islamic-umalqura` (label "perkiraan"). Libur dari SKB 3 Menteri (manual). | Tahunan | 1 | Hijriah bisa beda dengan isbat (perlu label) | 4 | **20** |

### 2.4 Kesehatan, layanan publik, dan darurat

| ID | Modul | Tujuan | Data dan sumber | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M12 | Nomor darurat | Telepon dengan satu ketukan | Nomor nasional (112, 110, 113, 119, 115) [D, verifikasi dari situs resmi]. Nomor lokal Sukoharjo (PSC, BPBD, Damkar) [?], dicek pemilik. | Tahunan | 1 | Nomor salah = berbahaya, jadi hanya tampilkan yang terverifikasi | 5 | **25** |
| M11 | Fasilitas kesehatan | RS, puskesmas, klinik, apotek terdekat | OSM via Overpass `https://overpass-api.de/api/interpreter` [D] (lisensi ODbL). Daftar puskesmas dari situs Dinkes [?]. | Bulanan | 3 | OSM belum lengkap (perlu label) | 5 | 15 |
| M13 | Layanan publik | Disdukcapil, Samsat, MPP, kantor kecamatan, kantor pos: alamat, jam, tautan resmi | Kurasi manual dari situs resmi Pemkab [D] dan OSM | 6 bulanan | 2 | Jam berubah, perlu tanggal verifikasi | 4 | **16** |

### 2.5 Pendidikan, transportasi, dan pasar

| ID | Modul | Tujuan | Data dan sumber | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M17 | Pasar tradisional dan hari pasaran | Pasar mana yang ramai hari ini | Lokasi dari OSM `amenity=marketplace` [D]. Hari pasaran tiap pasar dikurasi manual [?] | Tahunan | 2 | Data pasaran per pasar sulit didapat | 4 | **16** |
| M15 | Transportasi | KRL Jogja–Solo (stasiun di Sukoharjo [D, dugaan Gawok di Gatak]), BST koridor [D], terminal, Bandara Adi Soemarmo (Boyolali) | Kurasi manual, OSM `railway=station` | 6 bulanan | 2 | Jadwal berubah, jadi tautkan sumber resmi dan jangan salin jadwal | 3 | 12 |
| M14 | Pendidikan | Peta sekolah, tautan SPMB/PPDB | OSM `amenity=school`. Data Referensi Kemdikbud [D, ToS ?] | Tahunan | 3 | Kelengkapan dan ToS | 3 | 9 |

### 2.6 Wilayah, kependudukan, dan lingkungan

| ID | Modul | Tujuan | Data dan sumber | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M09 | Profil 12 kecamatan | Kenal wilayah sendiri, bahan pelajar | BPS Kab. Sukoharjo ("Dalam Angka") [D], kode wilayah Kemendagri [D], Wikipedia ID (ringkasan) [D], OSM | Tahunan | 3 | Akurasi isi deskripsi, perlu ditinjau pemilik | 4 | 12 → **inti (permintaan pemilik)** |
| M10 | Peta kecamatan dan "saya di kecamatan mana" | Memilih kecamatan otomatis dari GPS (dihitung di perangkat) | Batas OSM `admin_level` kecamatan [D: di Indonesia diduga 6] | Tahunan | 2 | Poligon tidak lengkap, cadangan: peta skematik | 3 | 12 |
| M21 | Statistik kependudukan | Penduduk, luas, kepadatan per kecamatan | BPS, disalin manual oleh pemilik ke CSV | Tahunan | 2 | Tahun data harus tertulis | 3 | 12 (bagian M09) |
| M22 | Lingkungan: bank sampah, TPS | Pengelolaan sampah | [?] | — | 4 | Tidak ada data | 2 | 4, ditunda |

### 2.7 Wisata, budaya, pertanian, dan lainnya

| ID | Modul | Tujuan | Data dan sumber | Frek. | Biaya | Risiko | Nilai | Skor |
|---|---|---|---|---|---|---|---|---|
| M20 | Wisata, budaya, agenda | Kegiatan akhir pekan, agenda lokal | OSM `tourism=*` [D], Wikipedia, agenda dikurasi manual | Bulanan | 3 | Agenda cepat usang | 3 | 9, ditunda |
| M24 | Pertanian lanjutan: kalender tanam, harga gabah | Petani | Si Katam Kementan [D], harga gabah BPS (provinsi, bulanan) [D] | Bulanan | 3 | Cakupan dan format | 3 | 9, ditunda |
| M29 | Perikanan | Pembudidaya ikan | Relevansi untuk Sukoharjo [?] | — | 4 | — | 2 | 4, ditunda |
| M25 | Pengumuman resmi | Tautan ke kanal resmi Pemkab | Tautan saja, tanpa menyalin isi [U] | Tahunan | 1 | — | 2 | 10 |
| M26 | Status data (transparansi) | Membangun kepercayaan, alat perawatan | `status.json` buatan sendiri | Tiap pembaruan | 1 | — | 4 | **20** |
| M27 | Pencarian global | Cari desa, komoditas, fasilitas, layanan | Indeks `cari.json` buatan skrip | Tiap build | 2 | — | 3 | 12 |
| M30 | Kurs dan harga emas | — | ToS sumber [?] | — | 3 | ToS | 2 | 6, tidak dibuat |

---

## 3. Cakupan

### 3.1 Versi lengkap (1.0) [U]
Lima tab: **Beranda**, **Harga**, **Cuaca**, **Wilayah**, **Layanan**. Ada juga halaman Tentang, Status data, dan pencarian. Modul yang masuk 1.0: M01, M02, M04–M08, M09–M13, M15–M18, M21, M25–M27. PWA bisa dibuka luring. Tiap kecamatan punya halaman statis yang bisa diindeks mesin pencari.

### 3.2 Urutan rilis

| Rilis | Isi | Mengapa urutan ini |
|---|---|---|
| 0.1 (T4) | Kerangka, sistem desain, cuaca BMKG 12 kecamatan, pemilih kecamatan, nomor darurat nasional terverifikasi, status data, deploy otomatis | Nilai tertinggi dengan sumber yang sudah [T]. Menguji seluruh pipeline lebih awal. |
| 0.2 (T5) | Harga pangan (jalur A, B, atau C sesuai hasil spike T1) | Permintaan utama pemilik. Risikonya sudah diuji di T1. |
| 0.3 (T6) | Jadwal sholat, kalender (pasaran, Hijriah, libur), gempa, udara dan UV, hujan 7 hari | Murah, banyak dihitung sendiri, nilai harian tinggi |
| 0.4 (T7) | Fasilitas kesehatan, pendidikan, pasar, layanan publik, transportasi, BBM/LPG/UMK, peta Leaflet | Butuh poligon dari T3 dan kurasi manual |
| 0.5 (T8) | Profil 12 kecamatan dan perbandingan antarkecamatan | Butuh data fasilitas (jumlah per kecamatan) dan isian BPS dari pemilik |
| 1.0 (T9–T10) | Pencarian, PWA, halaman statis SEO, audit aksesibilitas dan kinerja, umpan balik, runbook | Penyempurnaan |

**Bisa ditunda tanpa merusak keseluruhan:** M03, M14 (bagian Kemdikbud), M19, M20, M22, M23, M24, M29.

**Berisiko tinggi, punya titik berhenti:**
- M01: spike T1 maksimal 30 alat.
- M03: maksimal 4 alat di T6.
- Poligon M10: 1 percobaan + 1 perbaikan di T3.
- Akses dari GitHub Actions: diuji di T0.

---

## 4. Profil 12 kecamatan

### 4.1 Daftar dasar

Slug dan urutan tampilan mengikuti daftar pemilik. Kode Kemendagri [D]: diduga 33.11.01–33.11.12 sesuai urutan di bawah. Weru = 33.11.01 konsisten dengan kode desa 33.11.01.2001 yang sudah [T].

| Slug | Nama tampilan | Kode kec. [D] |
|---|---|---|
| weru | Weru | 33.11.01 |
| bulu | Bulu | 33.11.02 |
| tawangsari | Tawangsari | 33.11.03 |
| sukoharjo | Sukoharjo (tulis "Kec. Sukoharjo" agar tidak tertukar dengan kabupaten) | 33.11.04 |
| nguter | Nguter | 33.11.05 |
| bendosari | Bendosari | 33.11.06 |
| polokarto | Polokarto | 33.11.07 |
| mojolaban | Mojolaban | 33.11.08 |
| grogol | Grogol | 33.11.09 |
| baki | Baki | 33.11.10 |
| gatak | Gatak | 33.11.11 |
| kartasura | Kartasura | 33.11.12 |

### 4.2 Struktur isi profil (urutan di halaman `#/wilayah/<slug>`)

| Bagian | Isi | Sumber | Cara tampil |
|---|---|---|---|
| Kepala | Nama, kode, cuaca saat ini (dari cuaca.json), tombol "Jadikan kecamatan saya" | Kemendagri [D], BMKG | Judul 22 px, lencana cuaca |
| Angka kunci | Luas (km²), penduduk, kepadatan (dihitung), jumlah desa/kelurahan, tahun data | BPS (diisi pemilik), kode wilayah | 4 kartu angka dalam grid 2×2 |
| Ringkasan | Deskripsi 40–70 kata, ditulis sendiri (bukan salinan), status `draf` atau `ditinjau` | Ringkasan Wikipedia ID [D] sebagai bahan, ditinjau pemilik | Paragraf, tautan "sumber" |
| Ciri khas | 2–5 butir. Setiap butir wajib punya URL sumber. | Wikipedia, situs Pemkab, berita | Daftar berikon. Butir tanpa sumber tidak ditampilkan. |
| Peta | Poligon kecamatan disorot dan kecamatan tetangga | OSM | SVG statis, ketuk untuk membuka Leaflet |
| Tetangga | Kecamatan tetangga di dalam kabupaten (dihitung dari poligon). Batas luar kabupaten diisi manual dari sumber. | Poligon OSM | Chip yang bisa diketuk |
| Desa/kelurahan | Daftar nama dengan jenis (desa/kelurahan) | Kode wilayah [D] | Daftar yang bisa dicari, terlipat |
| Fasilitas | Jumlah per jenis (RS, puskesmas/klinik, apotek, sekolah, pasar). Label "menurut OpenStreetMap, bisa belum lengkap". | fasilitas.json | Baris ikon dan angka, tautan ke peta tersaring |
| Layanan | Kantor kecamatan (alamat, telepon bila terverifikasi) | Situs Pemkab [D] | Kartu kontak |
| Sumber dan verifikasi | Daftar sumber dan `tanggal_verifikasi` | — | Teks kecil |

### 4.3 Pengumpulan murah dan validasi
1. **Pemilik (sekitar 20 menit):** isi `data/statistik_kecamatan.csv` (12 baris) dari publikasi BPS "Kabupaten Sukoharjo Dalam Angka" edisi terbaru [D]. Kolom: `slug,luas_km2,penduduk,tahun_data,url_sumber`. Ini lebih murah daripada mengurai PDF dengan pustaka tambahan.
2. **Skrip (otomatis):** jumlah desa dan kelurahan diambil dari berkas kode wilayah. Tetangga dihitung dari poligon. Jumlah fasilitas dihitung dari fasilitas.json.
3. **Sonnet:** mengambil ringkasan Wikipedia untuk 12 judul lewat REST `https://id.wikipedia.org/api/rest_v1/page/summary/<judul>` [D]. Format judul diduga `Weru,_Sukoharjo` [D]. Hasilnya disimpan ke `data/mentah/`. Sonnet lalu menulis draf deskripsi dan ciri khas dengan sumber, berstatus `draf`.
4. **Validasi otomatis** (`cek_profil.py`):
   - total penduduk 12 kecamatan dibandingkan angka kabupaten di CSV (pemilik mengisi baris `_kabupaten`), toleransi 1%;
   - kepadatan dalam rentang wajar (100–10.000 jiwa/km²; ambang ini usulan, bukan fakta);
   - setiap ciri khas punya URL;
   - panjang deskripsi 40–70 kata;
   - `tahun_data` sama untuk semua baris.
5. **Validasi manusia:** pemilik membaca 12 draf (sekitar 15 menit), lalu mengubah status menjadi `ditinjau`. UI menampilkan lencana "draf" bila belum ditinjau.

---

## 5. Strategi harga pangan

### 5.1 Fakta yang sudah ada
- Panel Harga Bapanas memakai API `https://api-panelhargav2.badanpangan.go.id/api`. `front/harga-peta-provinsi` merespons tetapi butuh `komoditas_id`. `front/komoditas` membalas 401 [T].
- SISKAPERBAPO Jateng tidak bisa diakses dari lingkungan uji [T]. Bisa jadi ini pemblokiran IP non-Indonesia atau situs memang mati [?].
- PIHPS BI bisa diakses [T]. Cakupan Sukoharjo [?]. Dugaan: PIHPS meliputi kota-kota survei di Jateng, termasuk Surakarta [D]. Sukoharjo berbatasan langsung dengan Kota Surakarta.
- Hasil T1 [T]: Panel Harga Bapanas menyediakan Kab. Sukoharjo (`city_id=196`) tanpa login. Level Konsumen (`level_harga_id=3`) mengisi 24 komoditas, termasuk 8 dari 8 komoditas inti. Tidak ada riwayat. Timeout dari Actions (lihat Catatan revisi).

### 5.2 Jalur bertingkat

| Jalur | Isi | Label di UI | Syarat dipakai |
|---|---|---|---|
| **A**: Sukoharjo, otomatis | A1: Panel Harga tingkat kab/kota (endpoint ditemukan lewat DevTools). A2: SP2KP Kemendag [D]. A3: SISKAPERBAPO bila terjangkau dari Actions. | "Harga rata-rata Kab. Sukoharjo · sumber X" | Tanpa login, ToS tidak melarang, terjangkau dari Actions, ≥ 8 komoditas |
| **B**: terdekat atau provinsi, otomatis | B1: PIHPS Kota Surakarta (bila Sukoharjo tidak ada). B2: Panel Harga provinsi Jawa Tengah via `harga-peta-provinsi` dengan `komoditas_id` dari tangkapan DevTools. | Spanduk kuning: "Harga Kota Surakarta/Jawa Tengah, bukan khusus Sukoharjo" | Sama seperti A, cakupan lebih luas |
| **C**: Sukoharjo, manual terstruktur | `data/harga_manual.csv` diisi pemilik tiap pekan dari publikasi resmi Pemkab/Dinas Perdagangan Sukoharjo [?] atau pengamatan langsung di pasar | "Pengamatan pekanan di pasar X, tanggal Y" | Selalu bisa. Bisa digabung dengan B (B untuk tren harian, C untuk cek lokal). |
| **D**: tanpa angka | Kartu berisi tautan ke sumber resmi dan penjelasan | "Data harga belum tersedia" | Bila A, B, dan C semuanya tidak memungkinkan |

**Rekomendasi [U]:** pakai A bila T1 berhasil. Bila tidak, pakai **B + C** (tren otomatis berlabel jelas dan cek lokal pekanan). Jangan menampilkan angka B sebagai angka Sukoharjo.

**Hasil T1 [T]:** jalur A1 (Panel Harga level Konsumen) berhasil. Jalur B dan C tidak diperlukan untuk komoditas inti. Pengambilan data dari PC pemilik karena Actions timeout.

### 5.3 Daftar komoditas inti
Delapan komoditas utama tampil di Beranda (6 di HP): beras medium, cabai rawit merah, cabai merah keriting, bawang merah, bawang putih, telur ayam ras, minyak goreng, gula pasir. Komoditas lain di tab Harga: beras premium, daging ayam ras, daging sapi, kedelai, tepung terigu, jagung, cabai merah besar. Ikuti daftar dan satuan yang dipakai sumber terpilih. `komoditas_id` sumber dipetakan ke `id` internal kita di `data/peta_komoditas.csv`, tanpa mengarang ID.

### 5.4 Yang disiapkan pemilik sebelum T1 (sekitar 45 menit)
1. Buka situs Panel Harga Bapanas di Chrome atau Edge desktop.
2. Tekan F12, buka tab **Network**, pilih filter **Fetch/XHR**, centang **Preserve log**, lalu muat ulang halaman.
3. Di UI, pilih tingkat kabupaten/kota bila ada, provinsi Jawa Tengah, Kabupaten Sukoharjo, komoditas cabai rawit merah, dan rentang waktu terpanjang. Ulangi untuk **setiap tingkat harga** yang ada di UI (Produsen, Konsumen, dan lainnya): T1 menemukan bahwa level Produsen hanya mengisi 3 dari 8 komoditas inti.
4. Untuk tiap permintaan yang responsnya berisi angka harga, daftar komoditas, atau daftar wilayah:
   - klik kanan, pilih **Copy → Copy as cURL (bash)**, simpan ke `referensi/harga/panelharga_<isi>.txt`;
   - buka tab Response, simpan ke `referensi/harga/panelharga_<isi>_respons.json` (bila lebih dari 1 MB, simpan sebagian awal saja);
   - **hapus** nilai header `Cookie` dan `Authorization`, tetapi tulis di baris pertama berkas: "ada Authorization: ya/tidak; ada Cookie: ya/tidak".
5. Tangkap layar filter wilayah yang menunjukkan apakah Sukoharjo ada. Simpan sebagai `referensi/harga/panelharga_filter.png`.
6. Ulangi langkah 2–5 untuk PIHPS BI (pilih Jawa Tengah dan periksa daftar kab/kota) dan, bila sempat, SP2KP Kemendag [D].
7. Salin atau tangkap layar halaman ketentuan penggunaan atau footer hak cipta tiap situs ke `referensi/harga/`.
8. Cari publikasi harga bahan pokok dari Pemkab atau Dinas Perdagangan Sukoharjo (situs, Instagram). Catat URL dan frekuensinya di `referensi/harga/catatan_pemilik.md`.

### 5.5 Titik berhenti eksplorasi
- T1 dibatasi **30 panggilan alat dalam 1 sesi**. Tiap kandidat paling banyak 2 percobaan permintaan.
- Sonnet hanya boleh mengulang permintaan yang ada di tangkapan pemilik, dengan mengganti parameter wilayah atau komoditas ke nilai yang terlihat di respons. Sonnet dilarang menebak endpoint baru.
- Bila permintaan butuh token sesi, login, captcha, atau token yang disamarkan, kandidat ditandai "tidak dipakai". Jangan dibobol.
- Keluaran wajib berupa `referensi/keputusan_harga.md` yang berisi matriks kandidat (cakupan, jumlah komoditas, riwayat, autentikasi, ToS, terjangkau dari Actions), jalur terpilih, dan contoh keluaran ternormalisasi.

---

## 6. Arsitektur

### 6.1 Keputusan utama

| Keputusan | Opsi | Pilihan dan alasan |
|---|---|---|
| Hosting | GitHub Pages, Cloudflare Pages, Netlify | **GitHub Pages** [U]. Repo, Actions, dan deploy di satu tempat. Gratis untuk repo publik. Tidak perlu akun lain. Cloudflare Pages lebih cepat di Asia [D], tetapi menambah akun dan integrasi. Bisa dipindah nanti karena situsnya statis murni. |
| Pengambil data | GitHub Actions terjadwal; fetch langsung dari peramban; Cloudflare Worker | **Actions** [U]. Satu tempat untuk normalisasi dan validasi. Situs cepat karena JSON kecil siap pakai. Tidak tergantung CORS sumber [?]. Risikonya pemblokiran IP luar negeri [?], diuji di T0. Cadangannya: skrip yang sama dijalankan dari PC pemilik lewat Task Scheduler, lalu push. |
| Penyimpanan data cepat (cuaca, gempa, udara, hujan, status) | Commit ke git; hanya artefak deploy | **Hanya artefak** [U]. Data ini tidak di-commit agar repo tidak membengkak (8 pembaruan/hari) dan pemilik tidak sering konflik saat pull. Bila sumber gagal, skrip mengunduh versi terakhir dari situs live sebagai cadangan. |
| Data tetap (riwayat harga, data kurasi, poligon, sholat) | — | **Di-commit**. Butuh persistensi dan jarang berubah. |
| Front-end | Vanilla ES modules; Preact+htm; Alpine; Svelte | **Vanilla ES modules** [U]. Tanpa build dan tanpa dependensi. Sonnet paling lancar menulisnya. Ukuran minimal. |
| Grafik | SVG buatan sendiri; Chart.js; uPlot; ECharts | **SVG sendiri untuk sparkline** (sekitar 30 baris) dan **Chart.js 4 (UMD) dimuat malas** hanya di detail tren harga. uPlot lebih kecil tetapi API-nya kurang dikenal sehingga rawan bug. ECharts terlalu besar. |
| Peta | Leaflet; MapLibre; SVG statis | **SVG statis buatan skrip** untuk peta pemilih dan choropleth (0 dependensi, sangat ringan). **Leaflet 1.9.4** dimuat malas untuk peta fasilitas. MapLibre lebih berat dan butuh tile vektor. |
| Pustaka eksternal | CDN; vendoring | **Vendoring** ke `hasil/situs/vendor/` lewat skrip unduh berversi [U]. Tidak tergantung CDN saat runtime, bisa di-cache PWA, dan tidak perlu menghitung SRI. Ini menyimpang dari saran awal soal CDN, dengan alasan tersebut. |
| Font | Inter self-host; font sistem | **Font sistem** [U]: 0 byte dan cepat. |
| Python | stdlib; requests/pandas | **stdlib saja** (`urllib`, `json`, `csv`, `math`, `datetime`). Zona waktu memakai `timezone(timedelta(hours=7))` karena `zoneinfo` di Windows butuh paket tzdata. |

### 6.2 Alur data

```
SUMBER                         SKRIP (skrip/)                   KELUARAN (hasil/situs/data/)
BMKG prakiraan  ─────────────► ambil_cuaca.py      ─┐           cuaca.json          (artefak)
Open-Meteo forecast ─────────► ambil_hujan.py      ─┤           hujan_7hari.json    (artefak)
Open-Meteo air quality ──────► ambil_udara.py      ─┤           udara.json          (artefak)
BMKG gempa ──────────────────► ambil_gempa.py      ─┤           gempa.json          (artefak)
Harga (A/B) ─────────────────► ambil_harga.py      ─┤           harga.json, harga_riwayat.json (commit)
CSV manual harga ────────────► bangun_harga_manual.py┤
Overpass (sekali/bulanan) ───► ambil_batas.py, ambil_fasilitas.py ─► batas_kecamatan.geojson, fasilitas.json (commit)
Kode wilayah, BPS CSV, wiki ─► bangun_wilayah.py, bangun_profil.py ─► kecamatan.json, desa.json, profil_kecamatan.json (commit)
CSV kurasi (layanan, darurat)► bangun_layanan.py   ─┤           layanan.json (commit)
Perhitungan astronomi ───────► hitung_sholat.py    ─┤           sholat_<tahun>.json (commit)
SKB libur ───────────────────► bangun_libur.py     ─┘           libur.json (commit)
                 semua lewat: jalankan_semua.py (pakai umum.py) ──► status.json
                                   │
                              cek_data.py (skema, rentang, kesegaran)
                                   │
GitHub Actions perbarui_dan_terbitkan.yml (cron / push main / manual)
   ├─ modul gagal → pakai versi live terakhir, status "basi"
   ├─ commit data tetap bila berubah
   └─ upload-pages-artifact(hasil/situs) → deploy-pages
                                   │
Peramban: index.html → js/utama.js → fetch JSON (cache:'no-cache') → render
          → salinan terakhir di localStorage → service worker (1.0)
```

### 6.3 Struktur folder

```
dasbor_sukoharjo/                      (repo git sendiri, publik, lihat K1)
├─ README.md                           status, cara menjalankan, sumber, lisensi
├─ .gitignore                          data/mentah/, _tmp/, _arsip/, __pycache__/, berkas artefak (lihat 6.5)
├─ .github/workflows/
│  ├─ uji_jaringan.yml                 T0, boleh dihapus setelah T4
│  └─ perbarui_dan_terbitkan.yml       T4
├─ skrip/
│  ├─ umum.py                          http, amplop, tulis atomik, status, waktu WIB, cadangan live
│  ├─ jalankan_semua.py                orkestrator modul sesuai pemicu
│  ├─ cek_data.py                      validasi semua JSON
│  ├─ cek_situs.py                     anggaran ukuran, tautan internal, tanpa URL eksternal liar
│  ├─ cek_tampilan.ps1                 server lokal, tangkap layar, dump-dom
│  ├─ uji_jaringan.py                  T0
│  ├─ uji_harga.py                     T1
│  ├─ ambil_vendor.py                  unduh Leaflet, Chart.js, ikon Lucide (berversi)
│  ├─ ambil_kode_wilayah.py, bangun_wilayah.py, ambil_batas.py, bangun_peta_svg.py
│  ├─ ambil_cuaca.py, ambil_hujan.py, ambil_udara.py, ambil_gempa.py
│  ├─ ambil_harga.py | bangun_harga_manual.py
│  ├─ hitung_sholat.py, bangun_libur.py
│  ├─ ambil_fasilitas.py, bangun_layanan.py
│  ├─ ambil_ringkasan_wiki.py, bangun_profil.py, cek_profil.py
│  ├─ bangun_indeks_cari.py, bangun_halaman_kecamatan.py
│  └─ uji_umum.py                      unit test kecil (unittest stdlib) untuk fungsi murni
├─ data/                               kurasi buatan sendiri (di-commit)
│  ├─ kecamatan.csv                    slug,kode,nama,adm4_acuan,desa_acuan
│  ├─ statistik_kecamatan.csv          diisi pemilik dari BPS
│  ├─ profil_kecamatan.json            deskripsi dan ciri khas (draf/ditinjau)
│  ├─ peta_komoditas.csv               id internal ↔ id sumber, nama, satuan, kategori
│  ├─ harga_manual.csv                 jalur C
│  ├─ kontak_darurat.csv, layanan_publik.csv, transportasi.csv, info_rutin.csv (BBM, LPG, UMK)
│  ├─ libur_<tahun>.csv
│  └─ mentah/                          (diabaikan git) unduhan mentah
├─ referensi/
│  ├─ rencana_dasbor.md                dokumen ini
│  ├─ komponen.md                      katalog kelas CSS dan fungsi UI (≤ 80 baris, ditulis di T2)
│  ├─ keputusan_harga.md               hasil T1
│  ├─ harga/                           tangkapan DevTools pemilik
│  ├─ contoh_bmkg.json                 satu respons asli (untuk pemetaan bidang)
│  └─ uji_jaringan_actions.txt         hasil T0
├─ hasil/situs/                        yang di-deploy
│  ├─ index.html, gaya.css, manifest.webmanifest, sw.js, robots.txt, sitemap.xml, 404.html
│  ├─ js/ utama.js, data.js, format.js, komponen.js, grafik.js, peta.js, kalender.js, cari.js
│  ├─ js/tampilan/ beranda.js, harga.js, cuaca.js, wilayah.js, layanan.js, tentang.js, status.js
│  ├─ data/                            JSON (sebagian artefak, sebagian commit)
│  ├─ peta/ peta_kecamatan.svg
│  ├─ ikon/ sprite.svg, logo.svg, ikon-192.png, ikon-512.png
│  ├─ vendor/ leaflet/, chartjs/, VERSI.txt
│  └─ kecamatan/<slug>/index.html      halaman statis (T9)
├─ _tmp/  _arsip/                      (diabaikan git)
```

### 6.4 Skema JSON

#### 6.4.1 Amplop bersama (semua berkas kecuali GeoJSON dan SVG)
```json
{
  "versi_skema": 1,
  "modul": "cuaca",
  "diperbarui": "2025-06-01T08:17:00+07:00",
  "status": "ok",
  "catatan": "",
  "sumber": [{"nama": "BMKG", "url": "https://api.bmkg.go.id/", "lisensi": "Wajib mencantumkan BMKG sebagai sumber"}],
  "contoh": false,
  "data": {}
}
```
Penjelasan bidang:
- `status`: salah satu dari `ok`, `sebagian`, `basi`, `gagal`.
- `diperbarui`: waktu data terakhir berhasil diambil, bukan waktu skrip dijalankan.
- `contoh: true`: dipakai untuk data dummy di T2. UI lalu menampilkan lencana "CONTOH".
- Tanggal di contoh di atas hanya ilustrasi.

#### 6.4.2 status.json
```json
{"versi_skema":1,"dibangun":"2025-06-01T08:20:00+07:00","pemicu":"schedule",
 "modul":{"cuaca":{"status":"ok","terakhir_sukses":"...","terakhir_coba":"...","pesan":"12/12 kecamatan","ambang_jam":[9,24]}}}
```
`ambang_jam` berisi [batas segar, batas basi], dalam jam.

#### 6.4.3 cuaca.json → `data`
```json
{"kecamatan":[{"slug":"weru","adm4":"33.11.01.2001","desa_acuan":"<nama desa>","lat":-7.0,"lon":110.0,
  "analisis":"2025-06-01T06:00:00+07:00","basi":false,
  "prakiraan":[{"waktu":"2025-06-01T09:00:00+07:00","suhu":29,"kelembapan":72,"kode":3,"deskripsi":"Berawan",
                "angin_kmj":8,"arah_angin":"Tenggara","awan_persen":60,"hujan_mm":0.0}]}]}
```
**Pemetaan bidang BMKG [D].** Dugaan perencana dari struktur API BMKG 2024: `lokasi` (`desa`, `kecamatan`, `lat`, `lon`), `data[0].cuaca` berupa array bersarang berisi `local_datetime`, `t`, `hu`, `weather`, `weather_desc`, `ws`, `wd`, `tcc`, `tp`, `analysis_date`. Satuan `ws` [?]. **Wajib diverifikasi** dari `referensi/contoh_bmkg.json` di T4. Bila berbeda, ikuti respons asli dan perbarui bagian ini.

**Pemetaan ikon** berdasarkan `kode` [D: 0 cerah, 1–2 cerah berawan, 3 berawan, 4 berawan tebal, 5/10/45 kabur/asap/kabut, 60 hujan ringan, 61 hujan sedang, 63 hujan lebat, 80 hujan lokal, 95/97 petir]. Bila kode tidak dikenal, cocokkan kata kunci di `deskripsi`.

#### 6.4.4 hujan_7hari.json → `data`
```json
{"model":"Open-Meteo","kecamatan":[{"slug":"weru","hari":[{"tanggal":"2025-06-01","hujan_mm":4.2,"peluang_persen":70,"suhu_maks":31,"suhu_min":23}]}]}
```

#### 6.4.5 udara.json → `data`
```json
{"titik":{"nama":"Pusat Kabupaten","lat":0,"lon":0},"skala":"US AQI (model)",
 "jam":[{"waktu":"...","aqi":42,"pm2_5":12.1,"pm10":20.3,"uv":6.1}],"kini":{"aqi":42,"kategori":"Baik","uv":6.1,"uv_kategori":"Tinggi"}}
```

#### 6.4.6 gempa.json → `data`
```json
{"terbaru":{"waktu":"...","magnitudo":4.8,"kedalaman_km":10,"lat":-8.5,"lon":110.2,"wilayah":"...","dirasakan":"...","potensi":"...","jarak_km":95},
 "dirasakan":[{"...":"bidang sama"}],"relevan_24jam":true}
```
`relevan_24jam` bernilai true bila ada gempa dalam 24 jam terakhir dengan jarak ≤ 200 km, atau teks `dirasakan` memuat "Sukoharjo", "Solo", atau "Surakarta" [U].

#### 6.4.7 harga.json → `data`
```json
{"tingkat":"kabupaten","wilayah_label":"Kab. Sukoharjo","label_peringatan":"",
 "tanggal_data":"2025-06-01",
 "komoditas":[{"id":"cabai_rawit_merah","nama":"Cabai rawit merah","kategori":"bumbu","satuan":"kg",
   "harga":45000,"harga_sebelumnya":43000,"tanggal_sebelumnya":"2025-05-31","ubah_persen":4.7,
   "rata_7h":44100,"ubah_7h_persen":2.0,"acuan":null}]}
```
`tingkat` bernilai salah satu: `kabupaten`, `kota_terdekat`, `provinsi`, `manual`. `kategori` bernilai salah satu: `pokok`, `bumbu`, `protein`, `minyak_gula`. `acuan` berisi HET atau HAP bila tersedia dari sumber resmi [D], selain itu `null`.

#### 6.4.8 harga_riwayat.json → `data`
```json
{"tingkat":"kabupaten","seri":{"cabai_rawit_merah":[["2025-05-01",42000],["2025-05-02",43500]]}}
```
Simpan maksimal 400 hari.

#### 6.4.9 kecamatan.json → `data` (kecil, dimuat di semua halaman)
```json
{"kecamatan":[{"slug":"weru","nama":"Weru","kode":"33.11.01","lat":0,"lon":0,"tetangga":["bulu","tawangsari"]}]}
```
Daftar `tetangga` di contoh ini hanya ilustrasi. Isi sebenarnya dihitung skrip.

#### 6.4.10 profil_kecamatan.json → `data`
```json
{"kecamatan":[{"slug":"weru","luas_km2":0,"penduduk":0,"kepadatan":0,"tahun_data":2024,"jumlah_desa":0,"jumlah_kelurahan":0,
  "deskripsi":"...","status_isi":"draf","ciri_khas":[{"teks":"...","url":"https://..."}],
  "fasilitas":{"rumah_sakit":0,"puskesmas_klinik":0,"apotek":0,"sekolah":0,"pasar":0},
  "kantor":{"alamat":"...","telepon":null,"url":null},"tanggal_verifikasi":"2025-06-01"}]}
```
Angka 0 hanya placeholder. Angka sebenarnya dari CSV pemilik.

#### 6.4.11 desa.json → `data`
```json
{"desa":[{"kode":"33.11.01.2001","nama":"...","jenis":"desa","kec":"weru"}]}
```

#### 6.4.12 fasilitas.json → `data`
```json
{"fasilitas":[{"id":"osm:n123","jenis":"puskesmas_klinik","nama":"...","lat":0,"lon":0,"kec":"weru","alamat":null,"telepon":null}]}
```
`jenis` bernilai salah satu: `rumah_sakit`, `puskesmas_klinik`, `apotek`, `sekolah`, `perguruan_tinggi`, `pasar`, `kantor_pemerintah`, `polisi`, `pemadam`, `kantor_pos`, `stasiun`, `terminal`.

#### 6.4.13 layanan.json → `data`
```json
{"darurat":[{"nama":"Panggilan darurat","nomor":"112","cakupan":"nasional","sumber":"https://...","tanggal_verifikasi":"..."}],
 "layanan":[{"nama":"...","kategori":"kependudukan","alamat":"...","jam":"Senin–Jumat 08.00–15.00","telepon":null,"url":"...","lat":null,"lon":null,"sumber":"...","tanggal_verifikasi":"..."}],
 "transportasi":[...], "info_rutin":[{"jenis":"umk","label":"UMK Sukoharjo","nilai":0,"satuan":"Rp/bulan","berlaku":"2025-01-01","sumber":"..."}]}
```
Nilai `jam` di contoh hanya ilustrasi. **Aturan keras:** baris dengan `tanggal_verifikasi` kosong tidak ditampilkan.

#### 6.4.14 sholat_<tahun>.json → `data`
```json
{"lokasi":{"nama":"Kab. Sukoharjo","lat":0,"lon":0},"metode":"Kemenag: subuh 20°, isya 18°, ihtiyat 2 menit",
 "hari":{"2025-06-01":["04:12","04:22","05:37","11:30","14:50","17:22","18:34"]}}
```
Urutan kolom: imsak, subuh, terbit, dzuhur, asar, maghrib, isya. Jam di contoh hanya ilustrasi.

#### 6.4.15 libur.json → `data`
```json
{"tahun":2025,"hari":[{"tanggal":"2025-01-01","nama":"Tahun Baru","jenis":"libur_nasional"}],"sumber_skb":"https://..."}
```
`jenis` bernilai `libur_nasional` atau `cuti_bersama`.

#### 6.4.16 cari.json
Larik `[{"t":"Weru","j":"kecamatan","u":"#/wilayah/weru","k":"weru kec"}]`. `t` adalah teks, `j` jenis, `u` URL, `k` kata kunci tambahan yang dinormalisasi.

#### 6.4.17 batas_kecamatan.geojson
FeatureCollection. Tiap feature punya `properties.slug`. Koordinat dibulatkan 4 desimal dan disederhanakan Douglas–Peucker dengan toleransi sekitar 0,0004°. Target di bawah 60 KB.

### 6.5 Pembaruan terjadwal

**Jadwal (UTC; WIB = UTC+7) [U]:**

| Cron | Modul |
|---|---|
| `17 */3 * * *` | cuaca, hujan, udara, gempa |
| `41 3,9 * * *` | yang di atas, ditambah harga (10.41 dan 16.41 WIB) |
| `5 2 1 * *` | yang di atas, ditambah fasilitas (bulanan) |
| push ke `main` dan `workflow_dispatch` | modul cepat, lalu deploy |

Menit sengaja ganjil karena cron Actions sering terlambat di menit :00 [D].

**Fakta Actions yang relevan:**
- Commit yang dibuat dengan `GITHUB_TOKEN` tidak memicu workflow lain [D, perilaku terdokumentasi GitHub]. Karena itu satu workflow mengerjakan ambil, commit, dan deploy sekaligus.
- Jadwal di repo publik dinonaktifkan setelah 60 hari tanpa aktivitas repo [D]. Mitigasinya ada di bagian 10.

**Kerangka workflow** (pola standar dokumentasi GitHub Pages; versi action [D], periksa di Marketplace bila gagal):
```yaml
name: perbarui_dan_terbitkan
on:
  schedule: [{cron: "17 */3 * * *"}, {cron: "41 3,9 * * *"}, {cron: "5 2 1 * *"}]
  push: {branches: [main]}
  workflow_dispatch:
permissions: {contents: write, pages: write, id-token: write}
concurrency: {group: terbitkan, cancel-in-progress: false}
jobs:
  terbitkan:
    runs-on: ubuntu-latest
    environment: {name: github-pages, url: "${{ steps.deploy.outputs.page_url }}"}
    env: {SITUS_URL: "${{ vars.SITUS_URL }}"}
    steps:
      - uses: actions/checkout@v4
      - run: python3 skrip/jalankan_semua.py --pemicu "${{ github.event_name }}" --jadwal "${{ github.event.schedule }}"
      - run: python3 skrip/cek_data.py --mode ci
      - run: |
          git config user.name "bot-dasbor"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add hasil/situs/data/harga.json hasil/situs/data/harga_riwayat.json hasil/situs/data/fasilitas.json || true
          git diff --cached --quiet || (git commit -m "data: pembaruan otomatis" && git pull --rebase && git push)
      - uses: actions/upload-pages-artifact@v3
        with: {path: hasil/situs}
      - id: deploy
        uses: actions/deploy-pages@v4
```

**Berkas artefak** yang tidak di-commit dan dicantumkan di `.gitignore`: `hasil/situs/data/{cuaca,hujan_7hari,udara,gempa,status}.json`. Untuk pengembangan lokal, jalankan `python skrip/jalankan_semua.py --modul cuaca,...`.

### 6.6 Penanganan error dan kegagalan sebagian
1. `umum.ambil_json`:
   - timeout 20 detik, 3 kali coba dengan jeda 2, 4, dan 8 detik;
   - User-Agent `DasborSukoharjo/1.0 (+<URL repo>)`;
   - jeda 1,5 detik antarpermintaan ke host yang sama [U]. Batas laju BMKG [D] diduga sekitar 60 permintaan/menit/IP.
2. Tiap modul berjalan terpisah (`try/except` di `jalankan_semua.py`). Satu modul gagal tidak menghentikan modul lain. Exit code workflow tetap 0 kecuali `cek_data.py` menemukan berkas yang **rusak** (bukan sekadar basi).
3. Kegagalan sebagian per kecamatan:
   - nilai lama dari versi sebelumnya dipakai untuk kecamatan yang gagal, dengan `basi: true`;
   - `status: "sebagian"` dan `catatan: "11/12 kecamatan"`.
4. Sumber versi sebelumnya: berkas lokal di repo bila ada (data tetap), atau `SITUS_URL/data/<nama>.json` (data artefak). Bila keduanya tidak ada, tulis amplop `status: "gagal"` dengan `data` kosong. UI lalu menampilkan keadaan galat.
5. Penulisan atomik: tulis ke `.tmp`, lalu `os.replace`. JSON ringkas (`separators=(",",":")`, `ensure_ascii=False`).
6. Pemeriksaan kewajaran sebelum menimpa: suhu 10–42 °C, kelembapan 0–100, harga > 0, perubahan harian harga ≤ 60% (di atas itu ditandai `perlu_cek: true`, tidak dibuang), jumlah kecamatan 12.

### 6.7 Cache dan waktu pembaruan
- GitHub Pages diduga mengirim `Cache-Control: max-age=600` [D]. Klien memanggil `fetch(url, {cache: "no-cache"})` agar memvalidasi ulang dengan ETag.
- `data.js` menyimpan salinan JSON terakhir ke `localStorage` (kunci `data:<nama>`). Bila jaringan gagal, salinan itu ditampilkan dengan spanduk "Mode luring, data per <waktu>".
- Service worker (T9):
  - aset aplikasi memakai cache-first dengan nama cache berversi `sh-v<N>`;
  - JSON memakai stale-while-revalidate;
  - tile peta tidak di-cache.
- Setiap kartu menampilkan "Diperbarui 3 jam lalu · 08.17 WIB · BMKG", dihitung dari `diperbarui`.

**Ambang kesegaran (jam, [segar, basi])** [U]:

| Modul | Segar | Basi |
|---|---|---|
| cuaca, udara | 9 | 24 |
| hujan | 24 | 48 |
| gempa | 6 | 24 |
| harga otomatis | 48 | 120 |
| harga manual | 8 hari | 15 hari |
| fasilitas | 45 hari | 90 hari |
| layanan (dari `tanggal_verifikasi`) | 180 hari | 365 hari |
| sholat, libur | tahun harus sama dengan tahun berjalan | — |

---

## 7. Desain antarmuka dan pengalaman pengguna

### 7.1 Navigasi dan tata letak
- **Rute hash:**
  - `#/`, `#/harga`, `#/harga/<id>`, `#/cuaca`
  - `#/wilayah`, `#/wilayah/<slug>`, `#/wilayah/bandingkan?a=weru&b=bulu`
  - `#/layanan`, `#/layanan/peta?jenis=puskesmas_klinik`
  - `#/tentang`, `#/status`, `#/cari?q=`
  - Parameter `?kec=<slug>` bisa ditambahkan di rute mana pun agar tautan bisa dibagikan.
  - Parameter `?tema=gelap|terang` dipakai untuk uji tangkapan layar.
- **HP (< 600 px):**
  - kepala aplikasi tetap setinggi 56 px berisi logo, nama, chip kecamatan "Kec. Weru ▾", tombol cari, dan tombol tema;
  - nav bawah 64 px ditambah `env(safe-area-inset-bottom)`, berisi 5 tab (Beranda, Harga, Cuaca, Wilayah, Layanan) dengan ikon 24 px dan label 12 px;
  - tab aktif diberi pil `--utama-lemah` berukuran 56×32 di belakang ikon.
- **Tablet (600–959 px):** konten 2 kolom.
- **Desktop (≥ 960 px):**
  - nav pindah ke rel kiri selebar 88 px;
  - grid `repeat(auto-fill, minmax(320px, 1fr))` dengan lebar maksimal 1200 px;
  - kartu hero mengambil 2 kolom.

### 7.2 Sistem desain (nilai pasti, ditulis ke `:root` di `gaya.css`)

**Warna, mode terang** (`:root`):

| Token | Heks | Pakai |
|---|---|---|
| `--latar` | #F5F7F4 | latar halaman |
| `--permukaan` | #FFFFFF | kartu, kepala, nav |
| `--permukaan-2` | #EDF1EC | isian, baris selang-seling, poligon peta |
| `--garis` | #DCE3DA | border 1 px |
| `--teks` | #17211C | teks utama |
| `--teks-2` | #526058 | teks sekunder, meta |
| `--teks-3` | #7A867F | hanya placeholder/nonaktif |
| `--utama` | #1C7556 | aksi, tab aktif, garis grafik |
| `--utama-di-atas` | #FFFFFF | teks di atas `--utama` |
| `--utama-lemah` | #E2F0E8 | pil aktif, latar ikon kartu |
| `--aksen` | #E3A21A | isian matahari/sorotan (bukan untuk teks) |
| `--aksen-lemah` | #FBF0D6 | spanduk info hangat |
| `--info` / `--info-lemah` | #2C6CB0 / #E3EEF9 | hujan, info |
| `--sukses` / `--sukses-lemah` | #2E7D32 / #E5F2E6 | harga turun, udara baik |
| `--peringatan` / `--peringatan-lemah` | #A86200 / #FDF0DC | data basi, label provinsi |
| `--bahaya` / `--bahaya-lemah` | #C0392B / #FBE6E3 | harga naik, gempa, galat |

**Warna, mode gelap** (`[data-tema="gelap"]`, juga dipakai otomatis lewat `prefers-color-scheme: dark` bila pengguna belum memilih):

| Token | Nilai |
|---|---|
| `--latar` | #0E1412 |
| `--permukaan` | #151D1A |
| `--permukaan-2` | #1C2622 |
| `--garis` | #283430 |
| `--teks` | #E6ECE8 |
| `--teks-2` | #A1AEA7 |
| `--teks-3` | #6F7C75 |
| `--utama` | #4CC38A |
| `--utama-di-atas` | #0E1412 |
| `--utama-lemah` | #173A2B |
| `--aksen` / `--aksen-lemah` | #F2BD4B / #3A2F12 |
| `--info` / `--info-lemah` | #6EA8E6 / #16263A |
| `--sukses` / `--sukses-lemah` | #5CC27A / #163222 |
| `--peringatan` / `--peringatan-lemah` | #F0B44C / #3A2A10 |
| `--bahaya` / `--bahaya-lemah` | #F27A6B / #3D1A17 |

Target kontras: WCAG AA, yaitu minimal 4,5:1 untuk teks badan dan 3:1 untuk teks ≥ 18 px atau elemen non-teks. Pasangan `--teks-2`/`--permukaan`, `--utama`/`--permukaan`, `--utama-di-atas`/`--utama`, `--peringatan`/`--peringatan-lemah`, dan `--bahaya`/`--bahaya-lemah` diuji skrip di T9 (`cek_kontras.py`). Bila ada pasangan yang gagal, gelapkan atau terangkan nilai heksnya maksimal 10% dan catat perubahannya di sini. `--aksen` tidak boleh dipakai sebagai warna teks.

**Warna kategori data:**

| Pemakaian | Nilai |
|---|---|
| Seri grafik, urutan | `--utama`, `--info`, `--aksen`, `--bahaya`, `#7A5AC8` |
| Choropleth hijau 5 kelas, terang | #E2F0E8, #B9DDCB, #86C4A6, #4FA57F, #1C7556 |
| Choropleth hijau 5 kelas, gelap | #173A2B, #1F5A40, #2E7D59, #3FA374, #4CC38A |

Kategori kualitas udara (US AQI) selalu ditampilkan dengan teksnya:

| Rentang AQI | Kategori | Warna |
|---|---|---|
| 0–50 | Baik | #2E7D32 |
| 51–100 | Sedang | #B38600 |
| 101–150 | Tidak sehat bagi kelompok sensitif | #D9822B |
| 151–200 | Tidak sehat | #C0392B |
| 201–300 | Sangat tidak sehat | #7B3FA0 |
| > 300 | Berbahaya | #7A1F2B |

Kategori UV: 0–2 rendah, 3–5 sedang, 6–7 tinggi, 8–10 sangat tinggi, 11+ ekstrem.

**Tipografi:**
- Font: `system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", Arial, sans-serif`.
- Semua angka memakai `font-variant-numeric: tabular-nums`.

| Token | Ukuran/tinggi baris | Pakai |
|---|---|---|
| `--uk-1` | 12/16 | meta, label sumbu, label nav |
| `--uk-2` | 14/20 | label, teks sekunder, baris daftar |
| `--uk-3` | 16/24 | badan (minimum teks bacaan) |
| `--uk-4` | 18/26 | judul kartu besar, nama komoditas di detail |
| `--uk-5` | 22/28 | judul halaman |
| `--uk-6` | 28/34 | angka besar kartu |
| `--uk-7` | 40/44 | suhu hero |

Ketebalan: 400 badan, 500 label, 600 judul, 700 angka besar. Judul memakai `letter-spacing: -0.01em`.

**Spasi, sudut, dan bayangan:**

| Kelompok | Token |
|---|---|
| Spasi | `--r-1` 4, `--r-2` 8, `--r-3` 12, `--r-4` 16, `--r-5` 24, `--r-6` 32, `--r-7` 48 (px) |
| Sudut | `--sudut-1` 8 (chip, input), `--sudut-2` 12 (tombol, baris), `--sudut-3` 16 (kartu, lembar), `--sudut-penuh` 999 |
| Bayangan terang | `--bayang-1: 0 1px 2px rgba(17,26,21,.06), 0 1px 3px rgba(17,26,21,.08)`; `--bayang-2: 0 8px 24px rgba(17,26,21,.14)` |
| Bayangan gelap | `--bayang-1: none` (kartu dipisah dengan border); `--bayang-2: 0 8px 24px rgba(0,0,0,.5)` |

**Tata letak:**
- Padding samping 16 px di HP, 24 px pada ≥ 600 px.
- Jarak antarkartu 12 px di HP, 16 px pada ≥ 960 px.
- Breakpoint: 600 dan 960 px.
- Z-index: kepala/nav 10, lembar bawah 30, toast 40.
- Target sentuh minimal 44×44 px.

**Gerak:**
- `--gerak-cepat: 120ms`, `--gerak: 180ms`, `--kurva: cubic-bezier(.2,.8,.2,1)`.
- Tombol saat ditekan: `transform: scale(.98)`.
- Masuk tampilan: fade dan `translateY(4px → 0)` selama 180 ms.
- Lembar bawah: `translateY(100% → 0)` selama 220 ms.
- Skeleton: shimmer gradien 1,2 detik.
- Bila `prefers-reduced-motion: reduce`, semua transisi dibuat 0 ms dan shimmer dimatikan.
- Tidak ada animasi angka berjalan atau parallax.

**Ikon:**
- Pakai Lucide (lisensi ISC) [D: paket `lucide-static`], diunduh sekali oleh `ambil_vendor.py` dan digabung menjadi `ikon/sprite.svg` (`<symbol id="i-nama">`).
- Gaya: stroke 2, ukuran 20 atau 24, warna `currentColor`.
- Daftar ikon [D, nama perlu dicek di paket]: house, shopping-basket, cloud-sun, map, life-buoy, search, sun, moon, cloud, cloud-rain, cloud-drizzle, cloud-lightning, cloud-fog, haze, wind, droplets, thermometer, trending-up, trending-down, minus, triangle-alert, info, clock, map-pin, navigation, phone, external-link, chevron-right, chevron-down, x, refresh-cw, activity, leaf, sunrise, sunset, moon-star, calendar, hospital, pill, graduation-cap, bus, train-front, store, briefcase, fuel, landmark, share-2, locate.
- Bila suatu nama tidak ada di paket, ganti dengan ikon terdekat dan catat penggantinya di `vendor/VERSI.txt`.
- Logo: SVG buatan sendiri berupa persegi bersudut 8 berwarna `--utama` dengan huruf "S" putih. Jangan memakai lambang daerah.

**Komponen** (nama kelas tetap; katalog ringkasnya ditulis di `referensi/komponen.md` pada T2):

| Komponen | Kelas | Spesifikasi |
|---|---|---|
| Kartu | `.kartu`, `__kepala`, `__ikon`, `__judul`, `__isi`, `__meta`, `--hero`, `--lebar` | `--permukaan`, border 1 px `--garis`, sudut 16, padding 16, `--bayang-1`. Ikon 20 px di kotak 32 px bersudut 8 berlatar `--utama-lemah` dan berwarna `--utama`. Judul `--uk-2`/600 `--teks-2`. Meta `--uk-1` `--teks-2`, di bawah, didahului titik kesegaran 8 px. |
| Titik kesegaran | `.segar`, `--segar`, `--lama`, `--basi` | Warna `--sukses`, `--peringatan`, `--bahaya`. Selalu disertai teks waktu. |
| Lencana | `.lencana`, `--naik`, `--turun`, `--tetap`, `--info`, `--peringatan`, `--bahaya`, `--contoh` | Tinggi 24, padding 0 8, sudut penuh, `--uk-1`/600. Latar `*-lemah`, teks warna penuh. Harga naik ditandai ▲ dengan `--bahaya`, turun ▼ dengan `--sukses`, tetap "–" dengan `--teks-2`, karena bagi pembeli kenaikan harga itu buruk. Teks seperti "▲ 4,7%" selalu ada, jadi informasi tidak bergantung pada warna saja. |
| Chip | `.chip`, `--aktif` | Tinggi 36, padding 0 12, sudut 8, border `--garis`. Saat aktif: latar `--utama-lemah`, border `--utama`, teks `--utama`. |
| Tombol | `.tombol`, `--utama`, `--sekunder`, `--teks`, `--besar` | Tinggi 44 (besar 52), sudut 12, `--uk-3`/600 |
| Tab segmen | `.segmen` | Wadah `--permukaan-2` sudut 12 padding 4. Item aktif `--permukaan` dengan `--bayang-1`. |
| Daftar | `.daftar`, `.baris` | Baris minimal 56 px, pemisah 1 px `--garis`, chevron di kanan bila bisa diketuk |
| Lembar bawah | `.lembar` | Sudut atas 16, pegangan 32×4, `--bayang-2`, latar redup rgba(0,0,0,.4). Tutup lewat Esc, ketuk latar, atau tombol ×. Fokus terkunci di dalam lembar. |
| Spanduk | `.spanduk`, `--info`, `--peringatan`, `--bahaya` | Strip penuh di atas konten, ikon dan teks `--uk-2`, opsional tombol tutup |
| Strip jam | `.strip-jam` | Gulir horizontal dengan `scroll-snap`. Sel 64 px berisi jam, ikon 24, suhu 600, dan hujan mm bila > 0. |
| Skeleton | `.kerangka` | Blok `--permukaan-2` dengan shimmer, tinggi menyesuaikan kartu |
| Keadaan | `.keadaan`, `--kosong`, `--galat`, `--luring` | Ikon 32 `--teks-2`, judul `--uk-3`/600, penjelasan `--uk-2`, tombol "Coba lagi" bila galat |
| Tabel | `.tabel` | `--uk-2`, angka rata kanan, kepala lengket, baris selang-seling `--permukaan-2` |
| Toast | `.toast` | Bawah tengah, di atas nav, hilang otomatis setelah 3 detik, `aria-live="polite"` |

**Gaya grafik:**
- Garis 2 px `--utama`; area bergradien `--utama` dari opasitas 0,18 ke 0.
- Gridline horizontal saja, 1 px `--garis`, putus-putus 2/4.
- Label sumbu `--uk-1` `--teks-2`. Maksimal 4 label Y dan 5 label X.
- Tooltip `--permukaan` dengan `--bayang-2`, sudut 8, berisi tanggal dan "Rp 45.000".
- Tanpa legenda bila hanya satu seri.
- Setiap grafik punya tombol "Lihat tabel" yang membuka `.tabel` sebagai alternatif aksesibel.
- Sparkline: SVG 96×28, garis 1,5 px berwarna sesuai arah perubahan 7 hari, titik terakhir 3 px.

**Gaya peta SVG:**
- Poligon `--permukaan-2` dengan stroke `--garis` 1 px.
- Hover atau fokus: stroke `--utama` 1,5 px.
- Terpilih: isian `--utama-lemah`, stroke `--utama` 2 px.
- Label nama di centroid, `--uk-1`/500. Label disembunyikan bila lebar peta < 320 px; nama tetap muncul lewat lembar daftar.
- Choropleth memakai 5 kelas di atas, disertai legenda dan nilai.

### 7.3 Hierarki Beranda (urutan di HP)
1. **Spanduk kondisional**, maksimal satu, dengan prioritas: gempa relevan 24 jam, lalu hujan lebat di kecamatan terpilih (kode ≥ 63 dalam 12 jam ke depan), lalu AQI > 100, lalu mode luring atau data basi.
2. **Kartu hero cuaca** untuk kecamatan terpilih:
   - ikon 48 px, suhu `--uk-7`, deskripsi;
   - rentang min/maks hari ini, kelembapan, angin;
   - strip jam berisi 8 slot ke depan;
   - tautan "3 hari ke depan".
3. **Dua kartu kecil berdampingan:**
   - Sholat: waktu berikutnya, jamnya, dan hitung mundur "dalam 1 j 12 m" yang diperbarui tiap menit, bukan tiap detik.
   - Hari ini: "Senin Legi, 2 Juni 2025", Hijriah perkiraan, dan libur terdekat. Tanggal ini hanya contoh format.
4. **Kartu harga:**
   - 6 komoditas inti dalam baris berisi nama, harga, lencana perubahan, dan sparkline;
   - label cakupan (spanduk kuning kecil bila tingkat bukan kabupaten);
   - tombol "Semua harga".
5. **Kartu hujan 7 hari:** bar mini per hari dan teks seperti "3 hari kering berturut-turut mulai Kamis". Teks ini dihitung dari aturan hujan < 1 mm [U].
6. **Kartu udara dan UV:** kategori dan saran singkat (misalnya "UV tinggi pukul 10–14, pakai pelindung").
7. **Kartu darurat:** tombol besar "Telepon 112" (`tel:112`, hanya bila terverifikasi) dan tautan "Nomor lain dan layanan".
8. **Kartu "Kenali Kec. X":** dua angka kunci dan tautan profil.
9. **Footer:** sumber data, "Bukan situs resmi Pemerintah Kabupaten Sukoharjo", tautan Status data, Laporkan kesalahan, dan Tentang.

Di desktop, hero cuaca mengambil 2 kolom dan kartu sholat serta hari ini ada di kolom ke-3. Kartu harga mengambil 2 kolom dan hujan serta udara di kolom ke-3.

### 7.4 Halaman lain
- **Harga:**
  - segmen kategori (Semua, Pokok, Bumbu, Protein, Minyak & gula);
  - urutkan berdasarkan nama, kenaikan terbesar, atau penurunan terbesar;
  - kolom cari;
  - tiap baris berisi harga, perubahan harian, perubahan 7 hari, dan sparkline 30 hari;
  - detail `#/harga/<id>`: angka besar, grafik Chart.js dengan pilihan 30/90/365 hari, min/maks/rata-rata dalam periode, acuan HET/HAP bila ada, dan tabel.
- **Cuaca:**
  - chip kecamatan yang bisa digulir;
  - segmen Hari ini / 3 hari / Hujan 7 hari;
  - grafik suhu SVG sederhana di atas strip jam;
  - tabel "Bandingkan 12 kecamatan saat ini" (ikon, suhu, hujan), bisa diurutkan.
- **Wilayah:**
  - peta SVG yang bisa diketuk;
  - pemilih metrik choropleth (penduduk, kepadatan, luas, fasilitas kesehatan per 10.000 penduduk);
  - tabel 12 kecamatan yang bisa diurutkan;
  - tombol "Bandingkan dua kecamatan";
  - detail profil sesuai bagian 4.2.
- **Layanan:**
  - segmen Darurat, Kesehatan, Layanan publik, Transportasi, Kerja & harga BBM;
  - daftar dengan saring per kecamatan dan "Terdekat dari saya" (geolokasi opsional, jarak dihitung di perangkat);
  - tombol "Peta" membuka Leaflet dengan penanda berwarna per jenis dan chip filter;
  - tiap item punya tautan telepon, tautan rute (`https://www.google.com/maps/dir/?api=1&destination=<lat>,<lon>` [D, format URL Google Maps yang terdokumentasi]), dan tautan OSM.
- **Status:** tabel per modul berisi status, waktu sukses terakhir, dan pesan.
- **Tentang:** tujuan, pernyataan bukan situs resmi, sumber dan lisensi, metode (perhitungan sholat, label harga), kontak dan umpan balik.

### 7.5 Pemilih kecamatan
- Chip di kepala aplikasi membuka lembar bawah yang berisi:
  - kolom cari, yang juga mencocokkan nama desa dari desa.json lalu memetakannya ke kecamatan;
  - tombol "Gunakan lokasi saya" (point-in-polygon di perangkat, tanpa mengirim lokasi ke mana pun);
  - peta SVG mini;
  - daftar 12 kecamatan.
- Pilihan disimpan di `localStorage.kec`. Bawaan: `sukoharjo`.
- Semua tampilan membaca satu status global dan dirender ulang saat pilihan berubah (event `kec:ubah`).

### 7.6 Kinerja, aksesibilitas, dan keadaan kosong atau error
- **Anggaran ukuran** (dicek `cek_situs.py`):
  - HTML + CSS + JS awal ≤ 60 KB setelah gzip;
  - JSON awal Beranda (kecamatan, cuaca, harga, status) ≤ 40 KB;
  - sprite ikon ≤ 15 KB;
  - Leaflet dan Chart.js hanya dimuat lewat `muatSkrip()` saat dibutuhkan.
- Target LCP < 2,5 detik di 4G lambat, diukur dengan PageSpeed Insights oleh pemilik setelah deploy.
- `<html lang="id">`, landmark `header`/`nav`/`main`/`footer`, tombol ikon punya `aria-label`, cincin fokus `outline: 2px solid var(--utama); outline-offset: 2px`, wilayah pembaruan memakai `aria-live`, dan peta selalu punya padanan daftar.
- Semua teks dari sumber eksternal melewati `esc()` sebelum dimasukkan ke `innerHTML`.
- **Keadaan:**
  - sedang memuat: skeleton seukuran kartu;
  - data kosong: `.keadaan--kosong` dengan alasannya;
  - galat: `.keadaan--galat` dengan tombol "Coba lagi";
  - basi: kartu tetap tampil dengan titik merah dan teks "Data 2 hari lalu";
  - luring: spanduk dan salinan dari localStorage.
- Tema: skrip sebaris kecil di `<head>` membaca `localStorage.tema` atau `?tema=` sebelum render, untuk mencegah kedipan.

### 7.7 Inspirasi
- **GOV.UK Design System:** keyakinan tinggi bahwa ini ada. Ambil bahasanya yang lugas dan pola keadaan error yang jelas.
- **Our World in Data:** keyakinan tinggi. Ambil pola grafik yang selalu punya padanan tabel dan sumber di bawahnya.
- **Panel Harga Badan Pangan:** keyakinan tinggi. Jadikan acuan istilah komoditas dan satuan.
- **Aplikasi Info BMKG:** keyakinan tinggi bahwa ini ada. Ambil istilah cuaca agar warga familier.

---

## 8. Rencana eksekusi tahap demi tahap

### 8.0 Cara memakai
- Satu tahap dijalankan dalam satu sesi Sonnet baru. Tempel **Blok Umum** lalu prompt tahap.
- Sebelum menjalankan tahap, pemilik memastikan prasyaratnya sudah ada dan mengisi bagian `[ISI: ...]`.
- T1 bisa berjalan paralel dengan T2 dan T3 setelah T0 selesai.
- Berkas hasil di bawah `hasil/situs/` ditulis relatif ke folder itu kecuali disebut lain (`skrip/`, `referensi/`, `data/` di akar repo).
- **Status tahap (2026-11-16):** T0 selesai. T1 selesai (lihat Catatan revisi). T2A dan T2B belum. T3 dan seterusnya belum.
- Setiap akhir tahap, eksekutor memperbarui memori Serena `dasbor_sukoharjo/core`; pemilik memperbarui baris status ini dan Catatan revisi bila keputusan berubah.

### 8.0.1 BLOK UMUM (tempel di awal setiap prompt tahap)
```
=== BLOK UMUM ===
Kamu eksekutor proyek "dasbor_sukoharjo": dashboard statis untuk warga Kabupaten Sukoharjo
(12 kecamatan, slug: weru, bulu, tawangsari, sukoharjo, nguter, bendosari, polokarto, mojolaban,
grogol, baki, gatak, kartasura). Situs = HTML/CSS/JS biasa (ES modules, tanpa build, tanpa npm)
di hasil/situs/. Data = JSON dibuat skrip Python stdlib di skrip/. Sumber yang terjangkau dari
GitHub Actions diperbarui di sana; harga (Panel Harga Bapanas) diambil dari PC pemilik lewat
tugas terjadwal DasborHarga (skrip/jadwal_harga.ps1) dan didorong ke main. Situs dideploy ke
GitHub Pages. Bukan situs resmi pemerintah.
Folder kerja: c:\Users\Admin\Documents\proyek_kiro\dasbor_sukoharjo (repo git sendiri).
Rencana induk: referensi/rencana_dasbor.md. Baca HANYA bagian yang disebut prompt: cari nomor
baris judulnya dengan Select-String (keluaran dipotong), lalu read_file dengan offset/limit.

ATURAN
1. PowerShell 5.1. Perintah > 300 karakter diblokir. Logika panjang ditulis ke berkas
   ($env:TEMP\<nama>.ps1/.py untuk sekali pakai, _tmp/ untuk sementara proyek), dijalankan,
   keluarannya ditulis ke .txt, lalu baca .txt itu. Parameter cwd tool shell diabaikan: pakai
   path absolut. Bila keluaran kosong tanpa gema perintah, ulangi sekali. Skrip berjaringan
   atau berdurasi panjang diberi timeout eksplisit (300000 ms).
2. Potong semua keluaran: maksimal 40 baris (| Select-Object -First 40). Skrip Python mencetak
   ringkasan (jumlah, kunci, 3 contoh), bukan isi data.
3. Jangan baca berkas > 20 KB utuh. Jangan baca ulang berkas yang sudah dibaca di sesi ini
   kecuali berubah. Jangan menjelajah folder lain di workspace. Berkas *.log diblokir
   kiroignore: jangan dibaca dan jangan dibypass; baca status dari status.json.
4. Mulai sesi: baca memori Serena "dasbor_sukoharjo/core" (berkas
   .serena\memories\dasbor_sukoharjo\core.md). Untuk tahap UI, baca juga
   referensi/komponen.md bila sudah ada. Pakai simbol Serena untuk melihat fungsi sebelum membaca berkas utuh.
5. Nama berkas snake_case Indonesia. Skrip = kata kerja + objek. Teks UI dan komentar dalam
   bahasa Indonesia.
6. Python hanya stdlib. Zona waktu: timezone(timedelta(hours=7)), jangan zoneinfo. Tulis berkas
   dengan encoding="utf-8" (tanpa BOM). Jangan menulis JSON atau kode lewat Set-Content/Out-File;
   pakai fs_write.
7. Front-end hanya boleh memakai pustaka di hasil/situs/vendor/. Jangan menambah dependensi.
   Semua teks dari data eksternal lewat esc() sebelum masuk innerHTML.
8. Jangan mengarang URL, endpoint, atau nama bidang API. Pakai hanya yang disebut prompt atau
   rencana. Bila bidang API berbeda dari dugaan, ikuti respons asli dan catat di laporan.
9. Git: commit per langkah selesai: git add -A; git commit -m "tN: <ringkas>". Push hanya bila
   prompt menyuruh, dan sebelum push selalu git pull --rebase origin main (remote bisa berisi
   commit bot dan tugas PC). Dilarang force push, reset --hard, atau menghapus berkas pemilik.
10. PENGHITUNG: hitung setiap panggilan tool. Tulis [alat n/BATAS] di awal setiap pesanmu.
    Pada 80% BATAS: berhenti menambah fitur, commit keadaan stabil, tulis laporan.
    Pada BATAS: berhenti total.
11. Berhenti dan lapor bila: error yang sama muncul lagi setelah 2 kali perbaikan; sumber jaringan
    gagal 2 kali (catat lalu lanjut tanpa sumber itu); butuh keputusan pemilik; tugas
    membutuhkan sesuatu yang tidak tertulis di prompt.
12. Pemeriksaan visual: paling banyak 2 putaran tangkapan layar dan perbaikan per tahap.
    PNG dilihat dengan read_file.
13. Akhir sesi: perbarui memori Serena "dasbor_sukoharjo/core" (≤ 20 baris: tahap, status,
    berkas kunci, keputusan, masalah terbuka). Laporan akhir berisi: selesai/belum, keluaran
    cek kriteria selesai, berkas yang berubah, jumlah alat terpakai, hal yang perlu diputuskan
    pemilik.
14. Fakta T0-T1: (a) skrip/umum.py menyediakan ambil_json, amplop, tulis_json, baca_json,
    catat_status: pakai, jangan tulis ulang; (b) hasil/situs/data/status.json di-ignore git:
    jangan di-add; (c) Bapanas dan Overpass jangan diasumsikan terjangkau dari Actions;
    (d) hasil/situs/data/harga.json dan harga_riwayat.json adalah data asli yang ditulis tugas
    terjadwal: jangan diubah, ditimpa, atau dihapus; jangan menyentuh skrip/ambil_harga.py,
    skrip/jadwal_harga.ps1, atau tugas DasborHarga; (e) Python 3.12 dan Edge ada di
    C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe.
=== AKHIR BLOK UMUM ===
```

---

### Tahap 0: Fondasi repo dan uji jangkauan jaringan
- **Tujuan:** repo publik siap. `umum.py` jadi. Ada bukti sumber mana saja yang bisa dijangkau dari PC lokal dan dari runner GitHub Actions.
- **Hasil yang bisa diperiksa:** `referensi/uji_jaringan_lokal.txt` dan `referensi/uji_jaringan_actions.txt`, tabel status di README.
- **Prasyarat pemilik:**
  1. Simpan dokumen ini sebagai `referensi/rencana_dasbor.md`.
  2. Putuskan K1 (repo bersarang terpisah).
  3. Buat repo publik kosong di GitHub dan berikan URL remote-nya.
  4. Pastikan `git push` dari PC sudah terautentikasi.
- **Langkah:**
  1. Periksa `git rev-parse --show-toplevel` di folder proyek. Bila puncaknya adalah workspace dan K1 = "repo bersarang": `git init` di `dasbor_sukoharjo`, tambahkan `dasbor_sukoharjo/` ke `.gitignore` workspace, lalu commit di repo workspace.
  2. Buat folder sesuai 6.3 (yang kosong diberi `.gitkeep`). Isi `.gitignore` sesuai 6.3 dan 6.5.
  3. Tulis `skrip/umum.py`:
     - `ambil_json(url, params=None, metode="GET", data=None, header=None)` dengan coba ulang dan jeda;
     - `ambil_teks(...)`;
     - `amplop(modul, data, sumber, status, catatan)`;
     - `tulis_json(path, obj)` (atomik, ringkas);
     - `baca_json(path, bawaan)`;
     - `sekarang_wib()`;
     - `ambil_versi_live(nama)` (memakai env `SITUS_URL`);
     - `catat_status(modul, status, pesan, ambang)`.
  4. Tulis `skrip/uji_umum.py` (unittest) untuk `amplop`, `tulis_json`, dan `sekarang_wib`.
  5. Tulis `skrip/uji_jaringan.py`. Untuk tiap URL catat kode HTTP, waktu (ms), ukuran (byte), dan 100 karakter pertama:
     - BMKG prakiraan `adm4=33.11.01.2001`;
     - BMKG `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json`;
     - Open-Meteo forecast dan air-quality dengan lat -7.68, lon 110.84 (perkiraan pusat kabupaten [D]) dan `hourly=temperature_2m`, `hourly=pm2_5`;
     - Overpass POST kueri `[out:json];node(1);out;`;
     - Panel Harga `https://api-panelhargav2.badanpangan.go.id/api/front/harga-peta-provinsi` (tanpa parameter);
     - PIHPS `https://www.bi.go.id/hargapangan` [D];
     - Wikipedia `https://id.wikipedia.org/api/rest_v1/page/summary/Kabupaten_Sukoharjo` [D].
     
     Argumen `--keluaran <path>`.
  6. Jalankan lokal dan simpan hasilnya ke `referensi/uji_jaringan_lokal.txt`.
  7. Tulis `.github/workflows/uji_jaringan.yml`:
     - pemicu `push` dengan `paths: [skrip/uji_jaringan.py, .github/workflows/uji_jaringan.yml]` dan `workflow_dispatch`;
     - `permissions: contents: write`;
     - jalankan `python3 skrip/uji_jaringan.py --keluaran referensi/uji_jaringan_actions.txt`;
     - commit dan push hasilnya.
  8. `git remote add origin <URL>`, push `main`. Tunggu sekitar 3 menit (`Start-Sleep 180`), `git pull`, lalu baca hasilnya.
  9. Tulis tabel perbandingan lokal vs Actions ke README bagian "Status sumber". Commit dan push.
- **Kriteria selesai:**
  - `python skrip/uji_umum.py` lulus;
  - kedua berkas uji ada dan masing-masing berisi ≥ 7 baris;
  - README memuat tabel status.
- **Anggaran:** 6 kredit, BATAS 30 alat.
- **Titik berhenti:**
  - Workflow belum menghasilkan berkas setelah 2 kali menunggu: berhenti dan minta pemilik memeriksa tab Actions.
  - BMKG gagal dari Actions tetapi berhasil lokal: berhenti dan laporkan. Pemilik memilih Rencana Jaringan B (bagian 10).
- **Jangan:** membuat UI, skrip modul data, atau mengaktifkan Pages.

**Prompt T0:**
```
[BLOK UMUM]
TAHAP 0: Fondasi repo dan uji jangkauan jaringan. BATAS = 30 alat.
Masukan pemilik: K1 = [ISI: repo bersarang terpisah / lainnya]; URL remote = [ISI].
Kerjakan langkah T0 di referensi/rencana_dasbor.md bagian "Tahap 0" (baca bagian itu saja,
ditambah 6.3 untuk struktur folder dan 6.6 untuk perilaku umum.py).
URL yang boleh diuji hanya yang tertulis di langkah 5 Tahap 0.
Kriteria selesai: uji_umum.py lulus; referensi/uji_jaringan_lokal.txt dan
referensi/uji_jaringan_actions.txt ada (≥ 7 baris); tabel "Status sumber" ada di README.
Berhenti bila workflow tidak menghasilkan berkas setelah 2 kali menunggu, atau BMKG diblokir
dari Actions. Jangan membuat UI atau mengaktifkan Pages.
```

---

### Tahap 1: Spike harga pangan (berbatas)
- **Tujuan:** keputusan jalur harga A, B, C, atau D beserta bukti.
- **Hasil:** `referensi/keputusan_harga.md`, `data/peta_komoditas.csv` (bila A/B), `_tmp/contoh_harga.json`, `skrip/uji_harga.py`.
- **Prasyarat:** T0 selesai. Tangkapan DevTools pemilik sesuai 5.4 sudah ada di `referensi/harga/`.
- **Langkah:**
  1. Buat daftar berkas di `referensi/harga/` beserta ukurannya. Baca baris pertama tiap berkas cURL (catatan autentikasi). Ringkas tiap respons JSON lewat skrip (kunci tingkat atas, jumlah elemen, 2 contoh). Jangan membuka berkas utuh.
  2. Tulis `skrip/uji_harga.py` yang meniru permintaan dari tangkapan:
     - URL, metode, dan parameter disalin dari cURL, tanpa Cookie atau Authorization;
     - ubah parameter wilayah ke Sukoharjo dan komoditas ke 2 ID yang terlihat di respons;
     - maksimal 2 percobaan per kandidat.
  3. Untuk kandidat yang berhasil:
     - normalisasi ke skema 6.4.7 dan simpan ke `_tmp/contoh_harga.json`;
     - cek apakah ada riwayat (rentang tanggal);
     - jalankan sekali dari Actions dengan menambah langkah sementara di `uji_jaringan.yml`, lalu hapus langkah itu setelah hasilnya didapat.
  4. Tulis `referensi/keputusan_harga.md` berisi:
     - matriks kandidat (cakupan, jumlah komoditas, riwayat, autentikasi, ToS menurut tangkapan pemilik, terjangkau dari Actions);
     - jalur terpilih dan alasannya;
     - daftar komoditas dan `id_sumber`.
  5. Bila memilih A/B, isi `data/peta_komoditas.csv` (`id,nama,kategori,satuan,id_sumber,sumber`).
- **Kriteria selesai:** `keputusan_harga.md` ada dan memuat matriks serta keputusan. Bila A/B: `_tmp/contoh_harga.json` lolos pemeriksaan skrip (≥ 8 komoditas, harga > 0).
- **Anggaran:** 6 kredit, BATAS 30 alat.
- **Titik berhenti:**
  - Tidak ada tangkapan pemilik: berhenti segera.
  - Semua kandidat butuh autentikasi atau gagal: tulis keputusan "C" (atau "B" bila provinsi berhasil) lalu berhenti.
- **Jangan:** menebak endpoint, mencoba login, melewati captcha atau token, mengambil data lebih dari yang perlu untuk uji, atau membuat UI.
- **Hasil aktual (selesai 2026-11-16):**
  - Keputusan: jalur A1 level Konsumen (lihat Catatan revisi 1-3). `referensi/keputusan_harga.md` dan `data/peta_komoditas.csv` (24 baris) sudah diperbarui; `_tmp/contoh_harga.json` lolos (24 komoditas, 8/8 inti).
  - Berkas tambahan di luar daftar awal: `skrip/ambil_harga.py`, `skrip/jadwal_harga.ps1`, `hasil/situs/data/harga.json`, `hasil/situs/data/harga_riwayat.json`, tugas `DasborHarga`.
  - Uji Actions: timeout. Langkah sementara di `uji_jaringan.yml` dihapus pemilik sebelum hasilnya terbaca oleh eksekutor.
  - Tangkapan pertama pemilik level Produsen; level Konsumen ditangkap pada putaran kedua (lihat 5.4 butir 3).

**Prompt T1:**
```
[BLOK UMUM]
TAHAP 1: Spike harga pangan. BATAS = 30 alat.
Konteks: rencana bagian 5 (baca 5.1–5.5 saja) dan skema 6.4.7.
Masukan: tangkapan DevTools pemilik di referensi/harga/.
Kerjakan langkah "Tahap 1" di rencana. Aturan khusus: hanya meniru permintaan yang ada di
tangkapan (boleh mengganti nilai parameter wilayah/komoditas dengan nilai yang muncul di respons);
maksimal 2 percobaan per kandidat; tidak boleh memakai Cookie/Authorization, login, atau captcha.
Kandidat yang butuh itu ditandai "tidak dipakai".
Kriteria selesai: referensi/keputusan_harga.md dengan matriks dan jalur terpilih (A/B/C/D);
bila A/B: _tmp/contoh_harga.json valid (≥ 8 komoditas, harga > 0) dan data/peta_komoditas.csv.
Bila tangkapan tidak ada, berhenti dan minta pemilik mengikuti 5.4.
```

---

### Tahap 2: Sistem desain dan kerangka situs
- **Tujuan:** kerangka aplikasi lengkap dengan data contoh, sistem desain final, dan alat cek tampilan.
- **Dipecah dua sesi (revisi 2026-11-16):** T2A = fondasi (vendor, CSS, HTML, JS inti, cek statis); T2B = data contoh, tampilan, alat cek visual, `komponen.md`. Alasan: satu sesi 45 alat terlalu ketat untuk sekitar 25 berkas, dan T1 menunjukkan sebagian alat habis oleh keanehan shell.
- **Jalur berkas:** semua berkas situs berada di `hasil/situs/`. `data/contoh/` berarti `hasil/situs/data/contoh/`. Folder `data/` di akar repo hanya untuk CSV. `hasil/situs/data/harga.json` dan `harga_riwayat.json` adalah data asli dari tugas terjadwal: dilarang diubah. Mode contoh membaca `data/contoh/`, jadi tidak menyentuh berkas asli.
- **Hasil T2A:**
  - `vendor/` (Leaflet 1.9.4, Chart.js 4.x UMD, ikon Lucide) dan `vendor/VERSI.txt`;
  - `ikon/sprite.svg`, `logo.svg`;
  - `index.html`, `gaya.css`;
  - `js/format.js`, `data.js`, `komponen.js`, `grafik.js`, `peta.js`, `utama.js`;
  - `skrip/ambil_vendor.py`, `skrip/cek_situs.py`.
- **Hasil T2B:**
  - `data/contoh/*.json`;
  - `js/tampilan/*.js` (7 tampilan, sebagian kerangka);
  - `skrip/cek_tampilan.ps1`, tangkapan layar di `_tmp/layar/`;
  - `referensi/komponen.md`.
- **Prasyarat:** T0 dan T1 selesai. T2B juga membutuhkan T2A selesai.
- **Langkah T2A:**
  1. `ambil_vendor.py`:
     - unduh Leaflet `https://unpkg.com/leaflet@1.9.4/dist/` (leaflet.js, leaflet.css, images/) [D]. Gambar yang dicoba: layers.png, layers-2x.png, marker-icon.png, marker-icon-2x.png, marker-shadow.png [D]; bila 404, lewati dan catat;
     - unduh berkas UMD Chart.js 4 dari jsDelivr (`https://cdn.jsdelivr.net/npm/chart.js@4/dist/`; nama berkas tepat dicek lewat listing `https://data.jsdelivr.com/v1/packages/npm/chart.js` [D]; kunci ke versi pasti);
     - unduh ikon Lucide dari `https://unpkg.com/lucide-static@<versi>/icons/<nama>.svg` [D]; `<versi>` ditentukan dari listing `https://data.jsdelivr.com/v1/packages/npm/lucide-static`;
     - gabungkan ikon menjadi `sprite.svg`;
     - catat versi dan sha256 di `vendor/VERSI.txt`.
  2. `gaya.css`:
     - urutan: token (7.2, terang dan gelap), reset ringkas, tata letak (7.1), komponen (tabel 7.2), utilitas (≤ 15 kelas), dan reduced-motion;
     - satu berkas, target ≤ 18 KB.
  3. `index.html`:
     - skrip tema sebaris di `<head>`;
     - kepala aplikasi, `<main id="isi">`, nav bawah dan rel desktop, wadah lembar dan toast;
     - footer dengan pernyataan bukan situs resmi;
     - `<script type="module" src="js/utama.js">`.
  4. JS:
     - `format.js`: rupiah, angka, persen, tanggal id-ID, waktu relatif, WIB;
     - `data.js`: `muat(nama)` dengan `cache: "no-cache"`, salinan di localStorage, `kesegaran(amplop, ambang)`, dan mode contoh (`?contoh=1` memuat `data/contoh/`);
     - `komponen.js`: `esc`, `kartu`, `lencanaUbah`, `metaSumber`, `keadaan`, `kerangka`, `spanduk`, `ikon(nama)`;
     - `grafik.js`: `sparkline(nilai, opsi)` dan `muatChart()` (malas);
     - `peta.js`: `muatLeaflet()` (malas);
     - `utama.js`: router hash, status kecamatan (localStorage dan `?kec=`), tema, lembar pemilih kecamatan (daftar dan cari dulu; peta SVG ditambah di T3), dan `document.body.dataset.siap = "1"` setelah render. Parameter (`contoh`, `kec`, `tema`) dibaca dari query di dalam hash. Router memuat `js/tampilan/<nama>.js` lewat import dinamis; modul yang belum ada menampilkan keadaan "Segera hadir", bukan galat.
  5. `skrip/cek_situs.py`:
     - ukuran gzip HTML+CSS+JS awal ≤ 60 KB (Leaflet dan Chart.js dimuat malas, tidak dihitung);
     - semua `import` dan `src` lokal ada;
     - tidak ada URL eksternal di HTML/JS selain host tile OSM dan tautan keluar di data;
     - tidak ada `innerHTML` yang memakai variabel tanpa `esc(`, dan tidak ada kata Inggris umum di string UI. Keduanya heuristik regex; hasilnya peringatan, bukan galat.
- **Langkah T2B:**
  1. `data/contoh/*.json` (amplop `contoh: true`) untuk tiap modul yang dipakai Beranda. Untuk harga, salin struktur `hasil/situs/data/harga.json` asli ke `data/contoh/harga.json`; berkas aslinya tidak diubah.
  2. Tampilan: Beranda dirender lengkap sesuai 7.3 dengan data contoh (lencana CONTOH tampil); enam halaman lain berupa kerangka dengan judul dan `.keadaan--kosong` "Segera hadir".
  3. `cek_tampilan.ps1`:
     - jalankan `python -m http.server 8765 -d hasil/situs` di latar (`Start-Process`, catat PID);
     - Edge headless (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` [T], ada di PC pemilik) dengan `--headless=new --disable-gpu --hide-scrollbars --user-data-dir=$env:TEMP\edge_t2 --virtual-time-budget=4000 --window-size=<w,h> --screenshot=<png> <url>`, simpan ke `_tmp/layar/`;
     - `--dump-dom` ke berkas untuk memeriksa `data-siap="1"` dan menghitung `.kartu`;
     - hentikan server di blok `finally`;
     - cetak ringkasan.
  4. Tangkap layar 3 kondisi: `#/?contoh=1` 390×844 terang, 390×844 `&tema=gelap`, dan 1280×800 terang. Lihat PNG dengan `read_file` dan perbaiki bila perlu (maksimal 2 putaran).
  5. Tulis `referensi/komponen.md` (≤ 80 baris): kelas, fungsi JS beserta parameternya, dan pola menambah tampilan baru.
- **Kriteria selesai T2A:** `python skrip/cek_situs.py` lulus (peringatan boleh); `gaya.css` ≤ 18 KB; `vendor/VERSI.txt` ada; semua berkas hasil T2A ada.
- **Kriteria selesai T2B:**
  - `cek_tampilan.ps1` melaporkan `siap=1` untuk ketiga kondisi;
  - `cek_situs.py` lulus;
  - ketiga PNG ada;
  - tidak ada teks Inggris di UI;
  - `komponen.md` ≤ 80 baris.
- **Anggaran:** T2A BATAS 25 alat, T2B BATAS 35 alat (total 60; perkiraan kredit 4 + 6 [D]).
- **Titik berhenti:**
  - Edge headless tidak bisa menangkap layar: lanjutkan dengan `--dump-dom` saja dan laporkan.
  - Unduhan ikon gagal 2 kali: buat 10 ikon inti secara manual dalam sprite dan laporkan.
- **Jangan:** mengambil data nyata, membuat peta, menambah pustaka, mengubah token warna di luar nilai rencana (kecuali gagal kontras, dengan dicatat), membuat lebih dari 2 putaran revisi visual, membuat service worker, atau menyentuh data dan skrip harga.

**Prompt T2A:**
```
[BLOK UMUM]
TAHAP 2A: Fondasi situs (vendor, CSS, HTML, JS inti, cek statis). BATAS = 25 alat.
Prasyarat: T0 dan T1 selesai. Semua jalur situs relatif ke hasil/situs/ kecuali skrip/.
Baca saja: rencana 6.3, 7.1 dan 7.2, 7.6 (cari judulnya dengan Select-String), lalu bagian
"Tahap 2" di bagian 8: hanya "Langkah T2A" dan "Kriteria selesai T2A".
Kerjakan langkah T2A 1-5, commit per butir (vendor, css, html, js, cek_situs).
Nilai token di 7.2 wajib dipakai apa adanya. Jangan membuat tampilan lengkap, data contoh,
peta SVG, atau service worker; jangan menyentuh data dan skrip harga.
Kriteria selesai: python skrip/cek_situs.py lulus; gaya.css <= 18 KB; vendor/VERSI.txt ada.
Push: tidak.
```

**Prompt T2B:**
```
[BLOK UMUM]
TAHAP 2B: Tampilan, data contoh, alat cek visual, komponen.md. BATAS = 35 alat.
Prasyarat: T2A selesai (cek memori core). Semua jalur situs relatif ke hasil/situs/.
Baca saja: referensi/komponen.md bila ada, rencana 7.3-7.5, skema 6.4.1-6.4.8 dan subbagian
6.4.x yang dipakai Beranda menurut 7.3, lalu bagian "Tahap 2" di bagian 8: hanya
"Langkah T2B" dan "Kriteria selesai T2B".
Kerjakan langkah T2B 1-5, commit per butir (data contoh, tampilan, cek_tampilan, perbaikan
visual, komponen.md). Revisi visual maksimal 2 putaran.
Kriteria selesai: cek_tampilan.ps1 melaporkan siap=1 untuk #/?contoh=1 pada 390x844 terang,
390x844 gelap, dan 1280x800 terang; python skrip/cek_situs.py lulus; ketiga PNG ada;
komponen.md <= 80 baris.
Setelah semua kriteria lulus: git pull --rebase origin main, lalu git push origin main.
```
---

### Tahap 3: Wilayah, kode, batas, dan peta SVG
- **Tujuan:** `data/kecamatan.csv` (dengan `adm4_acuan`), `desa.json`, `kecamatan.json`, `batas_kecamatan.geojson`, dan `peta/peta_kecamatan.svg` yang dipakai pemilih kecamatan dan halaman Wilayah.
- **Prasyarat:** T2 selesai.
- **Langkah:**
  1. `ambil_kode_wilayah.py`:
     - unduh berkas kode wilayah Kemendagri dari repo publik `cahyadsn/wilayah` di GitHub [D: periksa dulu dengan API `https://api.github.com/repos/cahyadsn/wilayah/contents/db`; pilih berkas SQL/CSV wilayah terbaru] ke `data/mentah/`;
     - saring kode yang berawalan `33.11.`;
     - hasilkan `data/mentah/wilayah_3311.csv`;
     - cetak jumlah per kecamatan;
     - sumber cadangan: pemilik menyediakan daftar.
  2. `bangun_wilayah.py`:
     - cocokkan nama dan kode kecamatan dengan tabel 4.1, dan laporkan perbedaannya;
     - pilih `adm4_acuan` per kecamatan: desa/kelurahan yang namanya sama dengan nama kecamatan, bila tidak ada pilih kode pertama;
     - Weru wajib `33.11.01.2001` (sudah [T]);
     - tulis `data/kecamatan.csv` dan `hasil/situs/data/desa.json`.
  3. Uji 12 `adm4_acuan` ke BMKG (1 permintaan per kecamatan, jeda 1,5 detik). Simpan `lat`/`lon` dari respons bila ada [D]. Simpan satu respons utuh ke `referensi/contoh_bmkg.json`.
  4. `ambil_batas.py`:
     - kueri Overpass: area relasi `boundary=administrative` + `name~"Sukoharjo"` + `admin_level=5` [D], lalu relasi `admin_level=6` di dalamnya [D] dengan `out geom`;
     - rakit way menjadi ring (penyambungan ujung ke ujung);
     - sederhanakan dengan Douglas–Peucker (0,0004°), bulatkan 4 desimal;
     - petakan nama ke slug;
     - tulis GeoJSON (≤ 60 KB);
     - cetak jumlah poligon valid (ring tertutup, ≥ 4 titik).
  5. Hitung tetangga: dua kecamatan bertetangga bila ada ≥ 2 titik berjarak < 0,0008°. Tulis `kecamatan.json` (6.4.9) dengan centroid dari poligon atau dari lat/lon BMKG.
  6. `bangun_peta_svg.py`:
     - proyeksi equirectangular dengan skala x = cos(lat0);
     - `viewBox="0 0 400 H"`, satu `<path data-slug>` per kecamatan, dan `<text>` label di centroid;
     - kelas CSS sesuai 7.2 (gaya peta), tanpa warna inline.
  7. UI:
     - lembar pemilih memuat SVG (fetch teks, sisipkan, ketuk path memilih kecamatan);
     - "Gunakan lokasi saya" dengan point-in-polygon (ray casting) di `js/peta.js`;
     - halaman `#/wilayah` menampilkan peta dan daftar 12 kecamatan (profil menyusul di T8).
  8. Tangkap layar `#/wilayah` 390×844 (1 putaran).
- **Kriteria selesai:**
  - `kecamatan.csv` berisi 12 baris dengan `adm4_acuan` yang masing-masing mendapat HTTP 200 dari BMKG;
  - GeoJSON memuat 12 poligon valid, atau cadangan aktif;
  - SVG memuat 12 path;
  - `cek_tampilan` melaporkan `siap=1`.
- **Anggaran:** 7 kredit, BATAS 35 alat.
- **Titik berhenti:**
  - Penyusunan poligon gagal untuk lebih dari 2 kecamatan setelah 1 perbaikan: berhenti merakit. Pakai **cadangan peta skematik**: 12 heksagon di posisi relatif centroid (dari lat/lon BMKG), dibuat oleh `bangun_peta_svg.py --skematik`, dan "lokasi saya" memilih centroid terdekat. Laporkan.
  - Kode wilayah tidak bisa diunduh: minta daftar dari pemilik.
- **Jangan:** mengambil fasilitas, menulis profil, atau memakai GADM (lisensinya membatasi redistribusi [D]).

**Prompt T3:**
```
[BLOK UMUM]
TAHAP 3: Wilayah, kode, batas, peta SVG. BATAS = 35 alat.
Baca rencana bagian 4.1, 6.4.9, 6.4.11, 6.4.17, 7.2 (gaya peta), 7.5, dan "Tahap 3".
Kerjakan langkah Tahap 3 berurutan. Satu percobaan + satu perbaikan untuk perakitan poligon;
bila tetap gagal untuk > 2 kecamatan, pakai cadangan peta skematik sesuai rencana.
Kriteria selesai: 12 adm4_acuan → HTTP 200 dari BMKG; referensi/contoh_bmkg.json tersimpan;
12 poligon valid (atau mode skematik); peta_kecamatan.svg berisi 12 path; pemilih kecamatan dan
"lokasi saya" berfungsi; cek_tampilan siap=1.
```

---

### Tahap 4: Cuaca BMKG, pipeline, deploy (Rilis 0.1)
- **Tujuan:** situs live dengan cuaca nyata 12 kecamatan, nomor darurat nasional terverifikasi, dan status data, diperbarui otomatis tiap 3 jam.
- **Prasyarat pemilik:**
  - Settings → Pages → Source: **GitHub Actions**.
  - Settings → Secrets and variables → Actions → Variables: `SITUS_URL` = `https://<user>.github.io/<repo>`.
  - Isi `data/kontak_darurat.csv` (kolom 6.4.13) hanya dengan nomor yang sudah dicek di situs resmi (kandidat: 112, 110, 113, 119, 115 [D]), dengan URL sumber dan tanggal verifikasi.
- **Langkah:**
  1. Ringkas `referensi/contoh_bmkg.json` lewat skrip (struktur kunci dan 1 slot). Bandingkan dengan dugaan di 6.4.3. Perbarui bagian 6.4.3 di rencana bila berbeda.
  2. `ambil_cuaca.py`:
     - loop 12 kecamatan dengan jeda 1,5 detik;
     - normalisasi ke 6.4.3 (waktu lokal ISO +07:00, angin dalam km/jam bila sumbernya m/s dikali 3,6, sesuai satuan sebenarnya);
     - gabungkan dengan versi lama untuk kecamatan yang gagal;
     - cek kewajaran;
     - tulis amplop dan `catat_status`.
  3. `bangun_layanan.py` versi awal: dari `kontak_darurat.csv` hasilkan `layanan.json` bagian `darurat` saja (baris tanpa tanggal verifikasi dibuang).
  4. `jalankan_semua.py`:
     - argumen `--modul` (daftar) atau `--pemicu`/`--jadwal` (pemetaan cron ke modul sesuai 6.5);
     - registri modul berupa dict nama → fungsi, sehingga modul baru cukup ditambahkan di satu tempat;
     - menulis `status.json`.
  5. `cek_data.py`:
     - validator skema minimal per berkas (bidang wajib dan tipe), dibuat sebagai dict aturan, bukan pustaka;
     - rentang nilai dan kesegaran;
     - `--mode ci`: exit 1 hanya bila ada JSON rusak atau bidang wajib hilang;
     - `--mode laporan`: cetak tabel.
  6. UI:
     - kartu hero cuaca Beranda memakai data nyata;
     - halaman `#/cuaca` (segmen Hari ini/3 hari, strip jam, tabel 12 kecamatan, grafik suhu SVG);
     - kartu darurat dengan `tel:`;
     - halaman `#/status`;
     - halaman `#/tentang` (pernyataan, sumber BMKG, lisensi);
     - modul yang belum ada menampilkan `.keadaan--kosong`.
  7. `.github/workflows/perbarui_dan_terbitkan.yml` sesuai kerangka 6.5. Hapus `uji_jaringan.yml`.
  8. Jalankan lokal: `jalankan_semua.py --modul cuaca`, `cek_data.py --mode laporan`, dan `cek_tampilan` untuk `#/` dan `#/cuaca`.
  9. Push. Tunggu, lalu periksa situs live dengan `Invoke-WebRequest $SITUS_URL/data/status.json` (keluaran dipotong).
  10. Buat tag `dasbor_sukoharjo-v0.1` dan push tag.
- **Kriteria selesai:**
  - `cek_data` melaporkan cuaca `ok` atau `sebagian` dengan ≥ 11/12 kecamatan;
  - URL live mengembalikan `status.json` dengan `dibangun` < 1 jam;
  - halaman live menampilkan cuaca (lewat `--dump-dom` URL live: `siap=1`, ada `.kartu--hero`);
  - tag ada.
- **Anggaran:** 10 kredit, BATAS 45 alat.
- **Titik berhenti:**
  - Deploy gagal 3 kali: berhenti, laporkan log galat (20 baris terakhir yang disalin pemilik dari tab Actions).
  - BMKG membalas 429: naikkan jeda ke 3 detik sekali, lalu lapor bila masih gagal.
- **Jangan:** menambah modul selain cuaca dan darurat, membuat service worker, atau mengubah sistem desain.

**Prompt T4:**
```
[BLOK UMUM]
TAHAP 4: Cuaca BMKG, pipeline Actions, deploy → Rilis 0.1. BATAS = 45 alat.
Baca rencana 6.4.1–6.4.3, 6.4.13, 6.5–6.7, 7.3, 7.4 (Cuaca, Status, Tentang), referensi/komponen.md,
dan "Tahap 4". SITUS_URL = [ISI]. Pemilik sudah mengaktifkan Pages (Source: GitHub Actions),
membuat variabel SITUS_URL, dan mengisi data/kontak_darurat.csv.
Kerjakan langkah Tahap 4. Bidang BMKG mengikuti referensi/contoh_bmkg.json, bukan dugaan.
Kriteria selesai: cek_data → cuaca ≥ 11/12; status.json live dibangun < 1 jam; dump-dom live siap=1;
tag dasbor_sukoharjo-v0.1 terdorong. Deploy gagal 3 kali → berhenti dan laporkan.
```

---

### Tahap 5: Harga pangan (Rilis 0.2)
- **Tujuan:** modul harga berjalan sesuai `referensi/keputusan_harga.md`.
- **Prasyarat:**
  - T1 dan T4 selesai.
  - Bila jalur C atau B+C, pemilik mengisi minimal 2 pekan data di `data/harga_manual.csv` (`tanggal,pasar,komoditas_id,harga,satuan,sumber,pencatat`).
  - Opsional: `data/acuan_harga.csv` (HET/HAP dari regulasi resmi, dengan URL).
- **Langkah:**
  1. Jalur A/B: `ambil_harga.py` berdasarkan `uji_harga.py`.
     - Bila sumber menyediakan rentang tanggal, isi ulang riwayat 90 hari satu kali (`--isi-ulang`).
     - Selanjutnya ambil harian dan tambahkan ke `harga_riwayat.json` (maks 400 hari, tanggal unik).
     - Isi `tingkat` dan `label_peringatan` sesuai bagian 5.2.
  2. Jalur C: `bangun_harga_manual.py` memvalidasi CSV (komoditas dikenal, harga > 0, tanggal valid, tanpa duplikat), menghitung rata-rata antarpasar per tanggal, lalu menghasilkan `harga.json` dan `harga_riwayat.json` dengan `tingkat: "manual"`. Sediakan `data/harga_manual_templat.csv` beserta petunjuk singkat di README.
  3. Jalur B+C: `harga.json` memakai B. `harga_manual.json` terpisah dan ditampilkan sebagai kartu "Cek lokal pekan ini".
  4. Hitung `ubah_persen`, `rata_7h`, dan `ubah_7h_persen` dalam fungsi murni. Tambahkan unit test-nya di `uji_umum.py`.
  5. Daftarkan modul di `jalankan_semua.py` (jadwal harga). Tambahkan aturan harga ke `cek_data.py`.
  6. UI:
     - kartu harga Beranda;
     - halaman `#/harga` (segmen, urutkan, cari, sparkline);
     - detail `#/harga/<id>` dengan Chart.js dimuat malas (30/90/365), statistik periode, tabel, dan acuan bila ada;
     - spanduk label cakupan wajib tampil bila `tingkat` bukan `kabupaten`.
  7. `cek_tampilan` untuk `#/harga` dan satu detail (terang, 1 putaran). Push, verifikasi live, lalu tag `v0.2`.
- **Kriteria selesai:**
  - `cek_data` melaporkan harga `ok` dengan ≥ 8 komoditas;
  - riwayat ≥ 2 titik per komoditas;
  - unit test lulus;
  - spanduk cakupan tampil sesuai tingkat (diperiksa lewat dump-dom);
  - situs live diperbarui.
- **Anggaran:** 8 kredit, BATAS 40 alat.
- **Titik berhenti:**
  - Sumber A/B yang lolos di T1 sekarang gagal 2 kali: alihkan ke C, lalu laporkan.
  - Chart.js gagal dimuat 2 kali: tampilkan tabel saja, lalu laporkan.
- **Jangan:** mencari sumber harga baru (itu tugas T1) atau membuat grafik di Beranda selain sparkline.

**Prompt T5:**
```
[BLOK UMUM]
TAHAP 5: Harga pangan → Rilis 0.2. BATAS = 40 alat.
Baca referensi/keputusan_harga.md, rencana 5.2–5.3, 6.4.7–6.4.8, 7.4 (Harga), referensi/komponen.md,
dan "Tahap 5". Jalur terpilih = [ISI: A/B/C/B+C].
Kerjakan langkah sesuai jalur. Dilarang mencari sumber baru; bila sumber gagal 2 kali, alihkan ke C.
Kriteria selesai: cek_data harga ok ≥ 8 komoditas; riwayat ≥ 2 titik; unit test lulus; spanduk
cakupan tampil bila tingkat ≠ kabupaten; situs live diperbarui; tag dasbor_sukoharjo-v0.2.
```

---

### Tahap 6: Modul harian ringan (Rilis 0.3)
- **Tujuan:** jadwal sholat, kalender (pasaran, Hijriah, libur), gempa, udara dan UV, serta hujan 7 hari.
- **Prasyarat pemilik:**
  - Salin jadwal sholat Kemenag untuk Kab. Sukoharjo pada 3 tanggal berbeda (misalnya awal bulan ini, 3 bulan lagi, dan 6 bulan lagi) ke `referensi/jadwal_kemenag_contoh.csv`.
  - Isi `data/libur_<tahun>.csv` dari SKB 3 Menteri beserta URL-nya.
  - Sebutkan 2 tanggal beserta pasarannya dari kalender Jawa cetak atau daring tepercaya ke `referensi/pasaran_contoh.csv`.
- **Langkah:**
  1. `hitung_sholat.py`:
     - algoritma posisi matahari standar (deklinasi, persamaan waktu);
     - parameter Subuh −20°, Isya −18°, Asar bayangan 1×, terbit/terbenam −0,833°, ihtiyat +2 menit (terbit −2 menit), imsak = subuh − 10 menit;
     - koordinat pusat kabupaten dari `kecamatan.json` (centroid Kec. Sukoharjo);
     - setahun penuh ke `sholat_<tahun>.json`;
     - bandingkan dengan `jadwal_kemenag_contoh.csv`, toleransi ±2 menit;
     - hitung juga selisih untuk centroid paling barat dan paling timur. Bila > 1 menit, tambahkan `koreksi_menit` per kecamatan.
  2. `bangun_libur.py`: dari CSV ke `libur.json`.
  3. `js/kalender.js`:
     - `pasaran(tanggal)` dari jangkar di `pasaran_contoh.csv` (cek kedua tanggal cocok, tulis jangkarnya di komentar);
     - `hijriah(tanggal)` via `Intl.DateTimeFormat("id-ID-u-ca-islamic-umalqura")` dengan label "perkiraan";
     - `liburBerikut()`.
  4. `ambil_gempa.py`: `autogempa.json` dan `gempadirasakan.json` [D]. Ringkas struktur respons dulu (struktur diduga `Infogempa.gempa` [D]). Hitung jarak haversine dari centroid kabupaten dan `relevan_24jam` (6.4.6).
  5. `ambil_udara.py`: Open-Meteo air-quality, 1 titik, `hourly=pm2_5,pm10,us_aqi,uv_index`, `timezone=Asia/Jakarta`, `forecast_days=2` [D: nama parameter dicek pada respons pertama]. Hasilnya 24 jam ke depan beserta kategori.
  6. `ambil_hujan.py`: Open-Meteo forecast dengan 12 koordinat sekaligus (latitude dan longitude dipisah koma [D]; bila tidak didukung, loop dengan jeda 1 detik), `daily=precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min`, `forecast_days=7`.
  7. Spike peringatan dini BMKG: maksimal 4 alat. Hanya cari tautan resmi dari halaman `https://www.bmkg.go.id` [D] yang menyebut peringatan dini atau CAP. Bila ada format terstruktur, catat di README "Peluang" dan **jangan diimplementasikan**.
  8. Daftarkan semua modul di `jalankan_semua.py` dan `cek_data.py`.
  9. UI:
     - kartu sholat dan Hari ini di Beranda;
     - kartu hujan 7 hari dan udara;
     - spanduk gempa dan hujan lebat sesuai prioritas 7.3;
     - segmen "Hujan 7 hari" di `#/cuaca`;
     - halaman `#/kalender` berisi jadwal sholat sebulan dan libur setahun, dibuka dari kartu.
  10. Atribusi Open-Meteo (CC BY 4.0 [D]) di kartu dan halaman Tentang.
  11. Jalankan `cek_tampilan` untuk `#/` (terang dan gelap). Push, verifikasi live, tag `v0.3`.
- **Kriteria selesai:**
  - selisih sholat dengan Kemenag ≤ 2 menit di ketiga tanggal (keluaran skrip ditempel di laporan);
  - pasaran cocok dengan 2 tanggal contoh;
  - `cek_data` melaporkan gempa, udara, dan hujan `ok`;
  - Beranda menampilkan semua kartu baru (diperiksa lewat dump-dom dengan menghitung `.kartu` ≥ 8).
- **Anggaran:** 10 kredit, BATAS 50 alat.
- **Titik berhenti:**
  - Selisih sholat > 2 menit setelah 1 perbaikan: laporkan tabel selisih, jangan dirilis.
  - Respons gempa atau Open-Meteo tidak sesuai dugaan: ikuti respons asli, maksimal 2 percobaan per modul.
- **Jangan:** mengimplementasikan peringatan dini, memakai API jadwal sholat pihak ketiga, atau menulis kalender Jawa lengkap (wuku dan lainnya).

**Prompt T6:**
```
[BLOK UMUM]
TAHAP 6: Sholat, kalender, gempa, udara, hujan 7 hari → Rilis 0.3. BATAS = 50 alat.
Baca rencana 2.2–2.3, 6.4.4–6.4.6, 6.4.14–6.4.15, 6.7 (ambang), 7.3, referensi/komponen.md,
dan "Tahap 6". Masukan pemilik: referensi/jadwal_kemenag_contoh.csv, referensi/pasaran_contoh.csv,
data/libur_[ISI tahun].csv.
Kerjakan langkah Tahap 6. Spike peringatan dini maksimal 4 alat dan tidak diimplementasikan.
Kriteria selesai: selisih sholat ≤ 2 menit di 3 tanggal; pasaran cocok 2 tanggal; cek_data gempa/
udara/hujan ok; Beranda ≥ 8 kartu (dump-dom); live diperbarui; tag dasbor_sukoharjo-v0.3.
```

---

### Tahap 7: Fasilitas, layanan, transportasi, info rutin, peta Leaflet (Rilis 0.4)
- **Tujuan:** tab Layanan lengkap dengan peta dan "terdekat dari saya".
- **Prasyarat pemilik:** isi `data/layanan_publik.csv`, `data/transportasi.csv`, dan `data/info_rutin.csv` (BBM, LPG 3 kg, UMK) dari situs resmi, dengan URL dan tanggal verifikasi. Minimal: Disdukcapil, Samsat, MPP bila ada, 12 kantor kecamatan (alamat), RSUD, KRL, dan BST.
- **Langkah:**
  1. `ambil_fasilitas.py`:
     - satu kueri Overpass untuk area kabupaten dengan tag `amenity` = hospital, clinic, doctors, pharmacy, school, college, university, marketplace, townhall, police, fire_station, post_office; `railway=station`; `amenity=bus_station` [D];
     - `out center`;
     - pemetaan ke `jenis` (6.4.12);
     - kecamatan ditentukan lewat point-in-polygon (atau centroid terdekat pada mode skematik);
     - entri tanpa nama tetap disimpan dengan label jenis;
     - cetak jumlah per jenis dan kecamatan.
  2. `bangun_layanan.py` lengkap: semua CSV kurasi digabung ke `layanan.json` (baris tanpa `tanggal_verifikasi` dibuang).
  3. UI `#/layanan`:
     - segmen kategori, saring kecamatan, "Terdekat dari saya" (jarak di perangkat), kartu item (telepon, rute, OSM);
     - `#/layanan/peta`: Leaflet dimuat malas dengan tile OSM `https://tile.openstreetmap.org/{z}/{x}/{y}.png` [D] beserta atribusi "© OpenStreetMap contributors", lapisan poligon kecamatan, penanda `circleMarker` berwarna per jenis, chip filter, dan popup;
     - kartu Kerja & BBM (UMK, BBM, LPG beserta tanggal berlaku).
  4. Label "Data lokasi dari OpenStreetMap, bisa belum lengkap. Bantu lengkapi di openstreetmap.org" di halaman Layanan.
  5. Jadwal bulanan fasilitas di `jalankan_semua.py`. Data fasilitas di-commit.
  6. `cek_tampilan` untuk `#/layanan` dan `#/layanan/peta` (tile mungkin tidak termuat di headless, jadi yang dicek hanya `siap=1` dan jumlah penanda lewat dump-dom). Push, tag `v0.4`.
- **Kriteria selesai:**
  - `fasilitas.json` memuat ≥ 1 entri per jenis utama (RS, puskesmas/klinik, apotek, sekolah, pasar), dan setiap entri punya `kec`;
  - `layanan.json` lolos `cek_data`;
  - dump-dom peta memuat ≥ 50 penanda;
  - live diperbarui.
- **Anggaran:** 9 kredit, BATAS 40 alat.
- **Titik berhenti:**
  - Overpass timeout atau 429 dua kali: coba server cadangan `https://overpass.kumi.systems/api/interpreter` [D] sekali, lalu laporkan.
  - CSV pemilik belum ada: buat templatnya, kerjakan bagian OSM saja, lalu laporkan.
- **Jangan:** menyalin jadwal KRL atau BST (cukup tautan resmi), mengambil data dari Google Maps, atau menambah plugin Leaflet (cluster dan lainnya).

**Prompt T7:**
```
[BLOK UMUM]
TAHAP 7: Fasilitas, layanan, transportasi, info rutin, peta Leaflet → Rilis 0.4. BATAS = 40 alat.
Baca rencana 2.4–2.5, 6.4.12–6.4.13, 7.4 (Layanan), 10 (lisensi OSM), referensi/komponen.md,
dan "Tahap 7". CSV kurasi pemilik ada di data/ (bila belum, buat templat lalu lanjut bagian OSM).
Kriteria selesai: fasilitas.json ≥ 1 entri per jenis utama dan semua punya kec; layanan.json lolos
cek_data; dump-dom peta ≥ 50 penanda; live diperbarui; tag dasbor_sukoharjo-v0.4.
```

---

### Tahap 8: Profil 12 kecamatan dan perbandingan (Rilis 0.5)
- **Tujuan:** halaman profil lengkap sesuai bagian 4.2, choropleth, dan perbandingan dua kecamatan.
- **Prasyarat pemilik:** `data/statistik_kecamatan.csv` terisi (12 baris dan baris `_kabupaten`). Setelah tahap selesai, pemilik meninjau 12 draf deskripsi.
- **Langkah:**
  1. `ambil_ringkasan_wiki.py`:
     - 12 judul dengan pola `<Nama>,_Sukoharjo` [D];
     - bila respons 404, coba `Kecamatan_<Nama>` sekali;
     - simpan ke `data/mentah/wiki/`;
     - cetak 1 baris per kecamatan (judul dan panjang extract).
  2. Sonnet membaca extract (pendek) dan menulis `data/profil_kecamatan.json`:
     - deskripsi 40–70 kata dengan kalimat sendiri;
     - `ciri_khas` hanya fakta yang ada di sumber, masing-masing dengan URL;
     - `status_isi: "draf"`.
     
     Kerjakan 4 kecamatan per langkah, lalu commit.
  3. `bangun_profil.py`: gabungkan statistik, jumlah desa dan kelurahan (dari desa.json), tetangga, jumlah fasilitas, dan kantor (dari layanan) ke `hasil/situs/data/profil_kecamatan.json`.
  4. `cek_profil.py`: aturan di 4.3 butir 4.
  5. UI:
     - `#/wilayah`: choropleth dengan pemilih metrik dan legenda, tabel yang bisa diurutkan;
     - `#/wilayah/<slug>`: bagian 4.2 dan lencana "draf";
     - `#/wilayah/bandingkan?a=&b=`: dua kolom angka dengan bar horizontal SVG sederhana;
     - kartu "Kenali Kec. X" di Beranda.
  6. `cek_tampilan` untuk `#/wilayah` dan `#/wilayah/weru` (1 putaran). Push, tag `v0.5`.
- **Kriteria selesai:**
  - `cek_profil.py` lulus;
  - 12 profil tampil (dump-dom per slug lewat loop dalam satu skrip);
  - perbandingan berfungsi untuk satu pasangan.
- **Anggaran:** 9 kredit, BATAS 40 alat.
- **Titik berhenti:**
  - Selisih total penduduk > 1%: berhenti dan minta pemilik memeriksa CSV.
  - Wikipedia tidak punya artikel untuk suatu kecamatan: deskripsi berisi fakta dari statistik saja dan ditandai "perlu sumber".
- **Jangan:** mengarang fakta, menyalin paragraf Wikipedia apa adanya, atau mengubah status draf menjadi `ditinjau` (itu hak pemilik).

**Prompt T8:**
```
[BLOK UMUM]
TAHAP 8: Profil 12 kecamatan dan perbandingan → Rilis 0.5. BATAS = 40 alat.
Baca rencana bagian 4 (semua), 6.4.10, 7.4 (Wilayah), referensi/komponen.md, dan "Tahap 8".
Masukan pemilik: data/statistik_kecamatan.csv.
Deskripsi ditulis dengan kalimat sendiri dari sumber; setiap ciri khas wajib ber-URL; status "draf".
Kriteria selesai: cek_profil.py lulus; 12 profil tampil (dump-dom); perbandingan berfungsi; live
diperbarui; tag dasbor_sukoharjo-v0.5. Selisih total penduduk > 1% → berhenti.
```

---

### Tahap 9: Pencarian, PWA, halaman statis, aksesibilitas, umpan balik (Rilis 1.0)
- **Prasyarat pemilik:**
  - Pilih saluran umpan balik (K4): Google Form, GitHub Issues, atau email.
  - Putuskan analitik (K5).
  - Selesaikan tinjauan profil.
- **Langkah:**
  1. `bangun_indeks_cari.py`: susun `cari.json` dari kecamatan, desa, komoditas, fasilitas bernama, dan layanan. Normalisasi huruf kecil tanpa diakritik. Target ≤ 80 KB.
  2. `js/cari.js` dan `#/cari`:
     - indeks dimuat malas saat ikon cari diketuk;
     - pencocokan awalan dan substring;
     - hasil dikelompokkan per jenis, maksimal 30.
  3. PWA:
     - `manifest.webmanifest` (nama, `theme_color` #1C7556, ikon 192/512 dibuat dari `logo.svg` dengan skrip Python stdlib; bila tidak mungkin tanpa pustaka, gunakan Edge headless untuk merender PNG);
     - `sw.js` sesuai 6.7 dengan cache `sh-v1`, daftar aset tertulis eksplisit, versi dinaikkan setiap rilis;
     - tombol "Pasang aplikasi" opsional bila event `beforeinstallprompt` ada.
  4. `bangun_halaman_kecamatan.py`:
     - 12 halaman `kecamatan/<slug>/index.html` berisi HTML statis (judul, deskripsi, angka kunci, sumber, tautan ke aplikasi `../../#/wilayah/<slug>`) memakai `gaya.css` yang sama;
     - meta deskripsi dan OG;
     - `sitemap.xml` dan `robots.txt`.
  5. `cek_kontras.py`: hitung rasio kontras pasangan token di 7.2 untuk kedua tema. Perbaiki yang gagal sesuai aturan di 7.2.
  6. Perluas `cek_situs.py`:
     - semua `button` punya teks atau `aria-label`;
     - `img` dan `svg` bermakna punya label;
     - anggaran ukuran;
     - SW mencantumkan semua aset yang ada.
  7. Umpan balik: tautan "Laporkan kesalahan data" di setiap meta kartu, menuju saluran pilihan pemilik dengan parameter modul. Bila memakai GitHub Issues, buat `.github/ISSUE_TEMPLATE/laporan_data.md`.
  8. Analitik (bila K5 = ya): satu skrip GoatCounter atau Cloudflare Web Analytics sesuai pilihan, ditambah kalimat privasi di halaman Tentang.
  9. Jalankan daftar periksa rilis (bagian 11.3) lewat `cek_rilis.py` yang memanggil semua `cek_*`. Push, tag `dasbor_sukoharjo-v1.0`.
- **Kriteria selesai:**
  - `cek_rilis.py` lulus semua butir;
  - SW terdaftar (dump-dom tidak bisa memeriksa ini, jadi pemilik membuka DevTools → Application);
  - 12 halaman statis dan sitemap ada.
- **Anggaran:** 9 kredit, BATAS 45 alat.
- **Titik berhenti:** bug cache SW menyebabkan aset basi setelah 2 kali perbaikan. Matikan SW (hapus registrasi dan sediakan `sw.js` kosong yang melakukan `self.registration.unregister()`), lalu laporkan. Rilis tetap jalan tanpa PWA.
- **Jangan:** notifikasi push, akun pengguna, atau backend.

**Prompt T9:**
```
[BLOK UMUM]
TAHAP 9: Pencarian, PWA, halaman statis/SEO, aksesibilitas, umpan balik → Rilis 1.0. BATAS = 45 alat.
Baca rencana 6.4.16, 6.7, 7.2 (kontras), 7.6, 11, referensi/komponen.md, dan "Tahap 9".
Keputusan pemilik: umpan balik = [ISI]; analitik = [ISI: tidak/GoatCounter/Cloudflare].
Kriteria selesai: cek_rilis.py lulus; 12 halaman kecamatan statis + sitemap.xml; tag
dasbor_sukoharjo-v1.0. SW bermasalah setelah 2 kali perbaikan → matikan SW, lanjutkan rilis.
```

---

### Tahap 10: Runbook dan penutupan
- **Langkah:**
  1. README final berisi:
     - status selesai;
     - cara menjalankan lokal;
     - jadwal pemeliharaan (11.4);
     - cara memperbarui tiap CSV manual;
     - cara menjalankan pengambil data dari PC bila Actions diblokir;
     - daftar sumber dan lisensi.
  2. Kosongkan `_tmp/`.
  3. Perbarui memori Serena `dasbor_sukoharjo/core`, entri di memori `core`, dan `task_completion` (daftar `cek_*`).
  4. Commit dan push.
- **Kriteria selesai:** README memuat semua butir di atas, `_tmp/` kosong, dan memori terbarui.
- **Anggaran:** 3 kredit, BATAS 15 alat.
- **Jangan:** menambah fitur.

**Prompt T10:**
```
[BLOK UMUM]
TAHAP 10: Runbook dan penutupan. BATAS = 15 alat.
Baca rencana 10, 11.4, dan "Tahap 10". Kerjakan langkahnya; jangan menambah fitur.
Kriteria selesai: README berisi status selesai, cara lokal, jadwal pemeliharaan, cara mengisi tiap
CSV, cara menjalankan dari PC, sumber dan lisensi; _tmp/ kosong; memori Serena terbarui; push.
```

---

## 9. Anggaran dan efisiensi

### 9.1 Perkiraan per tahap
Asumsi: 1 kredit setara kira-kira 4–5 panggilan alat Sonnet dengan konteks kecil sampai sedang. **Ini perkiraan, bukan fakta.** Kalibrasikan dengan pemakaian nyata di akhir T0. Bila meleset lebih dari 30%, sesuaikan kredit tahap berikutnya secara proporsional, tetapi batas alatnya tetap.

| Tahap | Isi | Kredit | Batas alat |
|---|---|---|---|
| T0 | Fondasi, uji jaringan | 6 | 30 |
| T1 | Spike harga | 6 | 30 |
| T2 | Sistem desain, kerangka | 10 | 45 |
| T3 | Wilayah dan peta | 7 | 35 |
| T4 | Cuaca, pipeline, deploy (0.1) | 10 | 45 |
| T5 | Harga (0.2) | 8 | 40 |
| T6 | Modul ringan (0.3) | 10 | 50 |
| T7 | Fasilitas dan layanan (0.4) | 9 | 40 |
| T8 | Profil kecamatan (0.5) | 9 | 40 |
| T9 | Penyempurnaan (1.0) | 9 | 45 |
| T10 | Runbook | 3 | 15 |
| **Total** | | **87** | **415** |
| Cadangan 15% (perbaikan pascarilis, perubahan sumber) | | 13 | 60 |
| **Total dengan cadangan** | | **≈ 100** | **≈ 475** |

### 9.2 Aturan efisiensi untuk eksekutor
1. Sistem desain ditetapkan sekali di 7.2 dan ditulis sekali di T2. Tahap berikutnya hanya memakai kelas di `komponen.md` dan tidak menambah token.
2. Data, logika, dan tampilan dipisah:
   - skrip Python menormalisasi data ke skema tetap;
   - satu berkas `js/tampilan/<x>.js` per halaman;
   - komponen bersama hanya ada di `komponen.js`.
   
   Perubahan sumber data hanya menyentuh satu skrip `ambil_*`.
3. `umum.py`, `jalankan_semua.py` (registri modul), dan `cek_data.py` (dict aturan) dibuat sekali. Modul baru cukup menambah satu entri di tiap berkas.
4. Keluaran perintah selalu dipotong. Skrip mencetak ringkasan. JSON besar diperiksa dengan skrip, tidak dibaca langsung.
5. Pengujian memakai skrip `cek_*` dan dump-dom. Tangkapan layar maksimal 2 putaran per tahap UI.
6. Rencana dibaca per bagian (offset/limit), tidak utuh.
7. Satu siklus "push lalu tunggu Actions" maksimal 3 kali per tahap. Sebelum push, jalankan pipeline lokal sampai lulus.
8. Respons API pertama disimpan ke `referensi/contoh_*.json` agar pemetaan bidang tidak perlu mengambil ulang.
9. Python stdlib, tanpa pip. Front-end tanpa npm. Vendor diunduh sekali.

### 9.3 Titik paling berisiko membuang kredit
| Tempat | Gejala | Pencegahan |
|---|---|---|
| Harga (T1) | Mencoba endpoint satu per satu | Hanya meniru tangkapan pemilik, 2 percobaan per kandidat, batas 30 |
| Perakitan poligon OSM (T3) | Perbaikan geometri berulang | 1 percobaan + 1 perbaikan, lalu mode skematik |
| Revisi visual (T2) | "Sedikit lagi" berulang kali | Nilai pasti di 7.2, maksimal 2 putaran |
| Debug Actions | Push, tunggu, gagal, ulang | Jalankan lokal dulu, kerangka YAML di 6.5, maksimal 3 siklus |
| Encoding PowerShell 5.1 | BOM merusak JSON, karakter rusak | Berkas hanya ditulis dengan alat tulis atau Python `utf-8` |
| Zona waktu | Selisih 7 jam | `timezone(timedelta(hours=7))`, ISO dengan offset, unit test |
| Service worker | Aset basi, sulit dilacak | Versi cache eksplisit, aturan matikan SW di T9 |
| Membaca berkas besar | Konteks penuh | Aturan 3 Blok Umum, ringkasan lewat skrip |
| Chart.js | Konfigurasi bolak-balik | Hanya di satu tempat (detail harga), gaya di 7.2 |

---

## 10. Risiko dan mitigasi

### 10.1 Teknis
| Risiko | Mitigasi |
|---|---|
| Sumber Indonesia memblokir IP runner Actions (luar negeri) [?] | Diuji di T0. **Rencana Jaringan B:** jalankan `jalankan_semua.py` dari PC pemilik lewat Windows Task Scheduler (tiap 3 jam saat PC menyala), commit data cepat ke cabang `data`, dan workflow deploy membaca dari cabang itu. Ini menambah sekitar 1 tahap (5 kredit). Alternatif: Cloudflare Worker sebagai proksi, tetapi lokasi egress-nya [?]. **Status 2026-11-16 [T]:** harga dan Overpass timeout dari Actions; BMKG, gempa, Open-Meteo, dan Wikipedia terjangkau. Rencana Jaringan B dijalankan untuk harga (`skrip/jadwal_harga.ps1`, tugas `DasborHarga`). Penyebab timeout belum terbukti sebagai blokir IP (panggilan lokal juga timeout sesaat). |
| API berubah atau mati | Validasi skema di `cek_data.py`. Versi lama dipertahankan dengan status `basi`. Alur kegagalan di Actions memicu email ke pemilik [D: notifikasi jadwal dikirim ke pengguna yang terakhir mengubah cron]. |
| Pembatasan laju | Jeda 1,5 detik per host, backoff, 12 permintaan per 3 jam ke BMKG |
| Jadwal Actions tertunda atau dinonaktifkan setelah 60 hari tanpa aktivitas [D] | Commit data harga harian menjaga repo tetap aktif. Bila memakai jalur C, pemilik commit pembaruan CSV minimal tiap bulan. Halaman Status menampilkan umur data. |
| Repo membengkak | Data cepat tidak di-commit (6.1). Riwayat harga maksimal 400 hari. |
| Tile OSM dibatasi kebijakan pemakaian [D] | Peta utama memakai SVG sendiri. Leaflet hanya di halaman peta. Atribusi wajib. Bila lalu lintas naik, pindah ke penyedia tile lain dengan atribusi. |

### 10.2 Data
| Risiko | Mitigasi |
|---|---|
| Harga tidak mewakili Sukoharjo | Label tingkat wajib (spanduk). Angka provinsi atau kota tidak pernah ditampilkan sebagai angka Sukoharjo. |
| Data basi | Titik kesegaran, ambang di 6.7, halaman Status |
| Nomor atau alamat salah | Hanya baris terverifikasi yang tampil, tanggal verifikasi ditampilkan, ada tautan laporkan kesalahan |
| OSM tidak lengkap | Label dan ajakan berkontribusi ke OSM |
| Jadwal sholat atau Hijriah berbeda dari resmi | Validasi ±2 menit, label "perkiraan" pada Hijriah, rujukan ke Kemenag |
| Deskripsi kecamatan keliru | Status draf, tinjauan pemilik, ciri khas wajib bersumber |

### 10.3 Hukum dan etika
- **Atribusi:**
  - BMKG: cantumkan BMKG sebagai sumber [D, periksa ketentuan di data.bmkg.go.id].
  - Open-Meteo: CC BY 4.0, gratis untuk non-komersial [D].
  - OSM: ODbL, "© OpenStreetMap contributors".
  - Wikipedia: CC BY-SA. Karena itu situs menulis ringkasan dengan kalimat sendiri dan menautkan sumbernya.
  - BPS: cantumkan sumber [D].
  - Panel Harga, PIHPS, dan SP2KP: ketentuan [?], wajib dicek di T1 sebelum dipakai.
- Tidak ada scraping yang membutuhkan login, tidak ada pelanggaran ToS, dan frekuensi permintaan rendah.
- Footer setiap halaman: "Situs ini dibuat warga secara mandiri dan bukan situs resmi Pemerintah Kabupaten Sukoharjo. Data berasal dari sumber publik yang tercantum." Tidak memakai lambang daerah, nama domain atau nama situs tidak meniru instansi, dan tidak memakai kata "resmi".
- Privasi: tanpa cookie. Lokasi dihitung di perangkat. Analitik (bila ada) tanpa cookie. Formulir warga tidak menampilkan data pribadi.
- Lisensi kode MIT dan isi CC BY 4.0 [U, K6].

### 10.4 Operasional (satu orang)
- Pemeliharaan terjadwal (11.4) sekitar 15 menit per bulan, ditambah sekitar 1 jam per tahun.
- Semua pembaruan manual berupa CSV kecil dengan templat.
- Halaman Status dan email kegagalan Actions memberi tahu pemilik tanpa perlu memeriksa manual.
- Bila pemilik berhenti merawat, data otomatis tetap jalan, data manual ditandai basi, dan tidak ada yang rusak.

---

## 11. Kualitas dan pengujian

### 11.1 Cek otomatis per modul
| Modul | Cek (`cek_data.py` kecuali disebut lain) |
|---|---|
| Semua | Amplop valid, `diperbarui` berformat ISO +07:00, `status` sah, sumber tidak kosong |
| Cuaca | 12 kecamatan, ≥ 8 slot ke depan, suhu 10–42, kelembapan 0–100, waktu menaik |
| Hujan | 12 × 7 hari, mm ≥ 0, peluang 0–100 |
| Udara | ≥ 24 jam, AQI ≥ 0, kategori sesuai rentang |
| Gempa | Magnitudo 0–10, jarak dihitung, lat/lon dalam batas Indonesia |
| Harga | ≥ 8 komoditas, harga > 0, `tingkat` sah, perubahan > 60% ditandai, riwayat tanggal unik dan urut |
| Sholat | Satu tahun penuh, 7 kolom urut naik per hari, tahun = tahun berjalan (peringatan mulai 1 Desember) |
| Libur | Tahun = tahun berjalan, tanggal valid |
| Kecamatan/profil | 12 slug, `cek_profil.py` (4.3) |
| Fasilitas | Setiap entri punya `kec` dan koordinat di dalam kotak batas kabupaten |
| Layanan | Setiap baris punya `tanggal_verifikasi` dan URL sumber |
| Situs | `cek_situs.py`: ukuran, tautan, aksesibilitas dasar, URL eksternal; `cek_tampilan.ps1`: `siap=1` di semua rute; `cek_kontras.py` |
| Fungsi murni | `uji_umum.py`: format, perubahan harga, haversine, point-in-polygon (versi Python), pasaran (dua tanggal contoh) |

### 11.2 Data tidak basi
- `status.json` live dibandingkan dengan ambang 6.7, dicek di halaman Status dan oleh `cek_data.py --mode live` (mengunduh dari `SITUS_URL`).
- Pemilik bisa menjalankan `python skrip/cek_data.py --mode live` kapan saja. Keluarannya satu tabel.

### 11.3 Daftar periksa rilis (`cek_rilis.py` dan manual)
1. Semua `cek_*` lulus dan `uji_umum.py` lulus.
2. Tidak ada `contoh: true` di `hasil/situs/data/` (data contoh hanya di `data/contoh/`).
3. Footer memuat pernyataan bukan situs resmi. Halaman Tentang memuat semua sumber dan lisensi.
4. Semua rute `siap=1` di 390×844, tema terang dan gelap.
5. Anggaran ukuran terpenuhi.
6. Tidak ada teks UI berbahasa Inggris (pemeriksaan daftar kata umum: "Loading", "Error", "Search").
7. Manual: pemilik membuka situs di HP Android dengan jaringan seluler, mengganti kecamatan, membuka harga dan peta, mencoba mode pesawat (tampilan luring), dan menjalankan PageSpeed Insights (target Performance ≥ 90 di mobile).
8. Tag rilis dibuat.

### 11.4 Jadwal pemeliharaan pemilik
| Kapan | Tugas |
|---|---|
| Mingguan (jalur C) | Isi harga manual (sekitar 15 menit) |
| Bulanan | Buka halaman Status, perbarui BBM/LPG bila berubah, commit apa pun agar jadwal tetap aktif |
| Enam bulanan | Verifikasi ulang kontak darurat dan layanan (perbarui `tanggal_verifikasi`) |
| Tahunan (Desember–Januari) | Libur tahun depan (SKB), UMK baru, `hitung_sholat.py` tahun baru, statistik BPS edisi baru, tinjau profil |

---

## 12. Peluang pengembangan setelah rilis
- **Umpan balik warga:**
  - tautan "Laporkan kesalahan" per kartu;
  - formulir singkat "Fitur apa yang kamu butuhkan?" di halaman Tentang;
  - bagikan tautan lewat grup WhatsApp RT/RW dan komunitas lokal, lalu ukur lewat analitik tanpa cookie.
- **Notifikasi:** saluran Telegram atau WhatsApp Channel yang diisi bot Actions (ringkasan pagi: cuaca dan harga). Biayanya nol untuk Telegram Bot API [D]. Push notification web butuh server, jadi ditunda.
- **Kontribusi data warga:**
  - harga pasar lewat formulir dengan moderasi pemilik sebelum masuk CSV, ditampilkan sebagai "laporan warga" terpisah dari data resmi;
  - jadwal pasaran tiap pasar tradisional (M17).
- **Modul tertunda:** peringatan dini BMKG (bila spike T6 menemukan format terstruktur), tinggi muka air Bengawan Solo, agenda budaya dan wisata, direktori UMKM, kalender tanam.
- **Cuaca per desa:** semua desa (1 permintaan per desa, dipecah per jadwal) dan pencarian "desa saya".
- **Bahasa Jawa** sebagai pilihan antarmuka.
- **Template untuk kabupaten lain:** skema dan skrip sudah generik, cukup mengganti daftar wilayah.

---

## 13. Daftar hal yang belum diketahui

### 13.1 Harus diputuskan pemilik sebelum eksekusi
| ID | Keputusan | Rekomendasi | Batas waktu |
|---|---|---|---|
| K1 | Repo: `dasbor_sukoharjo` jadi repo git bersarang yang di-push ke repo GitHub **publik** terpisah, dan diabaikan oleh repo workspace | Ya. Pages gratis butuh repo publik [D], dan repo workspace tidak perlu publik. | Sebelum T0 |
| K2 | Nama situs dan alamat (`<user>.github.io/<repo>` atau domain sendiri) | "Sukoharjo Hari Ini", alamat bawaan GitHub dulu | Sebelum T2 (teks di UI) |
| K3 | Kesediaan waktu pemilik untuk data manual (harga pekanan, verifikasi kontak) | Menentukan jalur harga B atau B+C | Sebelum T5 |
| K4 | Saluran umpan balik | GitHub Issues dan Google Form | Sebelum T9 |
| K5 | Analitik | GoatCounter atau Cloudflare Web Analytics, tanpa cookie, atau tanpa analitik | Sebelum T9 |
| K6 | Lisensi | Kode MIT, isi CC BY 4.0 | Sebelum T10 |

### 13.2 Fakta yang belum diketahui dan cara tercepat menjawabnya
| Hal | Status | Cara menjawab | Di tahap |
|---|---|---|---|
| Sumber terjangkau dari runner Actions | [?] | `uji_jaringan.yml` | T0 |
| Endpoint harga tingkat kabupaten | [?] | Tangkapan DevTools pemilik (5.4) | T1 |
| Cakupan PIHPS untuk Sukoharjo atau Surakarta | [?] | Pemilik melihat filter wilayah di PIHPS | Sebelum T1 |
| ToS Panel Harga, PIHPS, SP2KP | [?] | Pemilik menyalin halaman ketentuan | Sebelum T1 |
| Nama bidang dan satuan respons BMKG | [D] | `referensi/contoh_bmkg.json` | T3/T4 |
| Batas laju BMKG | [D] | Halaman ketentuan data BMKG, ditambah pengamatan 429 | T4 |
| Kode kecamatan dan adm4 tiap kecamatan | [D] | Berkas kode wilayah dan uji 200 dari BMKG | T3 |
| `admin_level` kecamatan di OSM dan kelengkapan poligon | [D] | Kueri Overpass | T3 |
| Struktur JSON gempa BMKG, parameter Open-Meteo | [D] | Respons pertama disimpan | T6 |
| Parameter Kemenag (ihtiyat) | [D] | Perbandingan dengan 3 tanggal Kemenag | T6 |
| Tanggal jangkar pasaran | [?] | 2 tanggal dari kalender tepercaya (pemilik) | T6 |
| Nomor darurat lokal Sukoharjo | [?] | Situs resmi Pemkab/BPBD/Dinkes (pemilik) | T4/T7 |
| Stasiun KRL di wilayah Sukoharjo, koridor BST | [D] | Situs KAI Commuter dan BST (pemilik) | T7 |
| Publikasi harga oleh Pemkab Sukoharjo | [?] | Pencarian pemilik (5.4 butir 8) | Sebelum T1 |
| Feed peringatan dini BMKG | [?] | Spike ≤ 4 alat | T6 |
| Cache-Control GitHub Pages | [D] | `Invoke-WebRequest` ke situs live, lihat header | T4 |
| Kebijakan 60 hari jadwal Actions | [D] | Dokumentasi GitHub Actions | T4 |

### 13.3 Asumsi kerja
- Pemilik punya akun GitHub dan Edge terpasang di Windows (untuk `cek_tampilan`).
- Python 3.9 atau lebih baru sudah terpasang dan ada di PATH.
- Lalu lintas situs rendah sampai sedang (di bawah batas lunak bandwidth GitHub Pages [D]).
- Mayoritas pengguna memakai Android dengan Chrome versi baru, jadi ES modules dan `Intl` kalender Islam tersedia [D].
