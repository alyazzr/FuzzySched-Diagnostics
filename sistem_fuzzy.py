import numpy as np

class FuzzyMamdani:
    def __init__(self):
        # Universe of Discourse untuk Output (0 - 100)
        self.universe = np.arange(0, 100.1, 0.1)

    def trapezoid(self, x, a, b, c, d):
        x = np.atleast_1d(x)
        y = np.zeros_like(x, dtype=float)
        
        # Sisi kiri trapesium (Naik)
        if b > a:
            mask_left = (x >= a) & (x < b)
            y[mask_left] = (x[mask_left] - a) / (b - a)
        else:
            y[x == a] = 1.0  # Handle jika a == b (tegak lurus)
            
        # Bagian atas trapesium (Datar/Plato)
        mask_top = (x >= b) & (x <= c)
        y[mask_top] = 1.0
        
        # Sisi kanan trapesium (Turun)
        if d > c:
            mask_right = (x > c) & (x <= d)
            y[mask_right] = (d - x[mask_right]) / (d - c)
            
        return y[0] if y.size == 1 else y

    def fuzzifikasi(self, x1, x2, x3):
        # --- INPUT PARAMETERS ---
        
        mu_x1 = {
            'rendah': self.trapezoid(x1, 0, 0, 13.3, 46.6),
            'sedang': self.trapezoid(x1, 40, 50, 63, 73.3),
            'tinggi': self.trapezoid(x1, 66.6, 80, 200, 200) 
        }
        mu_x2 = {
            'rendah': self.trapezoid(x2, 0, 0, 25, 50),
            'sedang': self.trapezoid(x2, 25, 37.5, 62.5, 75),
            'tinggi': self.trapezoid(x2, 50, 75, 100, 100)
        }
        mu_x3 = {
            'cepat':  self.trapezoid(x3, 0, 0, 20, 60),
            'sedang': self.trapezoid(x3, 40, 50, 70, 80),
            'lama':   self.trapezoid(x3, 60, 80, 100, 100)
        }
        return {'x1': mu_x1, 'x2': mu_x2, 'x3': mu_x3}

    def evaluasi_aturan(self, mu):
        x1, x2, x3 = mu['x1'], mu['x2'], mu['x3']
        
        # Inisialisasi list untuk menampung firing strength (alpha-predikat)
        fire_strength = {
            'efisien': [],
            'cukup_efisien': [],
            'tidak_efisien': []
        }

        # --- BASIS ATURAN (REVISI TUNING) ---

        # 1. KELOMPOK X1 = SEDANG (Normal)
        fire_strength['efisien'].append(min(x1['sedang'], x2['rendah'], x3['sedang']))
        fire_strength['efisien'].append(min(x1['sedang'], x2['rendah'], x3['cepat']))
        fire_strength['efisien'].append(min(x1['sedang'], x2['rendah'], x3['lama']))
        fire_strength['efisien'].append(min(x1['sedang'], x2['sedang'], x3['sedang']))
        fire_strength['cukup_efisien'].append(min(x1['sedang'], x2['sedang'], x3['cepat']))
        fire_strength['cukup_efisien'].append(min(x1['sedang'], x2['sedang'], x3['lama']))
        fire_strength['cukup_efisien'].append(min(x1['sedang'], x2['tinggi'], x3['sedang']))
        fire_strength['tidak_efisien'].append(min(x1['sedang'], x2['tinggi'], x3['cepat']))
        fire_strength['tidak_efisien'].append(min(x1['sedang'], x2['tinggi'], x3['lama']))

        # 2. KELOMPOK X1 = RENDAH
        fire_strength['efisien'].append(min(x1['rendah'], x2['rendah'], x3['sedang']))
        fire_strength['efisien'].append(min(x1['rendah'], x2['rendah'], x3['cepat']))
        fire_strength['cukup_efisien'].append(min(x1['rendah'], x2['rendah'], x3['lama']))
        fire_strength['cukup_efisien'].append(min(x1['rendah'], x2['sedang'], x3['sedang']))
        fire_strength['cukup_efisien'].append(min(x1['rendah'], x2['sedang'], x3['cepat']))
        fire_strength['tidak_efisien'].append(min(x1['rendah'], x2['sedang'], x3['lama']))
        fire_strength['tidak_efisien'].append(min(x1['rendah'], x2['tinggi'], x3['sedang']))
        fire_strength['tidak_efisien'].append(min(x1['rendah'], x2['tinggi'], x3['cepat']))
        fire_strength['tidak_efisien'].append(min(x1['rendah'], x2['tinggi'], x3['lama']))

        # 3. KELOMPOK X1 = TINGGI (FOKUS TUNING R19-R21)
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['rendah'], x3['sedang'])) 
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['rendah'], x3['cepat']))  
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['rendah'], x3['lama']))   
        
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['sedang'], x3['sedang']))
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['sedang'], x3['cepat']))
        fire_strength['cukup_efisien'].append(min(x1['tinggi'], x2['sedang'], x3['lama']))
        fire_strength['tidak_efisien'].append(min(x1['tinggi'], x2['tinggi'], x3['sedang']))
        fire_strength['tidak_efisien'].append(min(x1['tinggi'], x2['tinggi'], x3['cepat']))
        fire_strength['tidak_efisien'].append(min(x1['tinggi'], x2['tinggi'], x3['lama']))

        return fire_strength

    def agregasi(self, rules):
        return {
            'efisien': max(rules['efisien']) if rules['efisien'] else 0.0,
            'cukup_efisien': max(rules['cukup_efisien']) if rules['cukup_efisien'] else 0.0,
            'tidak_efisien': max(rules['tidak_efisien']) if rules['tidak_efisien'] else 0.0
        }

    def defuzzifikasi(self, agregat):
        y = self.universe
        
        # --- OUTPUT PARAMETERS (TUNING) ---
        
        mu_efisien = self.trapezoid(y, 0, 0, 20, 40)
        mu_cukup   = self.trapezoid(y, 30, 45, 55, 70) 
        mu_tidak   = self.trapezoid(y, 60, 80, 100, 100)
        
        # Clipping (Memotong kurva output sesuai nilai alpha-predikat)
        c_efisien = np.minimum(mu_efisien, agregat['efisien'])
        c_cukup   = np.minimum(mu_cukup, agregat['cukup_efisien'])
        c_tidak   = np.minimum(mu_tidak, agregat['tidak_efisien'])
        
        # Agregasi (Menggabungkan semua kurva hasil clipping dengan Max)
        mu_total = np.maximum(c_efisien, np.maximum(c_cukup, c_tidak))
        
        # Perhitungan Centroid (Center of Gravity)
        num = np.sum(mu_total * y)
        den = np.sum(mu_total)
        
        return num / den if den != 0 else 0.0

    def inferensi(self, x1, x2, x3):
        mu = self.fuzzifikasi(x1, x2, x3)
        rules = self.evaluasi_aturan(mu)
        agregat = self.agregasi(rules)
        hasil = self.defuzzifikasi(agregat)
        return hasil

    def interpretasi(self, nilai):
        if nilai <= 40:
            return "Efisien"
        elif nilai <= 70:
            return "Cukup Efisien"
        else:
            return "Tidak Efisien"