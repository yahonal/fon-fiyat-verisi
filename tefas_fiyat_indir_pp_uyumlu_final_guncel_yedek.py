
import os
import shutil
from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

# html_yayin klasorunu bastan temizle
html_dir = os.path.join(os.getcwd(), "html_yayin")
if os.path.exists(html_dir):
    shutil.rmtree(html_dir)
    print("html_yayin klasoru tefas scripti basinda silindi.")

tefas = Crawler()

with open("fund_list.dat", "r") as file:
    fonlar = [line.strip() for line in file if line.strip()]

today = datetime.today().date()
last_business_day = (pd.Timestamp(today) - pd.tseries.offsets.BDay(1)).date()
default_start_date = pd.to_datetime("2020-06-28").date()

for fon_adi in fonlar:
    print(f"---\n{fon_adi} icin islem baslatiliyor...")

    yedek_dosya = f"{fon_adi}_fund.csv"

    # Mevcut CSV varsa oku
    if os.path.exists(yedek_dosya):
        try:
            existing_data = pd.read_csv(yedek_dosya, parse_dates=['Date'])
            print(f"Dosya mevcut, {len(existing_data)} satir yüklendi.")
        except Exception as e:
            print(f"Hata: Varolan dosya okunamadi: {e}")
            existing_data = pd.DataFrame(columns=["Date", "Close"])
    else:
        print("Mevcut dosya yok, yeni olusturulacak.")
        existing_data = pd.DataFrame(columns=["Date", "Close"])

    if existing_data.empty:
        new_start_date = default_start_date
    else:
        new_start_date = existing_data['Date'].max().date() + timedelta(days=1)

    if new_start_date > last_business_day:
        print(f"Yeni veri bulunmuyor ({new_start_date} > {last_business_day})")
        continue

    monthly_starts = pd.date_range(start=new_start_date, end=last_business_day, freq='MS').date
    if new_start_date not in monthly_starts:
        monthly_starts = [new_start_date] + list(monthly_starts)

    new_data_frames = []
    for i, month_start in enumerate(monthly_starts):
        if i < len(monthly_starts) - 1:
            next_month_start = monthly_starts[i + 1]
            interval_end = next_month_start - timedelta(days=1)
        else:
            interval_end = last_business_day

        if month_start > last_business_day:
            break

        print(f"{fon_adi} icin {month_start} ile {interval_end} arasi veri cekiliyor...")
        df = tefas.fetch(start=str(month_start), end=str(interval_end), name=fon_adi, columns=["date", "price"])
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values("date", ascending=True, inplace=True)
        if not df.empty:
            df.columns = ["Date", "Close"]
            new_data_frames.append(df)
        else:
            print(f"{fon_adi} icin {month_start} - {interval_end} arasi veri bulunamadi.")

    if new_data_frames:
        new_data = pd.concat(new_data_frames, ignore_index=True)
        # Concat uyarısını engelle: sadece boş olmayanları birleştir
        frames = [df for df in [existing_data, new_data] if not df.empty]
        if frames:
            full_data = pd.concat(frames, ignore_index=True)
            full_data.drop_duplicates(subset=["Date"], inplace=True)
            full_data.sort_values("Date", inplace=True)
            full_data.to_csv(yedek_dosya, index=False, encoding='utf-8')
            print(f"Yeni veriler {yedek_dosya} dosyasina eklendi.")
        else:
            print(f"{fon_adi} icin hicbir veri birlestirilemedi.")
    else:
        print(f"{fon_adi} icin hic yeni veri bulunamadi, dosya degistirilmeyecek.")
