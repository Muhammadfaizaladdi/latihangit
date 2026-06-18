0. ENV Variables
```python
PLAN_PRICES = {
    "Basic Plan":    120_000,
    "Standard Plan": 160_000,
    "Premium Plan":  200_000,
}

PLAN_TABLE = [
    [True,  True,  True,  "Bisa Stream"],
    [True,  True,  True,  "Bisa Download"],
    [True,  True,  True,  "Kualitas SD"],
    [False, True,  True,  "Kualitas HD"],
    [False, False, True,  "Kualitas UHD"],
    [1,     2,     4,     "Jumlah Device"],
    [
        "3rd party Movie only",
        "Basic Plan Content + Sports",
        "Basic Plan + Standard Plan + PacFlix Original Series",
        "Jenis Konten",
    ],
    [120_000, 160_000, 200_000, "Harga (Rp)"],
]

PLAN_HEADERS = ["Basic Plan", "Standard Plan", "Premium Plan", "Services"]

TIER_PARAMETERS = {
    "Platinum": [8, 15],
    "Gold":     [6, 10],
    "Silver":   [5, 7],
}

TIER_DISCOUNT = {
    "Platinum": 0.15,
    "Gold":     0.10,
    "Silver":   0.08,
}

BENEFIT_TABLE = [
    ["Platinum", "15%", "Benefit Gold + Silver + Cashback max. 30%"],
    ["Gold",     "10%", "Benefit Silver + Voucher Ojek Online"],
    ["Silver",   "8%",  "Voucher Makanan"],
]
BENEFIT_HEADERS = ["Membership", "Discount", "Another Benefit"]

REQUIREMENT_TABLE = [
    ["Platinum", 8, 15],
    ["Gold",     6, 10],
    ["Silver",   5, 7],
]
REQUIREMENT_HEADERS = ["Membership", "Monthly Expense (juta)", "Monthly Income (juta)"]
```

1. Struktur Proyek

Proyek dipisah berdasarkan **tipe tanggung jawab** di level atas (`models/`, `data/`), lalu di dalam masing-masing dipecah lagi berdasarkan **domain layanan** (`streaming/`, `commerce/`):

```
pacflix/
│
├── main.py                        ← Program utama (entry point)
│
├── models/
│   ├── __init__.py
│   ├── streaming/
│   │   ├── __init__.py
│   │   ├── user.py                ← Class User (pelanggan terdaftar)
│   │   └── new_user.py            ← Class NewUser (calon pelanggan)
│   └── commerce/
│       ├── __init__.py
│       └── membership.py          ← Class Membership (PacCommerce)
│
└── data/
    ├── __init__.py
    ├── streaming/
    │   ├── __init__.py
    │   └── data.py                ← Data pelanggan streaming (simulasi database)
    └── commerce/
        ├── __init__.py
        └── membership_data.py     ← Data tier membership per username
```

Prinsip pemisahan:

| Folder/File | Tanggung Jawab |
|---|---|
| `data/streaming/data.py` | Menyimpan data pelanggan streaming — tidak ada logika bisnis |
| `data/commerce/membership_data.py` | Menyimpan data tier membership — tidak ada logika bisnis |
| `models/streaming/user.py` | Logika untuk pengguna streaming yang sudah berlangganan |
| `models/streaming/new_user.py` | Logika untuk pendaftaran pengguna streaming baru |
| `models/commerce/membership.py` | Logika membership PacCommerce (benefit, requirement, prediksi, harga) |
| `main.py` | Login, dashboard, menampilkan menu, membaca input, memanggil class |

Mengapa dipisah per-tipe (`models/`, `data/`) bukan per-domain (`streaming/`, `commerce/`) di level atas:

- Memudahkan kalau perlu lihat "semua model" atau "semua sumber data" sekaligus, tanpa harus masuk ke folder domain satu-satu.
- Tetap konsisten: satu username dipakai untuk login ke seluruh layanan (streaming & belanja), sehingga kedua domain memang dirancang untuk hidup berdampingan dalam satu aplikasi, bukan dipisah jadi project sendiri-sendiri.
- Modul `streaming/` dan `commerce/` di dalam `models/` maupun `data/` tetap **tidak saling import** satu sama lain — keduanya hanya dipanggil dari `main.py`.

2. Perbaikan Penulisan Class

Perubahan pada `User` (`models/streaming/user.py`)

