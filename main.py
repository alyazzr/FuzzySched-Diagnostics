# %% [markdown]
# # Import Library

# %%
import pandas as pd
import numpy as np
from sistem_fuzzy import FuzzyMamdani
from agregasi import Agregasi
from validasi import analisis_sensitivitas, rekomendasi, hitung_mape, interpretasi_mape

# %%
import importlib
import sys

if 'agregasi' in sys.modules:
    importlib.reload(sys.modules['agregasi'])
    
from agregasi import Agregasi

# %%
PRODI_LIST = [
    'S1 Teknik Industri',
    'Arsitektur',
    'S1 Informatika',
    'S2 Teknik Industri',
    'S2 Informatika',
    'Matematika',
    'Fisika',
    'Kimia',
    'Biologi',
    'Sains Biomedis'    
    ]

FILE_RUANG = 'dataset/ruang.csv'
FILE_PAKAR = 'dataset/penilaian_pakar.csv'

print("="*80)
print("SISTEM DIAGNOSIS PENJADWALAN - FAKULTAS SAINS DAN TEKNOLOGI")
print("UIN Sunan Kalijaga Yogyakarta")
print("="*80)

# %%
def standarisasi_kolom(df):
    """Standarisasi nama kolom"""
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    mapping = {
        'kode_ruang': 'kode_ruang',
        'max_peserta': 'jumlah_peserta',
        'kelas_paralel': 'kelas',
        'kode_mata_kuliah': 'kode_mk',
        'kapasitas': 'kapasitas',
        'hari': 'hari',
        'jam_mulai': 'jam_mulai',
        'jam_selesai': 'jam_selesai',
        'dosen_pengampu': 'dosen',
        'nip_dosen': 'nip_dosen',
        'dosen': 'dosen',
        'mata_kuliah': 'mata_kuliah',
        'sks': 'sks',
    }
    
    df.rename(columns=mapping, inplace=True)
    return df

# %%
def baca_jadwal(prodi):
    """Baca file jadwal untuk satu prodi"""
    filename = f'dataset/jadwal/jadwal_{prodi.lower().replace(" ", "_")}.csv'

    try:
        df = pd.read_csv(
            filename,
            sep=';',
            engine='python',
            on_bad_lines='skip'
        )
        df = standarisasi_kolom(df)
        df['prodi'] = prodi
        return df

    except FileNotFoundError:
        print(f"⚠ File tidak ditemukan: {filename}")
        return None

    except Exception as e:
        print(f"⚠ Error membaca {filename}: {e}")
        return None


# %%
print("\n[TAHAP 1] MEMBACA DATA")
print("-" * 80)

try:
    df_ruang = pd.read_csv(
        FILE_RUANG,
        sep=";",
        engine="python",
    )
    df_ruang = standarisasi_kolom(df_ruang)
    print(f"✓ Data ruang: {len(df_ruang)} ruangan")

except Exception as e:
    print(f"✗ Error membaca {FILE_RUANG}: {e}")
    exit()


# %%
data_jadwal = {}
for prodi in PRODI_LIST:
    df = baca_jadwal(prodi)
    if df is not None:
        data_jadwal[prodi] = df
        print(f"✓ {prodi}: {len(df)} jadwal")

if len(data_jadwal) == 0:
    print("\n✗ Tidak ada data jadwal yang berhasil dibaca")
    exit()


# %%
df_pakar = pd.read_csv(
    FILE_PAKAR,
    sep=";",        
    engine="python"
)
df_pakar = standarisasi_kolom(df_pakar)
print(f"✓ Penilaian pakar: {len(df_pakar)} prodi")

# %%
print("\n[TAHAP 2] AGREGASI VARIABEL (8 Indikator → 3 Variabel)")
print("-" * 80)

agregator = Agregasi()
hasil_agregasi = []

for prodi, df_jadwal in data_jadwal.items():
    print(f"\n{prodi}:")
    
    # Hitung X1, X2, X3
    hasil = agregator.proses(df_jadwal, df_ruang)
    
    print(f"  X1 (Keterisian Ruang)  : {hasil['X1']:.2f}%")
    print(f"  X2 (Pelanggaran Batasan Akademik) : {hasil['X2']:.2f}%")
    print(f"  X3 (Waktu Tunggu Mahasiswa)   : {hasil['X3']:.2f}%")
    
    hasil_agregasi.append({
        'Prodi': prodi,
        'X1': hasil['X1'],
        'X2': hasil['X2'],
        'X3': hasil['X3']
    })

df_agregasi = pd.DataFrame(hasil_agregasi)
df_agregasi.to_csv('hasil_agregasi.csv', index=False)
print(f"\n✓ Hasil agregasi disimpan: hasil_agregasi.csv")

