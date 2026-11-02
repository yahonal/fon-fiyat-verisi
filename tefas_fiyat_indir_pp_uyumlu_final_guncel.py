import math
import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime

# html_yayin silinmez: otomatik calismada gecmis veri buradaki CSV'lerden okunur.
# Bir fon hata verirse onceki yayini da yerinde kalir.
html_dir = os.path.join(os.getcwd(), "html_yayin")
os.makedirs(html_dir, exist_ok=True)

with open("fund_list.dat", "r") as file:
    fonlar = [line.strip() for line in file if line.strip()]

today = datetime.today().date()
TEFAS_URL = "https://www.tefas.gov.tr/api/funds/fonFiyatBilgiGetir"
# TEFAS sadece bu ay degerlerini kabul eder; en fazla 5 yillik gecmis verir.
TEFAS_PERIYOTLARI = (1, 3, 6, 12, 36, 60)
# Son birkac gunu her seferinde yeniden cek: sonradan duzeltilen fiyatlari gunceller.
GERI_BAKIS_GUN = 10
# Son fiyat bundan eskiyse fon hatali sayilir (uzun bayram tatilleri icin 10 gun).
MAKS_GECIKME_GUN = 10
DENEME_SAYISI = 3
ISTEK_ZAMAN_ASIMI = 30  # saniye
ISTEK_ARASI_BEKLEME = 0.5  # saniye

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/plain, */*"}

hatali_fonlar = []


def bayat_mi(data):
    if data.empty:
        return True
    return (today - data["Date"].max().date()).days > MAKS_GECIKME_GUN


def periyot_sec(data):
    if data.empty:
        return TEFAS_PERIYOTLARI[-1]
    gerekli_gun = (today - data["Date"].max().date()).days + GERI_BAKIS_GUN
    gerekli_ay = math.ceil(gerekli_gun / 28)
    for periyot in TEFAS_PERIYOTLARI:
        if periyot >= gerekli_ay:
            return periyot
    return TEFAS_PERIYOTLARI[-1]


def veri_cek(fon_kodu, periyot):
    govde = {"fonKodu": fon_kodu, "dil": "TR", "periyod": periyot}
    for deneme in range(1, DENEME_SAYISI + 1):
        try:
            response = requests.post(
                TEFAS_URL, json=govde, headers=HEADERS, timeout=ISTEK_ZAMAN_ASIMI
            )
            response.raise_for_status()
            json_data = response.json()
            if json_data.get("errorMessage"):
                raise ValueError(json_data["errorMessage"])
            return json_data.get("resultList") or []
        except Exception as e:
            if deneme == DENEME_SAYISI:
                raise
            print(f"Deneme {deneme} basarisiz: {e}")
            time.sleep(5 * deneme)


for fon_kodu in fonlar:
    print(f"---\n{fon_kodu} icin islem baslatiliyor...")

    yedek_dosya = f"{fon_kodu}_fund.csv"

    # Gecmis veri: once yayindaki CSV, yoksa yerel yedek dosya
    html_csv = os.path.join(html_dir, f"{fon_kodu}.csv")
    kaynak_dosya = html_csv if os.path.exists(html_csv) else yedek_dosya

    if os.path.exists(kaynak_dosya):
        try:
            existing_data = pd.read_csv(kaynak_dosya, parse_dates=["Date"])
            print(f"Dosya mevcut, {len(existing_data)} satir yuklendi.")
        except Exception as e:
            print(f"Hata: Varolan dosya okunamadi: {e}")
            existing_data = pd.DataFrame(columns=["Date", "Close"])
    else:
        print("Mevcut dosya yok, yeni olusturulacak.")
        existing_data = pd.DataFrame(columns=["Date", "Close"])

    periyot = periyot_sec(existing_data)

    try:
        df = pd.DataFrame(veri_cek(fon_kodu, periyot))
        if not df.empty:
            df.rename(columns={"tarih": "Date", "fiyat": "Close"}, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
            # TEFAS bazen fiyati 0 dondurur (or. TP2); gecerli fiyat ustune yazilmasin
            df = df[(df["Close"] > 0) & (df["Date"].dt.date <= today)]
        if df.empty:
            print(f"{fon_kodu} icin yeni veri yok.")
            if bayat_mi(existing_data):
                print(f"UYARI: {fon_kodu} verisi guncel degil.")
                hatali_fonlar.append(fon_kodu)
            continue
        df = df[["Date", "Close"]].sort_values("Date")
        print(f"TEFAS'tan {len(df)} satir geldi, son tarih: {df['Date'].max().date()}")
    except Exception as e:
        print(f"{fon_kodu} icin veri cekme hatasi: {e}")
        hatali_fonlar.append(fon_kodu)
        continue
    finally:
        time.sleep(ISTEK_ARASI_BEKLEME)

    # Yeni verileri birlestir
    frames = [df]
    if not existing_data.empty:
        frames.insert(0, existing_data)
    full_data = pd.concat(frames, ignore_index=True)
    full_data["Date"] = pd.to_datetime(full_data["Date"]).dt.normalize()
    # Ayni tarih iki kez varsa API'den gelen yeni degeri tut
    full_data.drop_duplicates(subset=["Date"], keep="last", inplace=True)
    full_data.sort_values("Date", inplace=True)

    # CSV kaydet
    full_data.to_csv(yedek_dosya, index=False, encoding="utf-8")
    print(f"Yeni veriler {yedek_dosya} dosyasina eklendi.")

    # PP uyumlu HTML (JSON degil) format icin CSV kopyasini olustur
    full_data.to_csv(html_csv, index=False)
    print(f"{fon_kodu} icin html_yayin klasörune CSV yazildi.")

    if bayat_mi(full_data):
        print(f"UYARI: {fon_kodu} son fiyati {full_data['Date'].max().date()} tarihli.")
        hatali_fonlar.append(fon_kodu)

# Hatali fon varsa cikis kodu 1 olur; workflow digerlerini yukleyip kirmizi biter.
if hatali_fonlar:
    print(f"---\nHatali fonlar: {', '.join(hatali_fonlar)}")
    sys.exit(1)
