# data_pipeline/crawler.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base_url = "https://www.isro.gov.in"
visited_urls = set()

os.makedirs("assets/html", exist_ok=True)
os.makedirs("assets/pdfs", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)

def crawl(url):
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Save HTML
    path = urlparse(url).path.strip("/")
    if not path:
        path = "home"
    filename = path.replace("/", "_") + ".html"
    with open(os.path.join("assets/html", filename), "w", encoding="utf-8") as f:
        f.write(response.text)

    # Handle images
    download_images(soup, url)

    # Find links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        new_url = urljoin(base_url, href)

        if new_url.endswith(".pdf"):
            download_pdf(new_url)
        elif new_url.startswith(base_url):
            crawl(new_url)

def download_pdf(pdf_url):
    filename = pdf_url.split("/")[-1]
    save_path = os.path.join("assets/pdfs", filename)
    if os.path.exists(save_path):
        return
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded PDF: {filename}")
    except Exception as e:
        print(f"[ERROR] PDF {e}")

def download_images(soup, page_url):
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if not src:
            continue
        img_url = urljoin(page_url, src)
        filename = os.path.basename(img_url)
        if not filename:
            continue
        try:
            img_data = requests.get(img_url).content
            with open(f"assets/images/{filename}", "wb") as f:
                f.write(img_data)
            print(f"Downloaded image: {filename}")
        except Exception as e:
            print(f"[ERROR] Image {e}")

if __name__ == "__main__":
    crawl(base_url)