# %%
print("\n[TAHAP 3] INFERENSI FUZZY MAMDANI")
print("-" * 80)

fuzzy = FuzzyMamdani()

hasil_fuzzy = []
for _, row in df_agregasi.iterrows():
    # Pastikan nama objeknya 'fuzzy' dan methodnya 'inferensi'
    y = fuzzy.inferensi(row['X1'], row['X2'], row['X3'])
    
    hasil_fuzzy.append({
        'Prodi': row['Prodi'], 
        'Y_Fuzzy': round(y, 2), 
        'Interpretasi': fuzzy.interpretasi(y)
    })

df_fuzzy = pd.DataFrame(hasil_fuzzy)
nama_file_excel = "Hasil_Inferensi_Fuzzy_Mamdani.xlsx"
df_fuzzy.to_excel(nama_file_excel, index=False)
print(df_fuzzy.head())

# %%
if df_pakar is not None:
    print("\n[TAHAP 4] VALIDASI MODEL")
    print("-" * 80)
    
    # Merge dengan data pakar
    df_hasil = df_agregasi.merge(df_fuzzy, on='Prodi')
    df_hasil = df_hasil.merge(df_pakar[['prodi', 'skor_pakar']], 
                               left_on='Prodi', right_on='prodi', how='left')
    df_hasil.rename(columns={'skor_pakar': 'Y_Pakar'}, inplace=True)
    df_hasil.drop('prodi', axis=1, inplace=True)
    
    # Hitung MAPE
    if not df_hasil['Y_Pakar'].isna().all():
        df_hasil['Selisih'] = abs(df_hasil['Y_Fuzzy'] - df_hasil['Y_Pakar'])
        df_hasil['PE'] = (df_hasil['Selisih'] / df_hasil['Y_Pakar']) * 100

        mape = df_hasil['PE'].mean()
        status = interpretasi_mape(mape)
        print(f"\nMean Absolute Percentage Error (MAPE): {mape:.2f}%")
        print(f"Status Model: {status}")
        
    else:
        print("\n⚠ Data skor pakar tidak lengkap, MAPE tidak dapat dihitung")
        mape = None
else:
    df_hasil = df_agregasi.merge(df_fuzzy, on='Prodi')
    mape = None
    print("\n⚠ Validasi dilewati (tidak ada data pakar)")

# %%
import importlib
import sys

for mod in ['agregasi', 'sistem_fuzzy', 'validasi']:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

from agregasi import Agregasi
from sistem_fuzzy import FuzzyMamdani
from validasi import hitung_mape, interpretasi_mape, analisis_sensitivitas, rekomendasi

# %%
print("\n[TAHAP 5] ANALISIS SENSITIVITAS")
print("-" * 80)

hasil_sensitivitas = []

for _, row in df_hasil.iterrows():
    prodi = row['Prodi']
    x1, x2, x3 = row['X1'], row['X2'], row['X3']
    
    sens = analisis_sensitivitas(fuzzy, x1, x2, x3)
    
    print(f"\n{prodi}:")
    print(f"  Baseline Y: {sens['baseline']:.2f}")
    print(f"  S_X1: {sens['S_X1']:.4f}")
    print(f"  S_X2: {sens['S_X2']:.4f}")
    print(f"  S_X3: {sens['S_X3']:.4f}")
    print(f"  → Faktor Dominan: {sens['faktor_dominan']}")
    
    hasil_sensitivitas.append({
        'Prodi': prodi,
        'S_X1': sens['S_X1'],
        'S_X2': sens['S_X2'],
        'S_X3': sens['S_X3'],
        'Faktor_Dominan': sens['faktor_dominan']
    })

df_sensitivitas = pd.DataFrame(hasil_sensitivitas)

df_final = df_hasil.merge(df_sensitivitas, on='Prodi')


# %%
print("\n[TAHAP 6] REKOMENDASI PERBAIKAN")
print("-" * 80)

rekomendasi_list = []

for _, row in df_final.iterrows():
    prodi = row['Prodi']
    faktor = row['Faktor_Dominan']
    rekom = rekomendasi(faktor)
    
    print(f"\n{prodi}:")
    for r in rekom:
        print(f"  {r}")
    
    rekomendasi_list.append({
        'Prodi': prodi,
        'Rekomendasi': ' | '.join(rekom)
    })

df_rekomendasi = pd.DataFrame(rekomendasi_list)
df_final = df_final.merge(df_rekomendasi, on='Prodi')

# %%
print("\n[OUTPUT] MENYIMPAN HASIL")
print("-" * 80)
    
