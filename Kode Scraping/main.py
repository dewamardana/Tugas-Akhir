import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import time

session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[502, 503, 504, 429],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

names = [
    "Boletus edulis",
    "Cerioporus squamosus",
    "Coprinus comatus",
    "Lactarius deliciosus",
    "Laetiporus sulphureus",
    "Macrolepiota procera",
    "Amanita muscaria",
    "Amanita pantherina",
    "Coprinopsis atramentaria",
    "Hypholoma fasciculare",
    "Lactarius torminosus",
    "Paxillus involutus",
]

taxon_ids = [
    48701,
    940028,
    47392,
    155197,
    53713,
    63401,
    48715,
    48418,
    48521,
    48767,
    351313,
    55941,
]

max_images_list = [3273] * 12

os.makedirs("dataset_image", exist_ok=True)

for i in range(len(names)):
    name = names[i]
    taxon_id = taxon_ids[i]
    max_images = max_images_list[i]
    page = 1

    folder_path = f"dataset_image/{name}"
    os.makedirs(folder_path, exist_ok=True)

    downloaded_count = (
        len(os.listdir(folder_path)) if os.path.exists(folder_path) else 0
    )

    print(f"Mengunduh gambar untuk {name} (target: {max_images} gambar)...")

    while downloaded_count < max_images and page <= 500:
        try:
            url = (
                f"https://api.inaturalist.org/v1/observations"
                f"?taxon_id={taxon_id}&page={page}&per_page=30"
            )
            response = session.get(url, timeout=10)
            data = response.json()

            if not data["results"]:
                break

            for obs in data["results"]:
                if not obs["photos"]:
                    continue

                photo_url = obs["photos"][0]["url"].replace("square", "original")
                image_path = f"{folder_path}/{obs['id']}.jpg"

                if os.path.exists(image_path):
                    continue

                img_response = session.get(photo_url, timeout=10)
                if img_response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(img_response.content)
                    downloaded_count += 1

                if downloaded_count >= max_images:
                    break

                time.sleep(0.3)

            page += 1
            time.sleep(0.5)

        except requests.exceptions.SSLError:
            time.sleep(3)

        except requests.exceptions.RequestException:
            time.sleep(3)

    print(f"Selesai: {downloaded_count} gambar diunduh untuk {name}.")

print("Semua gambar selesai diunduh.")
