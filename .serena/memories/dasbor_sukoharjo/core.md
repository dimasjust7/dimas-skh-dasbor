# dasbor_sukoharjo / core
- Tahap: T0, T1 selesai. T2A selesai (cek_situs lulus: gzip awal 11 KB, gaya.css 12 KB). Berikutnya T2B.
- Berkas kunci (hasil/situs/): gaya.css, index.html, js/{format,data,komponen,grafik,peta,utama}.js,
  ikon/sprite.svg (48 ikon), vendor/{leaflet,chartjs}/ + VERSI.txt. skrip/{ambil_vendor,cek_situs}.py.
- Kontrak tampilan: js/tampilan/<nama>.js mengekspor async render(el, {rute,param,kec,muat,ulang}).
  Nama: beranda,harga,cuaca,wilayah,layanan,tentang,status,cari. Modul tak ada => "Segera hadir".
- Query dibaca dari hash (#/?contoh=1&tema=gelap&kec=weru). Mode contoh memuat data/contoh/<nama>.json.
  utama.js menyetel body.dataset.siap="1" setelah render. Nav membawa contoh/tema antarhalaman.
- Keputusan: ikon/logo.svg DIBLOKIR kiroignore (*.svg fs_write); logo disematkan inline di index.html,
  favicon data-URI. Chart.js dikunci 4.6.1 (/dist/chart.umd.min.js -> vendor/chartjs/chart.umd.js).
- Masalah terbuka: shell hanya menampilkan gema; baca hasil via berkas. vendor/ tak bisa dibaca read_file.
- Sisa T2 (T2B): data/contoh/*.json, js/tampilan/beranda.js (7.3), cek_tampilan.ps1, 3 PNG, referensi/komponen.md.
- Jangan sentuh: data/harga*.json, ambil_harga.py, jadwal_harga.ps1.
