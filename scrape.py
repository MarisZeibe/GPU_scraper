import requests
import time
from bs4 import BeautifulSoup as bs
import csv

URL = "https://www.1a.lv/c/datoru-komponentes-tikla-produkti/komponentes/video-kartes/2vs"
PAGES = "pages/"
DATA = "data/"

def save(url, file):
    output = requests.get(url)
    if output.status_code == 200:
        with open(f"{PAGES}{file}", 'w', encoding='UTF-8') as f:
            f.write(output.text)
    else:
        print(f"ERROR: Status code {output.status_code}")

def download_pages(count):
    for i in range(1, count + 1):
        save(f"{URL}?page={i}", f"{i}.html")
        time.sleep(1)

def info(file):
    data = []
    with open(file, 'r', encoding='UTF-8') as f:
        html = f.read()

    soup = bs(html, "html.parser")

    main = soup.find_all(class_="catalog-page")[0]

    products = main.find_all(class_="catalog-taxons-product")

    models = [model.text.replace('\n', '') for model in main.find(attr_id="3297").find_all(class_="catalog-taxons-filter-multiselect__link-label list-filterable__label")][1:-3]

    for item in products:
        product = {}
        product["name"] = item.find(attrs={"class": "gtm-categories"})["data-name"]
        product["price"] = item.find(attrs={"class": "gtm-categories"})["data-price"]
        product["image"] = item.find("img")["src"]

        listItems = {}

        for list_item in item.find_all("li"):
            text = list_item.text.replace('\n', '')
            listItems[text.split(":")[0]] = text.split(":")[1]
        
        if not "Atmiņas taktiskā frekvence" in listItems or not "Video kartes atmiņa" in listItems:
            continue

        product["clock speed"] = listItems["Atmiņas taktiskā frekvence"].replace("MHz", '')
        product["VRAM"] = listItems["Video kartes atmiņa"].replace("GB", '')
        product["manufacturer"] = product["name"].split(" ")[1]
        
        for model in models:
            if model in product["name"]:
                product["model"] = model

        if not "model" in product:
            continue

        data.append(product)

    return data

def save_data(data):
    with open(f"{DATA}GPU.csv", 'w', encoding="UTF-8", newline="") as f:
        header = ["name", "price", "image", "clock speed", "VRAM", "manufacturer", "model"]
        w = csv.DictWriter(f, fieldnames= header)
        w.writeheader()
        for item in data:
            w.writerow(item)

def get_data(amount):
    all_data = []
    for i in range(1, amount + 1):
        file = f"{PAGES}{i}.html"
        data = info(file)
        all_data += data

    save_data(all_data)

# download_pages(3)

get_data(3)
