import argparse
import sys
import pandas as pd
from sistem_fuzzy import FuzzyMamdani
import os

def tampilkan_menu():
    print("\n" + "="*50)
    print("   SISTEM DIAGNOSIS INEFISIENSI JADWAL (10 PRODI)")
    print("="*50)
    print("1. Diagnosis Program Studi Terdaftar (Data CSV)")
    print("2. Diagnosis Input Manual (Custom)")
    print("3. Keluar")
    print("-" * 50)


def proses_prodi(df, index, f):
    if df is None:
        print("[Peringatan] Data CSV tidak tersedia.")
        return 2
    if not (0 <= index < len(df)):
        print("Nomor tidak valid!")
        return 2
    prodi_data = df.iloc[index]
    x1, x2, x3 = prodi_data['X1'], prodi_data['X2'], prodi_data['X3']
    print(f"\n[INFO] Memproses data {prodi_data['Prodi']}...")
    print(f"Data: Ruang={x1}, Dosen={x2}, Mhs={x3}")
    skor = f.inferensi(x1, x2, x3)
    status = f.interpretasi(skor)
    print("-" * 30)
    print(f"SKOR INEFISIENSI : {skor:.2f}")
    print(f"STATUS           : {status.upper()}")
    print("-" * 30)
    return 0


def proses_manual(x1, x2, x3, f):
    print("\n[INFO] Memproses input manual...")
    print(f"Data: Ruang={x1}, Dosen={x2}, Mhs={x3}")
    skor = f.inferensi(x1, x2, x3)
    status = f.interpretasi(skor)
    print("-" * 30)
    print(f"SKOR INEFISIENSI : {skor:.2f}")
    print(f"STATUS           : {status.upper()}")
    print("-" * 30)
    return 0


def main():
    parser = argparse.ArgumentParser(description='CLI untuk sistem diagnosis inefisiensi jadwal')
    parser.add_argument('--file', '-f', default='hasil_diagnosis_tuning_10_prodi.csv', help='Path to CSV file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='List available prodi and exit')
    group.add_argument('--prodi-index', type=int, help='1-based index of prodi to process')
    group.add_argument('--prodi-name', type=str, help='Name (substring) of prodi to process')
    group.add_argument('--manual', nargs=3, type=float, metavar=('X1','X2','X3'), help='Manual input values (X1 X2 X3)')
    args = parser.parse_args()

    csv_file = args.file

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        print(f"[Peringatan] File {csv_file} tidak ditemukan!")
        df = None

    # Inisialisasi mesin fuzzy
    f = FuzzyMamdani()

    # Mode non-interaktif
    if args.list:
        if df is None:
            print("[Peringatan] Data CSV tidak tersedia.")
            sys.exit(2)
        print("DAFTAR PROGRAM STUDI:")
        for idx, row in df.iterrows():
            print(f"{idx+1}. {row['Prodi']}")
        sys.exit(0)

    if args.prodi_index is not None:
        idx = args.prodi_index - 1
        exit_code = proses_prodi(df, idx, f)
        sys.exit(exit_code)

    if args.prodi_name:
        if df is None:
            print("[Peringatan] Data CSV tidak tersedia.")
            sys.exit(2)
        matches = df[df['Prodi'].str.contains(args.prodi_name, case=False, na=False)]
        if matches.empty:
            print("Prodi tidak ditemukan.")
            sys.exit(2)
        if len(matches) > 1:
            print("Ditemukan lebih dari satu kecocokan, gunakan --list atau --prodi-index.")
            for idx, row in matches.iterrows():
                print(f"{idx+1}. {row['Prodi']}")
            sys.exit(2)
        index = matches.index[0]
        exit_code = proses_prodi(df, index, f)
        sys.exit(exit_code)

    if args.manual:
        x1, x2, x3 = args.manual
        exit_code = proses_manual(x1, x2, x3, f)
        sys.exit(exit_code)

    while True:
        tampilkan_menu()
        pilihan = input("Pilih Menu (1/2/3): ")

        if pilihan == '1':
            if df is None:
                print("[Peringatan] Data CSV tidak tersedia. Pilih opsi 2 untuk input manual.")
                continue

            print("\nDAFTAR PROGRAM STUDI:")
            for idx, row in df.iterrows():
                print(f"{idx+1}. {row['Prodi']}")
            
            try:
                nomer = int(input("\nPilih Nomor Prodi: ")) - 1
                if 0 <= nomer < len(df):
                    prodi_data = df.iloc[nomer]
                    # Ambil nilai X dari CSV
                    x1, x2, x3 = prodi_data['X1'], prodi_data['X2'], prodi_data['X3']
                    
                    print(f"\n[INFO] Memproses data {prodi_data['Prodi']}...")
                    print(f"Data: Ruang={x1}, Dosen={x2}, Mhs={x3}")
                    
                    # Hitung Fuzzy menggunakan FuzzyMamdani
                    skor = f.inferensi(x1, x2, x3)
                    status = f.interpretasi(skor)
                    
                    print("-" * 30)
                    print(f"SKOR INEFISIENSI : {skor:.2f}")
                    print(f"STATUS           : {status.upper()}")
                    print("-" * 30)
                else:
                    print("Nomor tidak valid!")
            except ValueError:
                print("Masukkan nomor yang valid!")

        elif pilihan == '2':
            print("\n--- INPUT MANUAL ---")
            try:
                x1 = float(input("Keterisian Ruang (0-100): "))
                x2 = float(input("Pelanggaran Dosen (0-100): "))
                x3 = float(input("Beban Mahasiswa (0-100): "))
            except ValueError:
                print("Input tidak valid. Masukkan angka.")
                continue

            skor = f.inferensi(x1, x2, x3)
            status = f.interpretasi(skor)
            print(f"\nHasil: {skor:.2f} ({status})")

        elif pilihan == '3':
            break

if __name__ == "__main__":
    main()