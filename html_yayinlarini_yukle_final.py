import os
from git import Repo

html_dir = os.path.join(os.getcwd(), "html_yayin")
repo_path = os.getcwd()

repo = Repo(repo_path)

# HTML dosyalarını fiziksel olarak sil
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        try:
            os.remove(file_path)
            print(f"Fiziksel olarak silindi: {filename}")
        except Exception as e:
            print(f"Silme hatasi: {filename} - {e}")

# Git rm güvenli kontrol
if os.path.isdir(html_dir) and os.listdir(html_dir):
    try:
        repo.git.rm("-r", "--cached", "html_yayin")
        print("html_yayin Git takibinden kaldirildi.")
    except Exception as e:
        print(f"Git rm hatasi: {e}")
else:
    print("html_yayin klasoru yok veya bos, git rm atlanacak.")

repo.git.add(all=True)
repo.index.commit("HTML dosyalari temizlendi ve guncellendi")

origin = repo.remote(name="origin")
origin.push()
