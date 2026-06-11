# Dokumentasi PacFlix — Terminal App

Panduan lengkap mengubah kode class PacFlix menjadi aplikasi sederhana yang bisa dijalankan lewat terminal.

---

## Daftar Isi

1. [Struktur Proyek](#1-struktur-proyek)
2. [Perbaikan Penulisan Class](#2-perbaikan-penulisan-class)
3. [Flowchart Aplikasi](#3-flowchart-aplikasi)
4. [Cara Menjalankan](#4-cara-menjalankan)

---

## 1. Struktur Proyek

Proyek dipisah menjadi tiga lapisan agar mudah dikembangkan:

```
pacflix/
│
├── main.py               ← Program utama (entry point)
│
├── models/
│   ├── __init__.py
│   ├── user.py           ← Class User (pelanggan terdaftar)
│   └── new_user.py       ← Class NewUser (calon pelanggan)
│
└── data/
    ├── __init__.py
    └── data.py           ← Data pengguna (simulasi database)
```

**Prinsip pemisahan:**

| File | Tanggung Jawab |
|---|---|
| `data/data.py` | Menyimpan data — tidak ada logika bisnis |
| `models/user.py` | Logika untuk pengguna yang sudah berlangganan |
| `models/new_user.py` | Logika untuk pendaftaran pengguna baru |
| `main.py` | Menampilkan menu, membaca input, memanggil class |

---

## 2. Perbaikan Penulisan Class

### Perubahan pada `User`

| Sebelum | Sesudah | Alasan |
|---|---|---|
| `check_plan(self, username)` menerima parameter `username` tapi tidak dipakai | `check_plan(self)` tanpa parameter | Parameter yang tidak terpakai menimbulkan kebingungan |
| `try/except` menangkap semua exception lalu mencetak `"aaaa"` | Validasi eksplisit dengan `raise ValueError` dan pesan jelas | Error message "aaaa" tidak informatif; lebih baik beri tahu persis apa yang salah |
| Kondisi `if new_plan != self.current_plan` di `upgrade_plan` tidak menampilkan error jika sama | Raise `ValueError` dengan pesan yang jelas | Pengguna perlu tahu kenapa upgrade gagal |
| Harga plan ditulis berulang di beberapa tempat | Dipusatkan di dictionary `PLAN_PRICES` | Perubahan harga cukup di satu tempat (DRY principle) |
| Tidak ada type hints | Semua method memiliki type hints | Lebih mudah dibaca dan didebug |
| Tidak ada docstring | Setiap method memiliki docstring | Dokumentasi kode lebih baik |

### Perubahan pada `NewUser`

| Sebelum | Sesudah | Alasan |
|---|---|---|
| `check_list = []` sebagai class variable | `self._referrals` sebagai instance variable (set) | Class variable berbagi state antar semua instance; set lebih efisien untuk lookup `in` |
| `convert_data_to_list` dipanggil manual oleh pemanggil | `_load_referral_codes` dipanggil otomatis di `__init__` | Pengguna class tidak perlu tahu detail implementasi internal |
| Looping manual untuk mengumpulkan referral | Menggunakan set comprehension | Lebih ringkas dan efisien; `O(1)` lookup vs `O(n)` pada list |
| `raise Exception("Referral Code doesn't exist")` | `raise ValueError(...)` dengan pesan berbahasa Indonesia | `ValueError` lebih semantik; pesan error konsisten dengan bahasa aplikasi |

---

## 3. Flowchart Aplikasi

```
                    ┌─────────────────────┐
                    │   Jalankan main.py  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Tampilkan Menu   │
                    │       Utama         │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
    │  [1] Login  │    │  [2] Daftar  │    │  [3] Keluar  │
    │  Pengguna   │    │  Pengguna    │    └──────────────┘
    │  Terdaftar  │    │     Baru     │
    └──────┬──────┘    └───────┬──────┘
           │                   │
    ┌──────▼──────┐    ┌───────▼──────┐
    │  Input      │    │  Input       │
    │  Username   │    │  Username    │
    └──────┬──────┘    └───────┬──────┘
           │                   │
    ┌──────▼──────┐    ┌───────▼──────┐
    │  Cek di     │    │  Pilih Plan  │
    │  data.py?   │    │  (a/b/c)     │
    └──────┬──────┘    └───────┬──────┘
           │                   │
       ┌───▼───┐        ┌──────▼──────┐
       │ Ada?  │        │  Input Kode │
       └───┬───┘        │  Referral   │
     Ya │  │ Tidak      └──────┬──────┘
        │  └──► Pesan Error    │
        │                  ┌───▼───┐
        │                  │Valid? │
        │                  └───┬───┘
        │            Ya  ───┘  │ Tidak
        │            │         └──► Pesan Error
        │     ┌──────▼──────┐
        │     │ Hitung harga│
        │     │ - diskon 4% │
        │     │ Tampilkan   │
        │     └─────────────┘
        │
   ┌────▼──────────────────────┐
   │  Buat objek User(...)     │
   │  Tampilkan Menu User      │
   └────┬──────────────────────┘
        │
   ┌────▼────┬──────────────┬────────────────┐
   │[1] Lihat│ [2] Lihat    │ [3] Upgrade    │
   │Semua    │ Plan Aktif   │ Plan           │
   │Plan     │ Saya         │                │
   └────┬────┴──────┬───────┴────┬───────────┘
        │           │            │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────────────┐
   │Tabel    │ │Detail   │ │ Input plan baru │
   │Semua    │ │plan user│ │                 │
   │Plan     │ │ini saja │ │ Durasi > 12 bln?│
   └─────────┘ └─────────┘ │  Ya  → diskon 5%│
                            │  Tidak → harga  │
                            │         normal  │
                            └─────────────────┘
```

---

## 4. Cara Menjalankan

### Prasyarat

```bash
pip install tabulate
```

### Jalankan Aplikasi

```bash
cd pacflix
python main.py
```

### Contoh Sesi

```
==================================================
         Selamat datang di PacFlix!
==================================================

Menu Utama:
  1. Login sebagai pengguna terdaftar
  2. Daftar sebagai pengguna baru
  3. Keluar

Masukkan pilihan (1-3): 1
Masukkan username: charlie99

Halo, charlie99! Pilih menu:
  1. Lihat semua plan PacFlix
  2. Lihat detail plan aktif saya
  3. Upgrade plan
  4. Kembali ke menu utama

Masukkan pilihan (1-4): 3

Plan yang tersedia:
  a. Basic Plan    — Rp 120.000
  b. Standard Plan — Rp 160.000
  c. Premium Plan  — Rp 200.000
Pilih plan tujuan (a/b/c): c
[!] Anda sudah berlangganan Premium Plan.
```

```
Masukkan pilihan (1-3): 2
Masukkan username baru Anda: budi123

Pilih plan berlangganan:
  a. Basic Plan    — Rp 120.000
  b. Standard Plan — Rp 160.000
  c. Premium Plan  — Rp 200.000
Pilih plan (a/b/c): b
Masukkan kode referral: alice-ref

Kode referral valid! Diskon 4% diterapkan.
--------------------------------------------------
Harga Standard Plan untuk budi123: Rp 153.600
--------------------------------------------------
```

### Username & Kode Referral untuk Uji Coba

| Username | Plan | Durasi | Kode Referral |
|---|---|---|---|
| `alice123` | Basic Plan | 12 bln | `alice-ref` |
| `bob_jones` | Standard Plan | 8 bln | `bob-ref` |
| `charlie99` | Premium Plan | 15 bln | `charlie-ref` |
| `diana_w` | Basic Plan | 3 bln | `diana-ref` |
| `evan_m` | Standard Plan | 20 bln | `evan-ref` |
