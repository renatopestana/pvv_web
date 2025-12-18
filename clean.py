import os
import shutil

def remove_pycache_and_pyc(root="."):
    removed_dirs = []
    removed_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Remover diretórios __pycache__
        for d in list(dirnames):
            if d == "__pycache__":
                full = os.path.join(dirpath, d)
                try:
                    shutil.rmtree(full)
                    removed_dirs.append(full)
                except Exception as e:
                    print(f"Falha ao remover {full}: {e}")
        # Remover arquivos .pyc
        for f in filenames:
            if f.endswith(".pyc"):
                full = os.path.join(dirpath, f)
                try:
                    os.remove(full)
                    removed_files.append(full)
                except Exception as e:
                    print(f"Falha ao remover {full}: {e}")

    print(f"Removidos diretórios __pycache__: {len(removed_dirs)}")
    print(f"Removidos arquivos .pyc: {len(removed_files)}")

if __name__ == "__main__":
    remove_pycache_and_pyc(".")
