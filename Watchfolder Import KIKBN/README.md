# Folder Monitor - Fitur Pemantauan dan Pencatatan File

Folder Monitor adalah sebuah skrip Python yang digunakan untuk memantau folder-folder tertentu dan memberikan notifikasi desktop ketika ada file baru yang masuk atau file yang sudah ada dimodifikasi. Selain itu, skrip ini juga mencatat riwayat (history) dari aktivitas pemantauan tersebut dalam bentuk file JSON.

## Fitur-fitur

1. **Pemantauan Folder**
   - Memantau folder-folder yang telah dikonfigurasi secara berkala (default: setiap 60 detik).
   - Mendeteksi file baru yang masuk ke dalam folder.
   - Mendeteksi file yang sudah ada yang mengalami modifikasi.

2. **Notifikasi Desktop**
   - Mengirimkan notifikasi desktop ketika ada file baru yang masuk.
   - Mengirimkan notifikasi desktop ketika ada file yang dimodifikasi.
   - Notifikasi menampilkan informasi singkat seperti nama file dan folder terkait.

3. **Pencatatan Riwayat (Record/History)**
   - Mencatat setiap kejadian file baru masuk atau file dimodifikasi ke dalam file JSON (`monitor_record.json`).
   - Format pencatatan berupa tabel JSON dengan kolom:
     - `no`: Nomor urut pencatatan.
     - `file name`: Nama file yang terpantau.
     - `date`: Tanggal dan waktu kejadian.
     - `file path`: Lokasi lengkap file.
     - `keterangan`: Keterangan kejadian (misal: "invoice masuk" atau "modifikasi file").
   - File JSON ini dapat digunakan untuk audit atau pelacakan aktivitas file.

## Konfigurasi

- **Folder yang Dipantau**
  - Atur daftar folder yang ingin dipantau pada variabel `MONITORED_PATHS` di dalam skrip `folder_monitor.py`.
  
- **Interval Pemantauan**
  - Interval waktu pengecekan folder dapat diatur pada variabel `CHECK_INTERVAL_SECONDS` (default 60 detik).

- **Notifikasi**
  - Nama aplikasi yang muncul di notifikasi dapat diatur pada variabel `APP_NAME`.
  - Ikon notifikasi dapat diatur pada variabel `NOTIFICATION_ICON` (gunakan file .ico untuk Windows).

- **File Pencatatan**
  - File JSON untuk menyimpan riwayat pencatatan adalah `monitor_record.json` yang berada di direktori yang sama dengan skrip.

## Cara Penggunaan

1. Pastikan Python sudah terinstall di sistem Anda.
2. Install pustaka `plyer` untuk notifikasi desktop:
   ```
   pip install plyer
   ```
3. Jalankan skrip `folder_monitor.py`:
   ```
   python folder_monitor.py
   ```
4. Skrip akan mulai memantau folder yang sudah dikonfigurasi dan menampilkan notifikasi serta mencatat riwayat ke file JSON.

## Catatan

- Jika file `monitor_record.json` kosong atau rusak, skrip akan menginisialisasi ulang file tersebut dengan array kosong.
- Pastikan folder yang dipantau memiliki izin akses yang memadai agar skrip dapat membaca file dan folder di dalamnya.

---

Dokumentasi ini dapat digunakan sebagai panduan untuk memahami dan menggunakan fitur-fitur yang tersedia pada Folder Monitor.
