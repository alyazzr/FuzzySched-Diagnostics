import pandas as pd
import numpy as np
import re

class Agregasi:

    def __init__(self):
        # --- KONFIGURASI BATASAN AKADEMIK ---
        self.JAM_OPERASIONAL_MULAI = 7
        self.JAM_OPERASIONAL_SELESAI = 18
        
        # Batasan Dosen
        self.MAX_BEBAN_HARIAN_DOSEN = 9  # SKS
        
        # Batasan Mahasiswa (Maksimal 2 Matkul Beruntun)
        self.MAX_KULIAH_BERUNTUN = 2     
        self.MIN_JEDA_MENIT = 15 

    def _to_minutes(self, t):
        """Konversi waktu format HH:MM atau int ke menit"""
        try:
            if pd.isna(t): return np.nan
            s = str(t).strip()
            if ':' in s:
                parts = s.split(':')
                return int(parts[0]) * 60 + int(parts[1])
            s_digits = ''.join(ch for ch in s if ch.isdigit())
            if s_digits == '': return np.nan
            v = int(s_digits)
            if v < 100: 
                return v * 60
            return (v // 100) * 60 + (v % 100)
        except:
            return np.nan

    def _explode_nip(self, df):
        """Memecah satu sel berisi banyak NIP"""
        tmp = df[['nip_dosen', 'hari', 'sks', 'kode_mk']].copy()
        tmp['nip_dosen'] = tmp['nip_dosen'].astype(str).fillna('').str.strip()
        tmp['nip_list'] = tmp['nip_dosen'].apply(lambda s: [re.sub(r'\D', '', p).strip() for p in re.split(r'[;,]+', s) if re.sub(r'\D', '', p).strip()])
        tmp = tmp.explode('nip_list')
        tmp = tmp[tmp['nip_list'].notna() & (tmp['nip_list'] != '')]
        return tmp.rename(columns={'nip_list': 'nip'})

    # ---------------------------------------------------------
    # X1: KETERISIAN RUANG (Sama dengan Manual: Rasio Utilitas)
    # ---------------------------------------------------------
    def hitung_x1(self, df_jadwal, df_ruang):
        try:
            df = df_jadwal.copy()
            if len(df) == 0: return 0.0
            
            # Merge Data Ruang
            if 'kode_ruang' in df.columns:
                df['kode_ruang'] = df['kode_ruang'].astype(str).str.strip()
                ruang = df_ruang[['kode_ruang', 'kapasitas']].copy()
                ruang['kode_ruang'] = ruang['kode_ruang'].astype(str).str.strip()
                ruang['kapasitas'] = pd.to_numeric(ruang['kapasitas'], errors='coerce')
                df = df.merge(ruang, on='kode_ruang', how='left')
            else:
                df['kapasitas'] = np.nan

            df['sks'] = pd.to_numeric(df['sks'], errors='coerce').fillna(0)
            df['jumlah_peserta'] = pd.to_numeric(df.get('jumlah_peserta', 0), errors='coerce').fillna(0)
            
            # Isi kapasitas kosong dengan rata-rata (agar tidak error)
            mean_cap = df['kapasitas'].mean()
            if np.isnan(mean_cap) or mean_cap == 0: mean_cap = 40 
            df['kapasitas'].fillna(mean_cap, inplace=True)

            # Rumus: (Peserta * SKS) / (Kapasitas * SKS)
            pembilang = (df['jumlah_peserta'] * df['sks']).sum()
            penyebut = (df['kapasitas'] * df['sks']).sum()

            if penyebut == 0: return 0.0

            x1 = (pembilang / penyebut) * 100
            return float(x1)
        
        except Exception as e:
            print(f"Warning hitung X1: {e}")
            return 0.0

    # ---------------------------------------------------------
    # X2: PELANGGARAN (Beda dengan Manual: Ada Deteksi Beruntun)
    # ---------------------------------------------------------
    def hitung_x2(self, df_jadwal):
        """
        Rumus: (Total SKS Melanggar / Total SKS Prodi) * 100%
        """
        try:
            df = df_jadwal.copy()
            if len(df) == 0: return 0.0
            
            total_sks_prodi = pd.to_numeric(df['sks'], errors='coerce').fillna(0).sum()
            if total_sks_prodi == 0: return 0.0

            violation_indices = set()

            df['start_min'] = df['jam_mulai'].apply(self._to_minutes)
            df['end_min'] = df['jam_selesai'].apply(self._to_minutes)
            df['sks'] = pd.to_numeric(df['sks'], errors='coerce').fillna(0)

            # --- A. Cek Jam Operasional ---
            start_limit = self.JAM_OPERASIONAL_MULAI * 60
            end_limit = self.JAM_OPERASIONAL_SELESAI * 60
            idx_jam = df[((df['start_min'] < start_limit) | (df['end_min'] > end_limit))].index
            violation_indices.update(idx_jam)

            # --- B. Cek Beban Dosen ---
            if 'nip_dosen' in df.columns:
                df_dosen = self._explode_nip(df)
                beban_harian = df_dosen.groupby(['nip', 'hari'])['sks'].sum()
                overload_cases = beban_harian[beban_harian > self.MAX_BEBAN_HARIAN_DOSEN].index
                
                for nip, hari in overload_cases:
                    mask = (df['hari'] == hari) & (df['nip_dosen'].astype(str).str.contains(nip, regex=False))
                    violation_indices.update(df[mask].index)

            # --- C. Cek Kuliah Beruntun (Mahasiswa) - FITUR TAMBAHAN SISTEM ---
            df['kelas_group'] = df['kelas'].astype(str).fillna('UNKNOWN')
            groups = df.groupby(['kelas_group', 'hari'])
            
            for name, group in groups:
                if len(group) <= self.MAX_KULIAH_BERUNTUN: 
                    continue
                
                group = group.sort_values('start_min')
                starts = group['start_min'].values
                ends = group['end_min'].values
                indices = group.index.values
                
                streak = 1
                for i in range(len(group) - 1):
                    gap = starts[i+1] - ends[i]
                    # Jika jeda kurang dari 15 menit, dianggap beruntun
                    if gap < self.MIN_JEDA_MENIT: 
                        streak += 1
                    else:
                        streak = 1 
                    
                    # Jika streak > 2, matkul ini (i+1) melanggar
                    if streak > self.MAX_KULIAH_BERUNTUN:
                        violation_idx = indices[i+1]
                        violation_indices.update([violation_idx])

            # --- Hitung Total SKS Pelanggaran ---
            total_sks_melanggar = df.loc[list(violation_indices), 'sks'].sum()

            x2 = (total_sks_melanggar / total_sks_prodi) * 100
            return float(np.clip(x2, 0, 100))
        
        except Exception as e:
            print(f"Warning hitung X2: {e}")
            return 0.0

    # ---------------------------------------------------------
    # X3: BEBAN MAHASISWA (Sama dengan Manual: Rasio Gap/Durasi)
    # ---------------------------------------------------------
    def hitung_x3(self, df_jadwal):
        """
        Rumus Manual: (Total Menit Gap / Total Menit Kuliah) * 100%
        """
        try:
            df = df_jadwal.copy()
            if len(df) == 0: return 0.0

            df['kelas_group'] = df['kelas'].astype(str).fillna('UNKNOWN')
            df['start_min'] = df['jam_mulai'].apply(self._to_minutes)
            df['end_min'] = df['jam_selesai'].apply(self._to_minutes)
            df['sks'] = pd.to_numeric(df['sks'], errors='coerce').fillna(0)

            total_gap_menit = 0
            
            # Hitung Total Durasi Kuliah (SKS * 50 menit)
            total_durasi_menit = df['sks'].sum() * 50
            if total_durasi_menit == 0: return 0.0

            # Hitung Gap
            for name, group in df.groupby(['kelas_group', 'hari']):
                group = group.dropna(subset=['start_min', 'end_min'])
                if len(group) < 2: continue
                
                group = group.sort_values('start_min')
                starts = group['start_min'].values
                ends = group['end_min'].values
                
                for i in range(len(group) - 1):
                    gap = starts[i+1] - ends[i]
                    if gap > 0: 
                        total_gap_menit += gap
            
            # Rumus Ratio (Sama persis dengan perhitungan manual)
            x3 = (total_gap_menit / total_durasi_menit) * 100
            return float(x3)
        
        except Exception as e:
            print(f"Warning hitung X3: {e}")
            return 0.0

    # ---------------------------------------------------------
    # PROSES UTAMA
    # ---------------------------------------------------------
    def proses(self, df_jadwal, df_ruang):
        # 1. Hitung Nilai
        x1 = self.hitung_x1(df_jadwal, df_ruang)
        x2 = self.hitung_x2(df_jadwal)
        x3 = self.hitung_x3(df_jadwal)

        # 2. Safety Check (Ubah None/NaN jadi 0.0)
        if x1 is None or np.isnan(x1): x1 = 0.0
        if x2 is None or np.isnan(x2): x2 = 0.0
        if x3 is None or np.isnan(x3): x3 = 0.0

        # 3. Return Dictionary (Tanpa Round agar presisi)
        return {
            'X1': float(x1),
            'X2': float(x2),
            'X3': float(x3)
        }