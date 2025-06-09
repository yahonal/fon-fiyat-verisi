import os
from git import Repo

html_dir = os.path.join(os.getcwd(), "html_yayin")
repo_path = os.getcwd()

repo = Repo(repo_path)

# 1. Git tarafında takip edilen .html dosyalarını listele
html_files_in_repo = [f for f in repo.git.ls_files().splitlines() if f.endswith(".html")]

# 2. Bunları fiziksel olarak sil (önceki html'ler)
for file_path in html_files_in_repo:
    try:
        os.remove(file_path)
        print(f"Eski HTML silindi: {file_path}")
    except Exception as e:
        print(f"Silinemedi: {file_path} - {e}")

# 3. Silmeleri sahnele ve commit et
repo.git.add("-A")
repo.index.commit("Onceki HTML dosyalari silindi")

# 4. convert_to_html.py ile yeniden uretilen dosyalar dizine gelir
# Tekrar html_yayin klasorundeki yeni dosyalar sahnelenir
if os.path.isdir(html_dir) and any(f.endswith(".html") for f in os.listdir(html_dir)):
    repo.git.add(html_dir)
    repo.index.commit("Yeni HTML dosyalari yuklendi")
    origin = repo.remote(name="origin")
    origin.push()
    print("Yeni HTML dosyalari yuklendi ve push edildi.")
else:
    print("Yeni yuklenecek HTML dosyasi bulunamadi.")