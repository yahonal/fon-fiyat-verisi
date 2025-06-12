@echo off
cd /d "%~dp0"

echo [INFO] Otomatik yayin scripti baslatiliyor...
python otomatik_yayin_final_guncel.py

echo.
echo [INFO] Islemler tamamlandi. Cikmak icin bir tusa basin...
pause >nul
