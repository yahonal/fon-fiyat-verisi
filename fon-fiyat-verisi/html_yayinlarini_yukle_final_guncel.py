import os
from git import Repo

html_dir = os.path.join(os.getcwd(), "html_yayin")
repo_path = os.getcwd()

repo = Repo(repo_path)

# 1. Yeni html dosyaları varsa Git'e ekle ve push et
if os.path.exists(html_dir) and any(f.endswith(".html") for f in os.listdir(html_dir)):
    repo.git.add(html_dir)
    repo.index.commit("html_yayin klasoru yuklendi")
    repo.remote(name="origin").push()
    print("Yeni HTML dosyalari yuklendi ve push edildi.")
else:
    print("Yeni yuklenecek HTML dosyasi bulunamadi.")
