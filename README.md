# FuzzySched Diagnostics 🎓📊

> Sistem Inferensi Fuzzy Mamdani untuk mendiagnosis faktor penghambat efisiensi penjadwalan mata kuliah melalui analisis sensitivitas variabel input.

Repositori ini memuat *source code* dan data yang digunakan dalam penelitian skripsi berjudul:
**"PEMODELAN LOGIKA FUZZY TIPE MAMDANI UNTUK DIAGNOSIS FAKTOR PENGHAMBAT EFISIENSI PENJADWALAN MATA KULIAH MELALUI ANALISIS SENSITIVITAS VARIABEL INPUT"**
---
## 📖 Latar Belakang
Penjadwalan mata kuliah di perguruan tinggi seringkali menghadapi kendala kompleks akibat berbagai variabel yang saling tarik-menarik. Proyek ini bertujuan untuk membangun sebuah model diagnosis berbasis *Fuzzy Logic Mamdani* yang tidak hanya menghasilkan tingkat efisiensi penjadwalan, tetapi juga melakukan **Analisis Sensitivitas** untuk mengetahui secara pasti variabel input mana yang paling menjadi *bottleneck* (penghambat utama) dalam penyusunan jadwal.

## 📌 Fitur Utama
* **Pemodelan Fuzzy Mamdani:** Menggunakan basis aturan (*rule base*) yang diekstraksi dari pakar untuk memodelkan ketidakpastian dalam penjadwalan akademik.
* **Analisis Sensitivitas:** Mengukur dan menganalisis seberapa besar pengaruh setiap variabel input terhadap output efisiensi penjadwalan.
* **Sistem Diagnosis Otomatis:** Memberikan hasil evaluasi yang secara langsung mengidentifikasi faktor utama yang menghambat kelancaran penyusunan jadwal.
---
## 🔬 Metodologi & Variabel
Sistem ini dibangun menggunakan metode **Fuzzy Inference System (FIS) Mamdani** yang secara garis besar terdiri dari tahapan: Pembentukan Himpunan Fuzzy (Fuzzifikasi), Aplikasi Fungsi Implikasi, Komposisi Aturan, dan Defuzzifikasi (menggunakan metode *Centroid*).

### Variabel yang Dianalisis
* **Input:** Keterisian Ruang, Pelanggaran Batasan Akademik, Waktu Tunggu Mahasiswa. 
* **Output Utama:** Tingkat Efisiensi Penjadwalan (Tidak Efisien, Cukup Efisien, Efisien).
* **Output Diagnosis:** Identifikasi variabel input paling sensitif yang menyebabkan penurunan efisiensi.
---
## 🛠️ Teknologi yang Digunakan
* **Python 3.8+**
* `scikit-fuzzy` (Untuk pemodelan logika fuzzy)
* `numpy` (Untuk komputasi numerik)
* `pandas` (Untuk manipulasi dataset)
---
## ⚙️ Cara Menjalankan Program (Instalasi)

1. **Clone repositori ini:**
   ```bash
   git clone [https://github.com/](https://github.com/)[username-github-kamu]/fuzzysched-diagnostics.git
   cd fuzzysched-diagnostics

2. **Buat Virtual Environment (Opsional tapi disarankan):**
   ```bash
   python -m venv env
   
   # Untuk pengguna Windows:
   env\Scripts\activate
   
   # Untuk pengguna Mac/Linux:
   source env/bin/activate
3. **Install dependensi yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
4. **Jalankan program utama:**
   Pastikan dataset input penjadwalan sudah tersedia di dalam direktori `data/`, kemudian eksekusi perintah berikut di terminal:
   ```bash
   python main.py

## 📂 Struktur Direktori

```text
fuzzysched-diagnostics/
├── dataset/                          # Folder untuk menyimpan file dataset penjadwalan
├── output/                           # Folder penyimpanan hasil evaluasi dan plot grafik
├── agregasi.py                       # Modul untuk proses agregasi data menjadi variabel input
├── main_cli.py                       # File utama untuk menjalankan sistem melalui Command Line
├── main.ipynb                        # Jupyter Notebook untuk eksperimen dan pengujian interaktif
├── sistem_fuzzy.py                   # Modul inti sistem inferensi Logika Fuzzy Mamdani
├── validasi.py                       # Skrip untuk proses validasi dan pengujian model
└── visualisasi.py                    # Modul umum untuk menampilkan plot dan grafik
```
## 👤 Penulis

**Alya Azzahra**
* **NIM:** 22106050008
* **Program Studi:** [Nama Program Studi, misal: Teknik Informatika / Ilmu Komputer]
* **Fakultas:** [Nama Fakultas, misal: Fakultas Sains dan Teknologi]
* **Universitas:** [Nama Universitas]

*Repositori ini dibuat sebagai bagian dari penelitian Skripsi untuk memenuhi syarat kelulusan jenjang Strata-1 (S1).*

---
*Jika ada pertanyaan atau saran terkait sistem FuzzySched Diagnostics ini, silakan hubungi melalui [Alamat Email Kamu] atau buat _issue_ di repositori ini.*
