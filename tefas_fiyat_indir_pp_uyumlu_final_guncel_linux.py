#!/usr/bin/env python3
import os
import shutil
import requests
import pandas as pd
from datetime import datetime, timedelta

# html_yayin klasorunu bastan temizle
html_dir = os.path.join(os.getcwd(), "html_yayin")
if os.path.exists(html_dir):
    shutil.rmtree(html_dir)
    print("html_yayin klasoru fundfy scripti basinda silindi.")
os.makedirs(html_dir, exist_ok=True)

with open("fund_list.dat", "r") as file:
    fonlar = [line.strip() for line in file if line.strip()]

today = datetime.today().date()
last_business_day = (pd.Timestamp(today) - pd.tseries.offsets.BDay(1)).date()
default_start_date = pd.to_datetime("2015-01-01").date()

for fon_kodu in fonlar:
    print(f"---\n{fon_kodu} icin islem baslatiliyor...")

    yedek_dosya = f"{fon_kodu}_fund.csv"

    if os.path.exists(yedek_dosya):
        try:
            existing_data = pd.read_csv(yedek_dosya, parse_dates=["Date"])
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
        new_start_date = existing_data["Date"].max().date() + timedelta(days=1)

    if new_start_date > last_business_day:
        print(f"Yeni veri yok ({new_start_date} > {last_business_day})")
        continue

    # Fundfy sadece genis araliklar destekliyor, tum aralik icin tek seferde cek
    from_date = new_start_date.strftime("%Y-%m-%d")
    to_date = last_business_day.strftime("%Y-%m-%d")
    url = f"https://api.fundfy.net/api/v1/fund/detail/graph/chart/{fon_kodu}?isDollar=false&fromDate={from_date}&toDate={to_date}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        df = pd.DataFrame(json_data["data"])
        if df.empty:
            print(f"{fon_kodu} icin yeni veri yok.")
            continue
        df.rename(columns={"date": "Date", "value": "Close"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[["Date", "Close"]].sort_values("Date")
    except Exception as e:
        print(f"{fon_kodu} icin veri cekme hatasi: {e}")
        continue

    # Yeni verileri birlestir
    frames = [df]
    if not existing_data.empty:
        frames.insert(0, existing_data)
    full_data = pd.concat(frames, ignore_index=True)
    full_data.drop_duplicates(subset=["Date"], inplace=True)
    full_data.sort_values("Date", inplace=True)

    # CSV kaydet
    full_data.to_csv(yedek_dosya, index=False, encoding="utf-8")
    print(f"Yeni veriler {yedek_dosya} dosyasina eklendi.")

    # PP uyumlu HTML (JSON degil) format icin CSV kopyasini olustur
    html_csv = os.path.join(html_dir, f"{fon_kodu}.csv")
    full_data.to_csv(html_csv, index=False)
    print(f"{fon_kodu} icin html_yayin klasörune CSV yazildi.")
