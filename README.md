# 🎧 TemanBelajar — Web Player Musik Pengiring Belajar

Aplikasi web sederhana berbasis **Streamlit** untuk memutar musik pengiring
sambil belajar, dilengkapi timer belajar (Pomodoro) dan pencatat riwayat sesi belajar.

---

## 1. Konsep

Banyak orang belajar lebih fokus sambil mendengarkan musik instrumental,
lo-fi, atau suara alam. **TemanBelajar** menggabungkan tiga hal dalam satu
halaman web:

1. **Pemutar musik** — memutar musik dari YouTube (embed resmi), file audio
   yang diunggah sendiri, atau URL audio langsung.
2. **Timer belajar (Pomodoro)** — countdown yang berjalan mulus di browser
   (JavaScript), lengkap dengan alarm bunyi saat waktu habis.
3. **Riwayat belajar** — mencatat setiap sesi belajar (tanggal, durasi,
   catatan) agar progres belajar bisa dipantau dari waktu ke waktu.

### Kenapa tidak ada lagu berhak cipta langsung di dalam kode?

Kode ini **tidak menyertakan file musik berhak cipta** secara langsung.
Sebagai gantinya, pemutar didesain fleksibel — pengguna bebas memilih sumber:

| Sumber | Cocok untuk |
|---|---|
| Link YouTube | Musik lo-fi/instrumental yang memang untuk didengarkan publik lewat embed resmi YouTube |
| Upload file audio (mp3/wav) | Musik koleksi pribadi pengguna |
| URL audio langsung | Musik bebas royalti dari sumber lain |

---

## 2. Struktur Proyek

```
belajar-lagu/
├── app.py                  # Aplikasi utama Streamlit
├── requirements.txt        # Daftar dependensi
├── README.md                # Dokumentasi ini
└── data/
    ├── playlist.json        # Database playlist (otomatis dibuat)
    ├── study_log.json       # Riwayat sesi belajar (otomatis dibuat)
    └── uploads/              # Folder penyimpanan file audio yang diupload
```

---

## 3. Fitur & Halaman

### 🏠 Beranda
- Memilih & memutar musik dari playlist
- Timer belajar di sisi kanan, berjalan independen dari pemutar musik
- Bisa mencatat sesi belajar langsung setelah timer selesai

### 📻 Playlist Saya
- Menampilkan semua musik yang tersimpan, dikelompokkan per kategori
  (Lo-fi, Piano, Suara Alam, Instrumental, Lainnya)
- Tombol untuk memutar atau menghapus musik dari playlist

### ➕ Tambah Musik
- Formulir menambahkan musik baru ke playlist:
  - Tempel link YouTube (ID video diambil otomatis)
  - Upload file audio dari komputer
  - Tempel URL audio langsung (.mp3/.wav)

### 📊 Riwayat Belajar
- Menampilkan total waktu belajar yang tercatat
- Daftar riwayat sesi (tanggal, durasi, catatan)
- Opsi menghapus seluruh riwayat

---

## 4. Cara Menjalankan

1. Pastikan Python 3.9+ sudah terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```
4. Browser akan otomatis terbuka di `http://localhost:8501`.

---

## 5. Cara Kerja Teknis Singkat

- **Penyimpanan data**: menggunakan file JSON lokal (`playlist.json`,
  `study_log.json`) agar data tetap ada meski aplikasi ditutup dan dibuka
  kembali — tidak perlu database eksternal.
- **Pemutar YouTube**: memakai `streamlit.components.v1.iframe` untuk
  menyematkan video YouTube resmi berdasarkan ID video yang diekstrak dari URL.
- **Pemutar audio lokal/URL**: memakai `st.audio()` bawaan Streamlit.
- **Timer belajar**: dibuat dengan HTML + JavaScript murni yang disematkan
  lewat `components.html()`, sehingga hitungan mundur berjalan di browser
  tanpa perlu Streamlit terus-menerus me-refresh halaman. Bunyi alarm
  dibangkitkan dengan Web Audio API (osilator nada), bukan file suara.
- **Session state**: `st.session_state` dipakai untuk menyimpan playlist,
  riwayat, dan lagu yang sedang diputar selama sesi berjalan, lalu disinkronkan
  ke file JSON setiap ada perubahan.

---

## 6. Pengembangan Lanjutan (Opsional)

Beberapa ide jika ingin dikembangkan lebih lanjut:
- Menambahkan mode "shuffle" atau "putar otomatis lagu berikutnya"
- Grafik riwayat belajar mingguan/bulanan (misalnya dengan `st.bar_chart`)
- Login sederhana agar setiap pengguna punya playlist & riwayat sendiri
- Rekomendasi musik otomatis berdasarkan kategori yang paling sering diputar
