import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

# html_yayin silinmez: otomatik calismada gecmis veri buradaki CSV'lerden okunur.
# Bir fon hata verirse onceki yayini da yerinde kalir.
html_dir = os.path.join(os.getcwd(), "html_yayin")
os.makedirs(html_dir, exist_ok=True)

with open("fund_list.dat", "r") as file:
    fonlar = [line.strip() for line in file if line.strip()]

today = datetime.today().date()
# Fon fiyatlari o gunun tarihiyle yayinlanir (onceki gunun kapanisi ile hesaplanir),
# bu yuzden bitis tarihi olarak bugunu kullaniyoruz. toDate haric tutuluyorsa diye +1 gun.
end_date = today + timedelta(days=1)
default_start_date = pd.to_datetime("2015-01-01").date()
# Son birkac gunu her seferinde yeniden cek: hem dar aralik sorununu onler
# hem de sonradan duzeltilen fiyatlari gunceller.
GERI_BAKIS_GUN = 10
# Son fiyat bundan eskiyse fon hatali sayilir (uzun bayram tatilleri icin 10 gun).
MAKS_GECIKME_GUN = 10
DENEME_SAYISI = 3
ISTEK_ZAMAN_ASIMI = 30  # saniye

hatali_fonlar = []


def bayat_mi(data):
    if data.empty:
        return True
    return (today - data["Date"].max().date()).days > MAKS_GECIKME_GUN


def veri_cek(url, headers):
    for deneme in range(1, DENEME_SAYISI + 1):
        try:
            response = requests.get(url, headers=headers, timeout=ISTEK_ZAMAN_ASIMI)
            response.raise_for_status()
            return response.json()["data"]
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

    if existing_data.empty:
        new_start_date = default_start_date
    else:
        new_start_date = existing_data["Date"].max().date() - timedelta(days=GERI_BAKIS_GUN)

    # Fundfy sadece genis araliklar destekliyor, tum aralik icin tek seferde cek
    from_date = new_start_date.strftime("%Y-%m-%d")
    to_date = end_date.strftime("%Y-%m-%d")
    url = f"https://api.fundfy.net/api/v1/fund/detail/graph/chart/{fon_kodu}?isDollar=false&fromDate={from_date}&toDate={to_date}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        df = pd.DataFrame(veri_cek(url, headers))
        if df.empty:
            print(f"{fon_kodu} icin yeni veri yok.")
            if bayat_mi(existing_data):
                print(f"UYARI: {fon_kodu} verisi guncel degil.")
                hatali_fonlar.append(fon_kodu)
            continue
        df.rename(columns={"date": "Date", "value": "Close"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        if df["Date"].dt.tz is not None:
            df["Date"] = df["Date"].dt.tz_localize(None)
        df["Date"] = df["Date"].dt.normalize()
        df = df[df["Date"].dt.date <= today]  # gelecek tarihli kayit varsa at
        df = df[["Date", "Close"]].sort_values("Date")
        print(f"API'den {len(df)} satir geldi, son tarih: {df['Date'].max().date() if not df.empty else '-'}")
    except Exception as e:
        print(f"{fon_kodu} icin veri cekme hatasi: {e}")
        hatali_fonlar.append(fon_kodu)
        continue

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
