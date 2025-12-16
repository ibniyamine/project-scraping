import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://fr.wikipedia.org/wiki/D%C3%A9mographie_de_l%27Europe"

headers = {
    "User-Agent": "Mozilla/5.0 (Scraping éducatif)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Trouver TOUS les tableaux wikitable
tables = soup.find_all("table", class_="wikitable")

# Le bon tableau est celui avec "Rang" dans l'en-tête
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
        population = cols[2].text.strip()

        # Nettoyage
        population = (
            population.split("[")[0]
            .replace("\xa0", "")
            .replace(" ", "")
        )

        data.append({
            "Pays": pays,
            "Population": int(population)
        })

df = pd.DataFrame(data)
df.to_csv("/data/demographie_europe.csv", index=False)

print(df.head())