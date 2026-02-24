# Perancangan Arsitektur Bot Telegram 'Asisten Belanja Cerdas'

Bot 'Asisten Belanja Cerdas' dirancang untuk membantu pengguna melacak voucher dan promo dari platform e-commerce seperti Shopee dan TikTok Shop. Arsitektur bot ini akan berfokus pada modularitas, skalabilitas, dan kemudahan pemeliharaan.

## 1. Komponen Utama

Bot ini akan terdiri dari beberapa komponen utama yang saling berinteraksi:

### 1.1. Telegram Bot API Handler
Komponen ini bertanggung jawab untuk berinteraksi langsung dengan Telegram Bot API. Ini akan menerima perintah dari pengguna (misalnya, `/start`, `/tambah_keyword`, `/lihat_promo`) dan mengirimkan respons atau notifikasi kembali ke pengguna. Library seperti `python-telegram-bot` akan digunakan untuk mempermudah interaksi ini.

### 1.2. Modul Pengelola Data Promo
Modul ini adalah inti dari fungsionalitas pelacakan promo. Mengingat tantangan dalam melakukan *web scraping* langsung dan berkelanjutan pada platform e-commerce besar (yang seringkali melanggar Syarat & Ketentuan dan rentan terhadap perubahan struktur situs), pendekatan awal akan berfokus pada:
*   **Pencarian Berbasis Kata Kunci:** Pengguna dapat mendaftarkan kata kunci produk atau kategori yang diminati. Bot kemudian akan melakukan pencarian berkala di platform e-commerce (melalui API publik jika tersedia, atau simulasi pencarian web) untuk menemukan promo yang relevan.
*   **Pemantauan URL Produk:** Pengguna dapat memberikan URL produk spesifik. Bot akan memantau perubahan harga atau ketersediaan voucher untuk produk tersebut.
*   **Agregasi Promo Publik:** Memanfaatkan sumber-sumber promo publik (misalnya, forum diskon, akun media sosial penyedia promo) sebagai input data, jika memungkinkan dan legal.

**Catatan Penting:** Implementasi *web scraping* langsung untuk skala besar dan real-time sangat kompleks dan berisiko. Untuk bot profesional, disarankan untuk mencari kemitraan API resmi atau menggunakan data agregator pihak ketiga yang legal. Dalam konteks proyek ini, kita akan fokus pada simulasi pencarian dan pemantauan sederhana yang dapat dikembangkan lebih lanjut.

### 1.3. Database (SQLite)
Sebuah database ringan seperti SQLite akan digunakan untuk menyimpan data-data penting, antara lain:
*   **Informasi Pengguna:** ID Telegram, preferensi notifikasi.
*   **Keyword Pelacakan:** Kata kunci yang didaftarkan pengguna untuk promo.
*   **URL Produk Terpantau:** Daftar URL produk yang ingin dipantau harganya.
*   **Riwayat Promo:** Promo yang ditemukan dan telah dikirimkan kepada pengguna untuk menghindari duplikasi.

### 1.4. Modul Penjadwal (Scheduler)
Modul ini akan menjalankan tugas-tugas secara berkala, seperti:
*   Melakukan pencarian promo berdasarkan kata kunci yang terdaftar.
*   Memantau perubahan harga pada URL produk yang dipantau.
*   Mengirimkan notifikasi promo kepada pengguna pada interval yang ditentukan.

### 1.5. Modul Notifikasi
Bertanggung jawab untuk memformat informasi promo yang ditemukan dan mengirimkannya kepada pengguna melalui Telegram. Ini akan memastikan pesan yang dikirimkan jelas, informatif, dan mudah dibaca.

## 2. Alur Kerja (Workflow)

1.  **Inisialisasi Bot:** Bot dimulai dan terhubung ke Telegram API.
2.  **Pendaftaran Pengguna:** Pengguna memulai interaksi dengan bot (misalnya, `/start`). Bot menyimpan ID pengguna.
3.  **Konfigurasi Preferensi:** Pengguna menambahkan kata kunci (`/tambah_keyword <keyword>`) atau URL produk (`/pantau_url <url>`).
4.  **Proses Pelacakan:** Modul penjadwal secara berkala memicu modul pengelola data promo untuk mencari atau memantau promo baru.
5.  **Penyimpanan Data:** Promo yang ditemukan disimpan ke database.
6.  **Notifikasi:** Modul notifikasi mengirimkan promo yang relevan kepada pengguna berdasarkan preferensi mereka.

## 3. Teknologi yang Digunakan

*   **Bahasa Pemrograman:** Python 3.x
*   **Library Telegram:** `python-telegram-bot`
*   **Database:** `SQLite` (melalui modul `sqlite3` bawaan Python)
*   **Penjadwal:** `APScheduler` atau implementasi sederhana dengan `threading.Timer` (untuk kasus deployment sederhana).
*   **HTTP Requests:** `requests` (untuk simulasi pencarian web atau interaksi API).

## 4. Struktur Direktori Proyek

```
telegram_promo_bot/
├── bot.py                # Logika utama bot Telegram
├── config.py             # Konfigurasi bot (token, dll.)
├── database.py           # Fungsi-fungsi interaksi database
├── promo_tracker.py      # Logika pelacakan promo (pencarian/pemantauan)
├── scheduler.py          # Penjadwal tugas berkala
├── .env                  # Variabel lingkungan (untuk token API)
├── requirements.txt      # Daftar dependensi Python
└── README.md             # Dokumentasi proyek
```

Dokumen ini akan menjadi dasar untuk implementasi kode bot pada fase berikutnya. Fokus utama adalah pada fungsionalitas inti dan menghindari kompleksitas *scraping* yang berlebihan pada tahap awal.
