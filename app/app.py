import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3
import os

# ==============================
# CONFIG
# ==============================
URL = "https://fr.wikipedia.org/wiki/D%C3%A9mographie_de_l%27Europe"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Scraping éducatif)"
}

LOCAL_FILE_PATH = "/data/demographie_europe.csv"

S3_BUCKET_NAME = "m2dsia-anoir-ibniyamine"   
S3_OBJECT_NAME = "europe/demographie_europe.csv"

# ==============================
# SCRAPING
# ==============================
response = requests.get(URL, headers=HEADERS, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table", class_="wikitable")

target_table = None
for table in tables:
    headers = [th.text.strip() for th in table.find_all("th")]
    if "Rang" in headers and "Pays" in headers:
        target_table = table
        break

if not target_table:
    raise Exception("Tableau non trouvé")

data = []

for row in target_table.find_all("tr")[1:]:
    cols = row.find_all("td")
    if len(cols) >= 3:
        pays = cols[1].text.strip()
        population = (
            cols[2].text.strip()
            .split("[")[0]
            .replace("\xa0", "")
            .replace(" ", "")
        )

        data.append({
            "Pays": pays,
            "Population": int(population)
        })

df = pd.DataFrame(data)

# Sauvegarde locale (volume Docker)
df.to_csv(LOCAL_FILE_PATH, index=False, encoding="utf-8")

print("Fichier CSV généré avec succès ✅")
print(df.head())

# ==============================
# UPLOAD S3
# ==============================
def upload_file_s3(file_path, bucket_name, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3 = boto3.client("s3")

    s3.upload_file(file_path, bucket_name, object_name)
    print(f"Fichier envoyé sur S3 : s3://{bucket_name}/{object_name} ✅")


upload_file_s3(
    file_path=LOCAL_FILE_PATH,
    bucket_name=S3_BUCKET_NAME,
    object_name=S3_OBJECT_NAME
)
