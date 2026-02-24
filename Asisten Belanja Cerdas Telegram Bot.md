# Asisten Belanja Cerdas Telegram Bot

Bot Telegram ini dirancang untuk membantu Anda melacak promo dan voucher dari platform e-commerce seperti Shopee dan TikTok Shop berdasarkan kata kunci atau URL produk yang Anda berikan. Bot ini akan berjalan 24/7 menggunakan GitHub Actions.

## Fitur

*   **Pelacakan Kata Kunci:** Tambahkan kata kunci untuk mencari promo relevan di Shopee dan TikTok Shop.
*   **Pelacakan URL Produk:** Pantau perubahan harga atau ketersediaan voucher pada URL produk spesifik.
*   **Notifikasi Real-time:** Dapatkan notifikasi langsung di Telegram saat promo baru ditemukan.
*   **Manajemen Mudah:** Tambah, hapus, dan lihat daftar kata kunci atau URL yang dilacak melalui perintah Telegram.

## Persyaratan

*   Akun Telegram
*   Akun GitHub
*   Python 3.8+

## Instalasi dan Konfigurasi

### 1. Dapatkan Token Bot Telegram Anda

1.  Buka aplikasi Telegram Anda dan cari `@BotFather`.
2.  Kirim perintah `/newbot` kepada BotFather.
3.  Ikuti instruksi untuk memilih nama dan username untuk bot Anda. Setelah selesai, BotFather akan memberikan Anda **Token API**.
4.  Simpan token ini dengan aman, Anda akan membutuhkannya nanti.

### 2. Siapkan Repositori GitHub Anda

1.  Buat repositori GitHub baru (misalnya, `telegram-promo-bot`).
2.  Clone repositori ini ke komputer lokal Anda.
3.  Salin semua file dari proyek bot ini ke dalam repositori lokal Anda.

### 3. Konfigurasi Variabel Lingkungan

Bot ini memerlukan `TELEGRAM_BOT_TOKEN` untuk beroperasi. Anda dapat menyediakannya melalui file `.env` atau sebagai GitHub Secret.

#### Opsi A: Menggunakan File `.env` (untuk pengembangan lokal)

Buat file bernama `.env` di direktori root proyek Anda dengan konten berikut:

```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
```

Ganti `YOUR_TELEGRAM_BOT_TOKEN_HERE` dengan token yang Anda dapatkan dari BotFather.

#### Opsi B: Menggunakan GitHub Secrets (untuk deployment 24/7)

Ini adalah metode yang direkomendasikan untuk deployment. Anda akan menambahkan token bot Anda sebagai *secret* di repositori GitHub Anda.

1.  Di repositori GitHub Anda, navigasikan ke `Settings` > `Secrets and variables` > `Actions`.
2.  Klik `New repository secret`.
3.  Untuk `Name`, masukkan `TELEGRAM_BOT_TOKEN`.
4.  Untuk `Secret`, masukkan token API Telegram bot Anda.
5.  Klik `Add secret`.

### 4. Instal Dependensi Python

Pastikan Anda memiliki Python 3.8 atau yang lebih baru terinstal. Kemudian, instal dependensi yang diperlukan:

```bash
pip install -r requirements.txt
```

## Menjalankan Bot (Lokal)

Untuk menjalankan bot secara lokal (misalnya, untuk pengujian):

```bash
python bot.py
```

Bot akan mulai berjalan dan Anda dapat berinteraksi dengannya di Telegram.

## Deployment 24/7 dengan GitHub Actions (dengan Pertimbangan)

Untuk menjaga bot tetap berjalan 24/7, kita akan menggunakan GitHub Actions. **Penting untuk memahami batasan pendekatan ini untuk bot yang membutuhkan persistensi data.**

### Batasan GitHub Actions untuk Bot 24/7 dan Data Persisten

GitHub Actions dirancang untuk CI/CD (Continuous Integration/Continuous Deployment), bukan sebagai platform hosting bot 24/7 secara *persisten*. Beberapa batasan utama:

*   **Durasi Job:** Setiap job GitHub Actions memiliki batas waktu eksekusi (biasanya 6 jam). Bot Anda akan berhenti setelah waktu ini atau setelah proses `python bot.py` selesai.
*   **Stateless Runner:** Setiap kali workflow berjalan, ia dimulai dari awal di lingkungan yang bersih. Ini berarti database SQLite (`promo_tracker.db`) yang dibuat oleh bot Anda **tidak akan bertahan antar eksekusi workflow**. Setiap kali bot dijalankan ulang oleh GitHub Actions, ia akan memulai dengan database kosong, dan semua data pengguna (kata kunci, URL yang dilacak) akan hilang.
*   **Jadwal Tidak Tepat Waktu:** GitHub Actions `schedule` tidak menjamin eksekusi yang tepat waktu dan mungkin ada penundaan.

