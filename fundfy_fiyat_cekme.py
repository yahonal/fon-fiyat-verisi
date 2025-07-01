import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fon bilgisi ve tarih aralığı
fon_kodu = "MAC"
from_date = "2015-01-01"
to_date = "2025-06-22"
is_dollar = "false"

# Fundfy API URL
url = f"https://api.fundfy.net/api/v1/fund/detail/graph/chart/{fon_kodu}?isDollar={is_dollar}&fromDate={from_date}&toDate={to_date}"
headers = {"User-Agent": "Mozilla/5.0"}

# API çağrısı
response = requests.get(url, headers=headers)
data = response.json()

# JSON içeriğini kontrol et
print("Anahtarlar:", data.keys())

# Gerçek veri burada: data["data"]
df = pd.DataFrame(data["data"])
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# İlk birkaç satırı göster
print(df.head())

# İsteğe bağlı: Görselleştirme
df['value'].plot(title=f"{fon_kodu} Fon Fiyatı", figsize=(12, 5))
plt.ylabel("Fiyat")
plt.grid(True)
plt.show()

# Fon fiyatını görselleştir
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(df.index, df['value'], label=fon_kodu, linewidth=2)
plt.title(f"{fon_kodu} Fon Fiyatı", fontsize=16)
plt.xlabel("Tarih", fontsize=12)
plt.ylabel("Fiyat", fontsize=12)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Fon fiyatlarını CSV dosyasına kaydet
csv_dosya_adi = f"{fon_kodu}_fiyatlari.csv"
df.to_csv(csv_dosya_adi)
print(f"CSV dosyası oluşturuldu: {csv_dosya_adi}")
