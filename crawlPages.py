import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base_url = "https://www.isro.gov.in"
visited_urls = set()

# Create folders
os.makedirs("html", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

def crawl(url):
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error:", e)
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Save HTML locally
    path = urlparse(url).path.strip("/")
    if not path:
        path = "home"
    filename = path.replace("/", "_") + ".html"
    with open(os.path.join("html", filename), "w", encoding="utf-8") as f:
        f.write(response.text)

    # Find links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        new_url = urljoin(base_url, href)

        # Download PDFs
        if new_url.endswith(".pdf"):
            download_pdf(new_url)
        # Crawl internal links
        elif new_url.startswith(base_url):
            crawl(new_url)

def download_pdf(pdf_url):
    filename = pdf_url.split("/")[-1]
    save_path = os.path.join("pdfs", filename)

    if os.path.exists(save_path):
        print("Already downloaded:", filename)
        return

    try:
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print("Downloaded PDF:", filename)
    except Exception as e:
        print("PDF download error:", e)

crawl(base_url)
