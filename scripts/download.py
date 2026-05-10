# scripts/download.py
# Downloads the 5 required patent data files from USPTO PatentsView
# Run this with: python scripts/download.py

import os
import zipfile
import requests
from tqdm import tqdm

# Where to save the downloaded files
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Correct direct download URLs from PatentsView S3 storage
FILES = {
    "g_patent.tsv.zip": (
        "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip"
    ),
    "g_inventor_disambiguated.tsv.zip": (
        "https://s3.amazonaws.com/data.patentsview.org/download/g_inventor_disambiguated.tsv.zip"
    ),
    "g_assignee_disambiguated.tsv.zip": (
        "https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_disambiguated.tsv.zip"
    ),
    "g_patent_inventor.tsv.zip": (
        "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_inventor.tsv.zip"
    ),
    "g_patent_assignee.tsv.zip": (
        "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_assignee.tsv.zip"
    ),
}


def download_file(name, url):
    """Download one file and show a progress bar."""
    save_path = os.path.join(RAW_DIR, name)

    # Skip if already downloaded so we don't re-download
    if os.path.exists(save_path):
        print(f"  [SKIP] {name} already exists")
        return save_path

    print(f"  [DOWNLOADING] {name}")

    response = requests.get(url, stream=True, timeout=300)

    # If the server rejects the request, show the real error
    if response.status_code != 200:
        print(f"  [ERROR] Server returned {response.status_code} for {name}")
        print(f"  [ERROR] Response: {response.text[:200]}")
        return None

    # Get file size so the progress bar knows the total
    total_bytes = int(response.headers.get("content-length", 0))
    print(f"  File size: {total_bytes / 1024 / 1024:.1f} MB")

    with open(save_path, "wb") as f, tqdm(total=total_bytes, unit="B", unit_scale=True) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    print(f"  [SAVED] {save_path}")
    return save_path


def unzip_file(zip_path):
    """Unzip a downloaded file into the raw folder."""
    print(f"  [UNZIPPING] {os.path.basename(zip_path)}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(RAW_DIR)
    print(f"  [DONE] Extracted to data/raw/")


def main():
    print("\n========================================")
    print("  Downloading USPTO Patent Data Files")
    print("========================================\n")

    for filename, url in FILES.items():
        zip_path = download_file(filename, url)
        if zip_path:                   # only unzip if download succeeded
            unzip_file(zip_path)
        print()

    print("All files downloaded and extracted.")
    print("Next step: python scripts/clean.py\n")


if __name__ == "__main__":
    main()