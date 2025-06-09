import os
from git import Repo

html_dir = os.path.join(os.getcwd(), "html_yayin")
repo_path = os.getcwd()

repo = Repo(repo_path)

# 1. Git'in takip ettigi tum mevcut .html dosyalarini bul ve sil
tracked_files = [item.a_path for item in repo.index.diff("HEAD") if item.a_path.endswith(".html")]
html_files_in_repo = [f for f in repo.git.ls_files().splitlines() if f.endswith(".html")]

for file_path in html_files_in_repo:
    try:
        os.remove(file_path)
        print(f"Git takipli eski HTML silindi: {file_path}")
    except Exception as e:
        print(f"Silinemedi: {file_path} - {e}")

# 2. Git'e bu silmeleri bildir
repo.git.add(update=True)
repo.index.commit("Onceki tum HTML dosyalari silindi")

# 3. Yeni html dosyalarini html_yayin klasorunden ekle
new_html_files = [
    os.path.join("html_yayin", f)
    for f in os.listdir(html_dir)
    if f.endswith(".html")
]

if new_html_files:
    repo.git.add(html_dir)
    repo.index.commit("Yeni HTML dosyalari yüklendi")
    origin = repo.remote(name="origin")
    origin.push()
    print("Yeni HTML dosyalari yuklendi ve push edildi.")
else:
    print("Yeni yuklenecek HTML dosyasi bulunamadi.")
