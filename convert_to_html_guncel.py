import os
import pandas as pd

csv_folder = os.getcwd()
html_output_dir = os.path.join(csv_folder, "html_yayin")
os.makedirs(html_output_dir, exist_ok=True)

converted_html_files = []

for filename in os.listdir(csv_folder):
    if filename.endswith("_fund.csv"):
        fund_code = filename.replace("_fund.csv", "")
        df = pd.read_csv(os.path.join(csv_folder, filename))

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