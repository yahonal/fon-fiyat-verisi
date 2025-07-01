#!/usr/bin/env python3
import subprocess
import logging
import datetime
import os

today = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = f"otomasyon_log_{today}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_script(script_path, description):
    try:
        logging.info(f"{description} basliyor...")
        print(f"{description} basliyor...")
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"{description} tamamlandi.")
        print(f"{description} tamamlandi.")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"{description} sirasinda hata: {e.stderr}")
        print(f"{description} sirasinda hata olustu:\n{e.stderr}")
        raise

def main():
    try:
        run_script("tefas_fiyat_indir_pp_uyumlu_final_guncel_linux.py", "1. TEFAS fiyat indiriliyor")
        run_script("convert_to_html_guncel_linux.py", "2. HTML dosyalari uretiliyor")
        run_script("html_yayinlarini_yukle_final_guncel_linux.py", "3. GitHub'a yukleniyor")
        print("Tum islem basariyla tamamlandi.")
    except Exception:
        print("Otomasyon islemi hata nedeniyle durdu. Log dosyasini kontrol edin.")

if __name__ == "__main__":
    main()
