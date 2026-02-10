from huggingface_hub import snapshot_download

# Menentukan folder yang ingin diunduh
snapshot_download(
    repo_id="einrafh/hnm-fashion-recommendations-data",
    repo_type="dataset",
    allow_patterns="data/raw/images/035/*",  # Hanya ambil folder images
    local_dir="./hnm-images",  # Nama folder tujuan
    resume_download=True,  # Bisa lanjut jika koneksi mati
)
print("Unduhan selesai! Silakan cek folder hnm-images 📸")
