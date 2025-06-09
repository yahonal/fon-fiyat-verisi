import os
from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

tefas = Crawler()

with open("fund_list.dat", "r") as file:
    fonlar = [line.strip() for line in file if line.strip()]

today = datetime.today().date()
last_business_day = (pd.Timestamp(today) - pd.tseries.offsets.BDay(1)).date()
default_start_date = pd.to_datetime("2020-06-28").date()

for fon_adi in fonlar:
    print(f"---\n{fon_adi} icin islem baslatiliyor...")

    yedek_dosya = f"{fon_adi}_fund.csv"

    if os.path.exists(yedek_dosya):
        print(f"Dosya {yedek_dosya} mevcut. Varolan veriler okunuyor...")
        try:
            existing_data = pd.read_csv(yedek_dosya, parse_dates=['Date'])
            last_recorded_date = existing_data['Date'].max().date()
            print(f"Dosyadaki son tarih: {last_recorded_date}")
            new_start_date = last_recorded_date + timedelta(days=1)
            print(f"Yeni veri cekmeye baslanacak tarih: {new_start_date}")
        except Exception as e:
            print(f"Dosya okuma hatasi: {e}. Varsayilan baslangic tarihi ({default_start_date}) kullanilacak.")
            existing_data = pd.DataFrame()
            new_start_date = default_start_date
        if new_start_date < default_start_date:
            new_start_date = default_start_date
    else:
        print(f"Dosya {yedek_dosya} bulunamadi. Tum veriler {default_start_date}'den cekilecek.")
        existing_data = pd.DataFrame()
        new_start_date = default_start_date

    if new_start_date > last_business_day:
        print(f"Yeni baslangic tarihi ({new_start_date}) son is gununden ({last_business_day}) sonraya denk geldi. Yeni veri cekilmeyecek.")
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
        new_data_frames.append(df)

    if new_data_frames:
        new_data = pd.concat(new_data_frames, ignore_index=True)
        if not existing_data.empty:
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            combined_data.drop_duplicates(subset=['Date'], inplace=True)
            combined_data.sort_values("Date", inplace=True)
        else:
            combined_data = new_data

        # Kolon kontrolü
        date_col = [col for col in combined_data.columns if col.lower() == "date"]
        price_col = [col for col in combined_data.columns if col.lower() == "price"]

        if not date_col or not price_col:
            raise ValueError("Gerekli 'date' ve 'price' kolonlari bulunamadi.")

        combined_data_pp = combined_data[[date_col[0], price_col[0]]].copy()
        combined_data_pp.columns = ["Date", "Close"]

        combined_data_pp["Date"] = pd.to_datetime(combined_data_pp["Date"]).dt.strftime("%Y-%m-%d")
        combined_data_pp.to_csv(yedek_dosya, index=False, encoding='utf-8')
        print(f"Veriler {yedek_dosya} dosyasina kaydedildi.")
    else:
        print(f"{fon_adi} icin yeni veri bulunamadi.")
