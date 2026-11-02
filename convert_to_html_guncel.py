import os
import pandas as pd

csv_folder = os.getcwd()
html_output_dir = os.path.join(csv_folder, "html_yayin")
os.makedirs(html_output_dir, exist_ok=True)

converted_html_files = []

# Kaynak html_yayin CSV'leridir: fiyati cekilemeyen fonun yayini eski yedekle ezilmez.
for filename in os.listdir(html_output_dir):
    if filename.endswith(".csv"):
        fund_code = filename.replace(".csv", "")
        df = pd.read_csv(os.path.join(html_output_dir, filename))

        html_table = df.to_html(index=False)
        html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{fund_code} Historical Data</title>
</head>
<body>
<h2>{fund_code} Historical Quotes</h2>
{html_table}
</body>
</html>"""

        html_filename = os.path.join(html_output_dir, f"{fund_code}.html")
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_full)
        converted_html_files.append(html_filename)