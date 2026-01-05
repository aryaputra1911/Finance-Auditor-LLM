import pandas as pd
import numpy as np
import re
import io
import json
import os
from pathlib import Path

class FinancialCanonicalizer:
    def __init__(self):
        # Regex untuk membersihkan simbol uang, koma, dan karakter aneh
        self.clean_regex = re.compile(r'[^\d\.\(\)\-]')
        # Keyword darurat untuk mendeteksi tabel finansial
        self.emergency_keywords = ['revenue', 'income', 'asset', 'profit', 'loss', 'cash', 'tax', 'sales', 'operating', 'net', 'ebitda']

    def clean_cell(self, val):
        """Pembersih sel yang sangat aman dari error 'ambiguous'"""
        # 1. Penanganan awal untuk nilai None atau NaN
        if val is None: 
            return 0.0
        
        # 2. Proteksi dari error 'The truth value of a Series is ambiguous'
        # Jika val ternyata adalah Series/List, ambil elemen pertamanya
        if isinstance(val, (pd.Series, np.ndarray, list)):
            val = val[0] if len(val) > 0 else 0.0

        # Cek NaN secara aman
        try:
            if pd.isna(val): return 0.0
        except:
            pass

        # 3. Normalisasi teks
        s = str(val).strip().lower()
        if s in ['-', '', '_', 'none', 'þ', '¨', 'n/a', 'nil', '.']: 
            return 0.0
        
        # 4. Deteksi Persentase
        is_percent = '%' in s
        
        # 5. Pembersihan Karakter
        clean = self.clean_regex.sub('', s)
        
        # 6. Logika Akuntansi (Dalam kurung berarti negatif)
        if clean.startswith('(') and clean.endswith(')'):
            clean = '-' + clean[1:-1]
        elif clean.endswith('-'):
            clean = '-' + clean[:-1]
            
        # 7. Konversi Akhir ke Float
        try:
            num = float(clean)
            return num / 100 if is_percent else num
        except:
            # Jika tetap teks (label baris), kembalikan teks aslinya (tapi bersih)
            return str(val).strip()

    def is_high_quality(self, df):
        """Filter kualitas agar hanya tabel emas yang disimpan"""
        if df.empty or df.shape[1] < 2: 
            return False
        
        # Ambil konteks dari header dan 3 baris pertama
        header_context = " ".join(df.columns.astype(str)).lower()
        top_rows_context = " ".join(df.head(3).astype(str).values.flatten()).lower()
        full_context = header_context + " " + top_rows_context

        # A. Deteksi Tahun
        has_time = bool(re.search(r'(201\d|202\d|q[1-4]|fiscal|year|ended)', full_context))

        # B. Hitung Kepadatan Angka (Density)
        def check_num(x):
            return isinstance(x, (int, float)) and x != 0.0
        
        # Gunakan .map() sesuai saran warning pandas terbaru
        num_count = df.map(check_num).sum().sum()
        density = num_count / df.size if df.size > 0 else 0

        # C. Cari Kata Kunci Finansial
        has_fin = any(kw in full_context for kw in self.emergency_keywords)

        # Keputusan: Lolos jika ada konteks waktu ATAU punya keyword + sedikit angka
        if has_time and density > 0.02: return True 
        if has_fin and density > 0.05: return True
        if density > 0.2: return True
        
        return False

    def parse_markdown_table(self, md_content):
        """Parsing manual tabel Markdown agar kolom tidak bergeser"""
        lines = md_content.strip().split('\n')
        rows = []
        for line in lines:
            if '|' in line:
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                # Abaikan baris separator |---|---|
                if all(set(c) <= {'-', ':', ' '} for c in cells):
                    continue
                rows.append(cells)
        
        if len(rows) < 2: return None
        
        df = pd.DataFrame(rows)
        # Baris pertama jadi kolom
        df.columns = [str(c).strip() if c else f"Col_{i}" for i, c in enumerate(df.iloc[0])]
        return df.iloc[1:].reset_index(drop=True)

    def process_file(self, json_path, output_dir):
        """Fungsi utama untuk memproses file JSON decomposed"""
        if not os.path.exists(json_path): return 0
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON {json_path}: {e}")
            return 0
        
        count = 0
        for item in data:
            if item.get('type') == 'table':
                df = self.parse_markdown_table(item['content'])
                if df is not None:
                    # Bersihkan setiap elemen tabel menggunakan .map()
                    df = df.map(self.clean_cell)
                    
                    if self.is_high_quality(df):
                        file_id = item['id']
                        output_file = Path(output_dir) / f"{file_id}.csv"
                        df.to_csv(output_file, index=False)
                        count += 1
        return count