ringkasan = pd.DataFrame({
        'Metrik': ['Jumlah Prodi', 'MAPE (%)', 'Status Model', 
                   'Rata-rata X1', 'Rata-rata X2', 'Rata-rata X3',
                   'Rata-rata Y_Fuzzy'],
        'Nilai': [
            len(df_final),
            f'{mape:.2f}' if mape else 'N/A',
            interpretasi_mape(mape) if mape else 'N/A',
            f'{df_final["X1"].mean():.2f}',
            f'{df_final["X2"].mean():.2f}',
            f'{df_final["X3"].mean():.2f}',
            f'{df_final["Y_Fuzzy"].mean():.2f}'
        ]
    })

df_final.to_csv('hasil_diagnosis_tuning_10_prodi.csv', index=False)
ringkasan.to_csv('ringkasan_diagnosis_tuning_10_prodi.csv', index=False)

print("✓ hasil_diagnosis_tuning_10_prodi.csv")
print("✓ ringkasan_diagnosis_tuning_10_prodi.csv")

# %%
with open('laporan_lengkap_tuning_10_prodi.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("LAPORAN DIAGNOSIS PENJADWALAN MATA KULIAH\n")
    f.write("Fakultas Sains dan Teknologi - UIN Sunan Kalijaga\n")
    f.write("="*80 + "\n\n")
    
    f.write("RINGKASAN HASIL\n")
    f.write("-"*80 + "\n")
    f.write(f"Jumlah Program Studi: {len(df_final)}\n")
    if mape:
        f.write(f"MAPE: {mape:.2f}% ({interpretasi_mape(mape)})\n")
    f.write(f"Rata-rata Inefisiensi: {df_final['Y_Fuzzy'].mean():.2f}\n\n")
    
    f.write("DETAIL PER PROGRAM STUDI\n")
    f.write("-"*80 + "\n\n")
    
    for _, row in df_final.iterrows():
        f.write(f"{row['Prodi']}\n")
        f.write(f"  Variabel Input:\n")
        f.write(f"    X1 (Keterisian Ruang)  : {row['X1']:.2f}%\n")
        f.write(f"    X2 (Pelanggaran Batasan Akademik) : {row['X2']:.2f}%\n")
        f.write(f"    X3 (Waktu Tunggu Mahasiswa)   : {row['X3']:.2f}%\n")
        f.write(f"  Output:\n")
        f.write(f"    Y_Fuzzy: {row['Y_Fuzzy']:.2f} ({row['Interpretasi']})\n")
        if 'Y_Pakar' in row and not pd.isna(row['Y_Pakar']):
            f.write(f"    Y_Pakar: {row['Y_Pakar']:.2f}\n")
        f.write(f"  Sensitivitas:\n")
        f.write(f"    S_X1: {row['S_X1']:.4f}\n")
        f.write(f"    S_X2: {row['S_X2']:.4f}\n")
        f.write(f"    S_X3: {row['S_X3']:.4f}\n")
        f.write(f"  Faktor Dominan: {row['Faktor_Dominan']}\n")
        f.write(f"  Rekomendasi:\n")
        for r in row['Rekomendasi'].split(' | '):
            f.write(f"    {r}\n")
        f.write("\n")

print(f"✓ laporan_lengkap_tuning_10_prodi.txt")

# %%
print("\n" + "="*80)
print("KESIMPULAN")
print("="*80)

avg_s_x1 = df_sensitivitas['S_X1'].abs().mean()
avg_s_x2 = df_sensitivitas['S_X2'].abs().mean()
avg_s_x3 = df_sensitivitas['S_X3'].abs().mean()

faktor_dominan_fakultas = max([
    ('Keterisian Ruang', avg_s_x1),
    ('Pelanggaran Batasan Akademik', avg_s_x2),
    ('Waktu Tunggu Mahasiswa', avg_s_x3)
], key=lambda x: x[1])[0]

print(f"\nFaktor Dominan di Tingkat Fakultas: {faktor_dominan_fakultas}")
print(f"  S_X1: {avg_s_x1:.4f}")
print(f"  S_X2: {avg_s_x2:.4f}")
print(f"  S_X3: {avg_s_x3:.4f}")

print("\nRekomendasi Kebijakan Fakultas:")
for r in rekomendasi(faktor_dominan_fakultas):
    print(f"  {r}")

print("\n" + "="*80)
print("SELESAI")
print("="*80)
print("\nFile output:")
print("  1. hasil_agregasi.csv")
print("  2. hasil_diagnosis_tuning_10_prodi.csv")
print("  3. laporan_lengkap_tuning_10_prodi.txt")


