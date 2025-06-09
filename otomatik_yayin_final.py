import subprocess
import logging
import datetime
import os
import glob

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

def temizle_html_dosyalari():
    html_dosyalar = glob.glob("*.html")
    if not html_dosyalar:
        print("Silinecek HTML dosyasi bulunamadi.")
        logging.info("Silinecek HTML dosyasi bulunamadi.")
    else:
        for dosya in html_dosyalar:
            try:
                os.remove(dosya)
                print(f"Silindi: {dosya}")
                logging.info(f"Silindi: {dosya}")
            except Exception as e:
                print(f"{dosya} silinemedi: {e}")
                logging.error(f"{dosya} silinemedi: {e}")

def main():
    try:
        run_script("tefas_fiyat_indir_pp_uyumlu_final.py", "1. TEFAS fiyat indiriliyor")
        run_script("convert_to_html.py", "2. HTML dosyalari uretiliyor")
        run_script("html_yayinlarini_yukle_final.py", "3. GitHub'a yukleniyor")
        temizle_html_dosyalari()
        print("Tum islem basariyla tamamlandi.")
    except Exception:
        print("Otomasyon islemi hata nedeniyle durdu. Log dosyasini kontrol edin.")

if __name__ == "__main__":
    main()