**Rekomendasi untuk Bot 24/7 dengan Data Persisten:**

Untuk bot yang benar-benar berjalan 24/7 dan mempertahankan state (seperti data pengguna dan promo), sangat disarankan untuk menggunakan Virtual Private Server (VPS) atau platform Platform-as-a-Service (PaaS) seperti Railway, Render, atau Google Cloud Run. Pada platform ini, Anda dapat menjalankan bot secara terus-menerus dan menggunakan database eksternal (seperti PostgreSQL, MySQL) atau menyimpan file SQLite di persistent storage.

### Workflow GitHub Actions (Periodic Run)

Jika Anda tetap ingin menggunakan GitHub Actions, Anda dapat menggunakannya untuk menjalankan bot secara berkala. Namun, ingat bahwa data akan hilang setiap kali job selesai.

Buat direktori `.github/workflows/` di root repositori Anda. Di dalamnya, buat file baru bernama `main.yml` (atau nama lain yang deskriptif) dengan konten berikut:

```yaml
name: Telegram Promo Bot Periodic Check

on:
  schedule:
    # Jalankan setiap 6 jam. Sesuaikan sesuai kebutuhan.
    # Format cron: menit (0-59) jam (0-23) hari-bulan (1-31) bulan (1-12) hari-minggu (0-6)
    - cron: '0 */6 * * *'
  workflow_dispatch: # Memungkinkan menjalankan workflow secara manual

jobs:
  run-bot-check:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.9' # Atau versi Python yang Anda gunakan

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run Bot (Periodic Check)
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      run: python bot.py
```

### Penjelasan Workflow (Periodic Run)

*   **`name`**: Nama workflow.
*   **`on`**: Memicu workflow ini pada:
    *   `schedule`: Menggunakan ekspresi cron untuk menjalankan bot secara berkala (contoh: setiap 6 jam). Bot akan melakukan pengecekan promo, mengirim notifikasi, dan kemudian berhenti.
    *   `workflow_dispatch`: Memungkinkan Anda untuk menjalankan workflow ini secara manual dari tab Actions di repositori GitHub Anda.
*   **`jobs`**: Mendefinisikan pekerjaan yang akan dijalankan.
    *   `run-bot-check`: Nama pekerjaan.
    *   `runs-on: ubuntu-latest`: Menjalankan pekerjaan di runner Ubuntu terbaru.
    *   **`steps`**:
        *   `Checkout repository`: Mengambil kode dari repositori Anda.
        *   `Set up Python`: Mengatur lingkungan Python.
        *   `Install dependencies`: Menginstal semua pustaka yang tercantum dalam `requirements.txt`.
        *   `Run Bot (Periodic Check)`: Menjalankan `bot.py`. `TELEGRAM_BOT_TOKEN` diambil dari GitHub Secrets yang telah Anda atur sebelumnya. **Penting:** Dalam mode ini, bot akan memulai, melakukan pengecekan promo, dan kemudian keluar. Database SQLite akan dibuat ulang setiap kali, sehingga data pengguna tidak akan disimpan.

## Pengembangan Lebih Lanjut

*   **Integrasi API Resmi:** Jika memungkinkan, gunakan API resmi dari Shopee atau TikTok Shop untuk mendapatkan data promo yang lebih akurat dan stabil.
*   **Web Scraping Lanjutan:** Jika API tidak tersedia, pertimbangkan untuk menggunakan pustaka seperti `BeautifulSoup` atau `Selenium` untuk *web scraping* yang lebih canggih, namun selalu perhatikan Syarat & Ketentuan platform.
*   **Filter Promo:** Tambahkan opsi filter promo berdasarkan kategori, harga, atau tanggal kedaluwarsa.
*   **UI Interaktif:** Kembangkan antarmuka pengguna yang lebih interaktif di Telegram menggunakan tombol inline atau keyboard kustom.
*   **Skalabilitas Database:** Untuk jumlah pengguna yang besar dan persistensi data, migrasi ke database yang lebih robust seperti PostgreSQL atau MySQL yang dihosting secara eksternal sangat disarankan.

---
