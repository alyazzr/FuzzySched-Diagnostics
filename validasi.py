import pandas as pd
import numpy as np

def analisis_sensitivitas(fuzzy_system, x1, x2, x3):
    """
    Analisis Sensitivitas OAT (One-at-a-Time).
    Mencoba kenaikan bertahap (+10, +25, +50) jika kenaikan kecil tidak mempan.
    """
    # 1. Output awal (Baseline)
    y_baseline = fuzzy_system.inferensi(x1, x2, x3)
    
    y_base_denom = y_baseline if y_baseline != 0 else 1.0

    def hitung_sensitivitas_per_variabel(var_name, val, v_others):
        for delta in [10, 25, 50]:
            val_baru = min(val + delta, 100)
            
            if val_baru == val: continue

            if var_name == 'x1':
                y_baru = fuzzy_system.inferensi(val_baru, v_others[0], v_others[1])
            elif var_name == 'x2':
                y_baru = fuzzy_system.inferensi(v_others[0], val_baru, v_others[1])
            else:
                y_baru = fuzzy_system.inferensi(v_others[0], v_others[1], val_baru)

            # Hitung perubahan output
            diff_y = abs(y_baru - y_baseline)
            
            if diff_y > 1e-5:
                return diff_y / delta
        
        return 0.0 

    # Eksekusi tes untuk tiap variabel
    s_x1 = hitung_sensitivitas_per_variabel('x1', x1, (x2, x3))
    s_x2 = hitung_sensitivitas_per_variabel('x2', x2, (x1, x3))
    s_x3 = hitung_sensitivitas_per_variabel('x3', x3, (x1, x2))

    # Tentukan faktor dominan
    sens_dict = {
        'Keterisian Ruang': s_x1,
        'Pelanggaran Batasan Akademik': s_x2,
        'Waktu Tunggu Mahasiswa': s_x3
    }
    
    if max(sens_dict.values()) == 0:
        faktor_dominan = "Stabil (Semua Variabel Optimal)"
    else:
        faktor_dominan = max(sens_dict, key=sens_dict.get)

    return {
        'S_X1': round(s_x1, 4),
        'S_X2': round(s_x2, 4),
        'S_X3': round(s_x3, 4),
        'faktor_dominan': faktor_dominan,
        'baseline': round(y_baseline, 2)
    }

def rekomendasi(faktor_dominan):
    """Rekomendasi strategis berdasarkan faktor dominan inefisiensi"""
    rekomendasi_dict = {
        'Keterisian Ruang (X1)': [
            "Prioritas: Optimasi penggunaan ruang kelas",
            "- Evaluasi distribusi mata kuliah pada ruang-ruang dengan kapasitas kecil",
            "- Manfaatkan sistem shift atau pengalihan ke ruang laboratorium jika memungkinkan",
            "- Tinjau ulang rasio jumlah mahasiswa per kelas paralel"
        ],
        'Pelanggaran Batasan Akademik (X2)': [
            "Prioritas: Perbaikan ergonomi dan batasan akademik",
            "- Kurangi jadwal kuliah beruntun (maraton) mahasiswa > 2 matkul",
            "- Tambahkan jeda minimal 15-30 menit antar sesi kuliah",
            "- Sosialisasi ulang batas maksimal mengajar dosen (9 SKS/hari)"
        ],
        'Waktu Tunggu Mahasiswa (X3)': [
            "Prioritas: Optimasi jeda waktu antar kelas",
            "- Rapatkan jadwal kuliah yang memiliki jeda kosong (gap) terlalu lama",
            "- Gunakan sistem blok waktu untuk angkatan yang sama",
            "- Evaluasi sebaran jadwal pada hari-hari yang memiliki waktu tunggu tinggi"
        ]
    }
    return rekomendasi_dict.get(faktor_dominan, ["Kondisi Ideal: Pertahankan pola penjadwalan saat ini."])

def hitung_mape(y_true, y_pred):
    """
    Menghitung Mean Absolute Percentage Error (MAPE)
    """
    import numpy as np
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def interpretasi_mape(mape_value):
    """
    Interpretasi nilai MAPE berdasarkan standar Lewis
    """
    if mape_value < 10:
        return "Sangat Akurat"
    elif 10 <= mape_value < 20:
        return "Baik"
    elif 20 <= mape_value < 50:
        return "Layak (Reasonable)"
    else:
        return "Tidak Akurat"