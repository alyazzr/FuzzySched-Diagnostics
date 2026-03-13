import numpy as np
import matplotlib.pyplot as plt

def trapmf(x, params):
    a, b, c, d = params
    y = np.zeros_like(x)
    
    # Kaki Kiri (Naik)
    if b > a:
        idx_naik = np.logical_and(x > a, x < b)
        y[idx_naik] = (x[idx_naik] - a) / (b - a)
    else:
        y[x == a] = 1 
        
    # Bahu Atas (Datar/Plateau)
    idx_top = np.logical_and(x >= b, x <= c)
    y[idx_top] = 1.0
    
    # Kaki Kanan (Turun)
    if d > c:
        idx_turun = np.logical_and(x > c, x < d)
        y[idx_turun] = (d - x[idx_turun]) / (d - c)
        
    return y

x = np.arange(0, 100.1, 0.1)


# X1: Keterisian Ruang
params_x1 = {
    'Rendah': [0, 0, 13.3, 46.6],
    'Sedang': [40, 50, 63, 73.3],
    'Tinggi': [66.6, 80, 100, 100]
}

# X2: Pelanggaran Dosen
params_x2 = {
    'Rendah': [0, 0, 25, 50],
    'Sedang': [25, 37.5, 62.5, 75],
    'Tinggi': [50, 75, 100, 100]
}

# X3: Waktu Tunggu
params_x3 = {
    'Cepat':  [0, 0, 20, 60],
    'Sedang': [40, 50, 70, 80],
    'Lama':   [60, 80, 100, 100]
}

params_output = {
    'Efisien (Baik)':        [0, 0, 20, 40],
    'Cukup Efisien (Sedang)': [30, 45, 55, 70],
    'Tidak Efisien (Buruk)':  [60, 80, 100, 100]
}

def plot_single_curve(filename, title, x_label, params):
    plt.figure(figsize=(8, 5)) 
    
    colors = ['#1f77b4', '#2ca02c', '#d62728'] 
    styles = ['-', '-', '-'] 
    
    for i, (label, p) in enumerate(params.items()):
        y = trapmf(x, p)
        plt.plot(x, y, linewidth=2.5, color=colors[i], label=label, linestyle=styles[i])
        plt.fill_between(x, y, alpha=0.1, color=colors[i])
    
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel('Derajat Keanggotaan (μ)', fontsize=12)
    plt.ylim(-0.05, 1.1)
    plt.xlim(0, 100)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc='center right', fontsize=10, frameon=True)
    plt.tight_layout()
    
    plt.savefig(filename, dpi=300)
    print(f"Gambar tersimpan: {filename}")
    plt.show()

# Gambar 1: Keterisian Ruang
plot_single_curve('Kurva_Awal_Keterisian.png', 
                  'Fungsi Keanggotaan Keterisian Ruang (X1)', 
                  'Persentase Keterisian (%)', 
                  params_x1)

# Gambar 2: Pelanggaran Dosen
plot_single_curve('Kurva_Awal_Pelanggaran.png', 
                  'Fungsi Keanggotaan Pelanggaran Batasan Akademik (X2)', 
                  'Persentase Poin Pelanggaran (%)', 
                  params_x2)

# Gambar 3: Waktu Tunggu
plot_single_curve('Kurva_Awal_WaktuTunggu.png', 
                  'Fungsi Keanggotaan Waktu Tunggu Mahasiswa (X3)', 
                  'Persentase Waktu Tunggu (%)', 
                  params_x3)

plot_single_curve('Kurva_Awal_Output_Inefisiensi.png', 
                  'Fungsi Keanggotaan Output: Inefisiensi Jadwal (Y)', 
                  'Skor Inefisiensi (0 - 100)', 
                  params_output)