import os
import zipfile

zip_filename = "code.zip"

# HackerRank şartnamesine göre pakete girecek dosyalar
include_files = ["README.md"]
include_dirs = ["code", "evaluation"]

print(f"[PACKAGE] Creating clean '{zip_filename}' for HackerRank submission...")

with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    # 1. README.md ekle
    for f in include_files:
        if os.path.exists(f):
            zipf.write(f, arcname=f)
            print(f"  + Added: {f}")

    # 2. code/ ve evaluation/ klasörlerini ekle (cache hariç)
    for d in include_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                if "__pycache__" in root:
                    continue
                for file in files:
                    if file.endswith(".pyc"):
                        continue
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, ".")
                    zipf.write(full_path, arcname=rel_path)
                    print(f"  + Added: {rel_path}")

print("=" * 60)
print(f"[SUCCESS] '{zip_filename}' created successfully! Size: {os.path.getsize(zip_filename)/1024:.1f} KB")
print("=" * 60)