| Sebelum | Sesudah | Alasan |
|---|---|---|
| `check_plan(self, username)` menerima parameter `username` tapi tidak dipakai | `check_plan(self)` tanpa parameter | Parameter yang tidak terpakai menimbulkan kebingungan |
| `try/except` menangkap semua exception lalu mencetak `"aaaa"` | Validasi eksplisit dengan `raise ValueError` dan pesan jelas | Error message "aaaa" tidak informatif; lebih baik beri tahu persis apa yang salah |
| Kondisi `if new_plan != self.current_plan` di `upgrade_plan` tidak menampilkan error jika sama | Raise `ValueError` dengan pesan yang jelas | Pengguna perlu tahu kenapa upgrade gagal |
| Harga plan ditulis berulang di beberapa tempat | Dipusatkan di dictionary `PLAN_PRICES` | Perubahan harga cukup di satu tempat (DRY principle) |
| Tidak ada type hints | Semua method memiliki type hints | Lebih mudah dibaca dan didebug |
| Tidak ada docstring | Setiap method memiliki docstring | Dokumentasi kode lebih baik |

Perubahan pada `NewUser` (`models/streaming/new_user.py`)

| Sebelum | Sesudah | Alasan |
|---|---|---|
| `check_list = []` sebagai class variable | `self._referrals` sebagai instance variable (set) | Class variable berbagi state antar semua instance; set lebih efisien untuk lookup `in` |
| `convert_data_to_list` dipanggil manual oleh pemanggil | `_load_referral_codes` dipanggil otomatis di `__init__` | Pengguna class tidak perlu tahu detail implementasi internal |
| Looping manual untuk mengumpulkan referral | Menggunakan set comprehension | Lebih ringkas dan efisien; `O(1)` lookup vs `O(n)` pada list |
| `raise Exception("Referral Code doesn't exist")` | `raise ValueError(...)` dengan pesan berbahasa Indonesia | `ValueError` lebih semantik; pesan error konsisten dengan bahasa aplikasi |

Perubahan pada `Membership` (`models/commerce/membership.py`)

| Sebelum | Sesudah | Alasan |
|---|---|---|
| `data` sebagai class variable di dalam class | Dipindah ke `data/commerce/membership_data.py` sebagai `membership_data` | Konsisten dengan pola `User`/`NewUser`; class variable berisiko *shared state* antar instance |
| `show_membership(self, username)` menerima parameter `username` padahal sudah ada `self.username` | `show_membership(self)` tanpa parameter | `self.username` sudah cukup; parameter ekstra membingungkan |
| `calculate_price` membungkus semuanya dalam `try/except` generik yang berakhir `raise Exception("Invalid process")` | Validasi eksplisit dengan `raise ValueError(...)` dan pesan jelas | Pesan generik tidak membantu debugging; pengguna perlu tahu persis kenapa proses gagal |
| Magic number (`0.15`, `0.10`, `0.08`) ditulis langsung di `if/elif` | Dipusatkan di dictionary `TIER_DISCOUNT` | Perubahan persentase diskon cukup di satu tempat |
| Parameter acuan tier (`[8,15]`, `[6,10]`, `[5,7]`) ditulis ulang di `show_requirements` dan `predict_membership` | Dipusatkan di `TIER_PARAMETERS`, dipakai ulang di kedua method | DRY — hindari duplikasi data yang sama |
| `predict_membership` looping manual dengan `enumerate` lalu bandingkan ke `min(res)` | Pakai `min(distances, key=distances.get)` | Lebih ringkas dan jelas maksudnya: ambil tier dengan jarak terkecil |

3. Flowchart Aplikasi

```
                         ┌──────────────────┐
                         │   Jalankan app    │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Login (1x)      │
                         │  Input username   │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │     Dashboard      │
                         │ 1.Streaming        │
                         │ 2.Belanja          │
                         │ 3.Logout           │
                         └──┬───────────┬─────┘
                            │           │
                ┌───────────▼──┐   ┌────▼────────────┐
                │  STREAMING    │   │    BELANJA       │
                │ Sudah ada di  │   │ Cek membership   │
                │ data/streaming│   │ di data/commerce/│
                │ /data.py?     │   │ membership_data? │
                └──┬─────────┬──┘   └──┬───────────┬───┘
              Ya   │         │ Tidak Ya │           │ Tidak
        ┌──────────▼──┐  ┌───▼─────┐  │      ┌─────▼──────────┐
        │ Menu User:   │  │Tawarkan │  │      │ Pesan: belum   │
        │1.Lihat plan  │  │daftar   │  │      │ punya membership│
        │2.Detail plan │  │baru?    │  │      │ → opsi prediksi │
        │3.Upgrade plan│  └─────────┘  │      └────────┬────────┘
        │4.Kembali     │               │               │
        └──────┬───────┘               │      ┌────────▼────────┐
               │                       │      │ Input expense &  │
               │              ┌────────▼──┐   │ income           │
               │              │ Menu       │   │ → Euclidean      │
               │              │ Membership:│   │   Distance        │
               │              │1.Benefit   │   │ → simpan tier     │
               │              │2.Requirement│  └───────────────────┘
               │              │3.Hitung    │
               │              │  belanja   │
               │              │4.Kembali   │
               │              └────────────┘
               │                       │
               └───────────┬───────────┘
                            │
                  kembali ke Dashboard
                  (tanpa login ulang)
```

Poin penting alur:

- Login hanya **sekali**, lalu pengguna bisa bolak-balik antara modul Streaming dan Belanja melalui Dashboard tanpa mengulang login.
- Modul Streaming mengecek dulu apakah `username` ada di `data/streaming/data.py`; jika tidak, ditawarkan pendaftaran plan baru (pakai `NewUser` + kode referral).
- Modul Belanja mengecek dulu apakah `username` ada di `data/commerce/membership_data.py`; jika tidak, pengguna diberi pesan dan opsi submenu untuk memprediksi tier baru berdasarkan pengeluaran & pemasukan bulanan.

4. Cara Menjalankan

Prasyarat
```
pip install tabulate
```

Jalankan Aplikasi
```
cd pacflix
python main.py
```

Contoh Sesi
```
==================================================
     Selamat datang di PacFlix & PacCommerce     
==================================================
Masukkan username Anda: alice123

=== Dashboard — alice123 ===
  1. Streaming (PacFlix)
  2. Belanja (PacCommerce)
  3. Logout

Masukkan pilihan (1-3): 1

[Streaming] Halo, alice123! Pilih menu:
  1. Lihat semua plan PacFlix
  2. Lihat detail plan aktif saya
  3. Upgrade plan
  4. Kembali ke dashboard

Masukkan pilihan (1-4): 3

Plan yang tersedia:
  a. Basic Plan    — Rp 120.000
  b. Standard Plan — Rp 160.000
  c. Premium Plan  — Rp 200.000
Pilih plan tujuan (a/b/c): c
[!] Anda sudah berlangganan Premium Plan.

Masukkan pilihan (1-4): 4

=== Dashboard — alice123 ===
  1. Streaming (PacFlix)
  2. Belanja (PacCommerce)
  3. Logout

Masukkan pilihan (1-3): 2

[Belanja] Halo, alice123! Membership Anda: Gold
  1. Lihat benefit semua membership
  2. Lihat requirements semua membership
  3. Hitung total belanja (dengan diskon membership)
  4. Kembali ke dashboard

Masukkan pilihan (1-4): 3
Masukkan harga barang, pisahkan dengan koma (contoh: 50000,120000): 50000,120000
--------------------------------------------------
Total belanja setelah diskon Gold: Rp 153.000
--------------------------------------------------
```

Contoh Sesi — Pengguna Baru (belum punya akun streaming)
```
Masukkan username Anda: budi123

=== Dashboard — budi123 ===
  1. Streaming (PacFlix)
  2. Belanja (PacCommerce)
  3. Logout

Masukkan pilihan (1-3): 1

[!] budi123 belum berlangganan PacFlix.
Daftar plan baru sekarang? (y/n): y

Plan yang tersedia:
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

Contoh Sesi — Belum Punya Membership
```
Masukkan username Anda: diana_w

=== Dashboard — diana_w ===
  1. Streaming (PacFlix)
  2. Belanja (PacCommerce)
  3. Logout

Masukkan pilihan (1-3): 2

[!] diana_w belum memiliki membership PacCommerce.
  1. Prediksi membership sekarang
  2. Kembali ke dashboard

Masukkan pilihan (1-2): 1

Belum ada data membership. Mari prediksi tier Anda.
Rata-rata pengeluaran bulanan (dalam juta): 7
Rata-rata pemasukan bulanan (dalam juta): 9

Hasil perhitungan Euclidean Distance untuk diana_w: {'Platinum': 6.08, 'Gold': 1.41, 'Silver': 2.83}
--------------------------------------------------
Membership yang direkomendasikan untuk Anda: Gold
--------------------------------------------------
```

Username & Kode Referral untuk Uji Coba (Streaming)

| Username | Plan | Durasi | Kode Referral |
|---|---|---|---|
| alice123 | Basic Plan | 12 bln | alice-ref |
| bob_jones | Standard Plan | 8 bln | bob-ref |
| charlie99 | Premium Plan | 15 bln | charlie-ref |
| diana_w | Basic Plan | 3 bln | diana-ref |
| evan_m | Standard Plan | 20 bln | evan-ref |

Username & Tier untuk Uji Coba (Membership)

| Username | Tier |
|---|---|
| alice123 | Gold |
| bob_jones | Silver |
| charlie99 | Platinum |

> `diana_w` dan `evan_m` ada di data streaming tapi **belum** di data membership — cocok untuk menguji skenario prediksi membership baru.
