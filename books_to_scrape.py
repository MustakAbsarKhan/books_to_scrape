import random
import requests
from time import sleep
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs4

BASE_URL = "https://books.toscrape.com/"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})


# ---------------------------
# Get soup
# ---------------------------
def get_soup(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        return bs4(response.content, "lxml")
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None


# ---------------------------
# Extract catalogue page
# ---------------------------
def extract_catalogue_page_details(soup, current_page_url, page_number):
    books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]
        stock = book.find("p", class_="instock availability").text.strip()

        href = book.find("a")["href"]
        product_url = urljoin(current_page_url, href)

        img_src = book.find("img")["src"]
        img_url = urljoin(current_page_url, img_src)

        print(f"Title: {title}")
        print(f"Rating: {rating}")
        print(f"Price: {price}")
        print(f"Stock: {stock}")
        print(f"Product URL: {product_url}")
        print(f"Image URL: {img_url}")
        print("-" * 40)

        sleep(random.uniform(0.3, 1))


# ---------------------------
# Extract individual product details
# ---------------------------
def extract_individual_book_details(soup, current_page_url, page_number):
    books = soup.find_all("article", class_="product_pod")

    for book in books:
        href = book.find("a")["href"]
        product_url = urljoin(current_page_url, href)

        product_soup = get_soup(product_url)

        if not product_soup:
            continue

        try:
            title = product_soup.find("h1").text.strip()

            breadcrumb = product_soup.find("ul", class_="breadcrumb").find_all("li")
            category = breadcrumb[2].text.strip() if len(breadcrumb) > 2 else "Unknown"

            price = product_soup.find("p", class_="price_color").text.strip()

            stock_text = product_soup.find("p", class_="instock availability").text.strip()
            stock = stock_text.split("(")[1].split("available")[0].strip() if "(" in stock_text else "0"

            rating = product_soup.find("p", class_="star-rating")["class"][1]

            upc = product_soup.find("th", string="UPC").find_next_sibling("td").text.strip()

            desc_tag = product_soup.find("meta", {"name": "description"})
            description = desc_tag["content"].strip() if desc_tag else "No description"

            print(f"📘 Title: {title}")
            print(f"Category: {category}")
            print(f"Rating: {rating}")
            print(f"Price: {price}")
            print(f"Stock Available: {stock}")
            print(f"UPC: {upc}")
            print(f"Description: {description}")
            print("=" * 50)

            sleep(random.uniform(0.3, 1))

        except Exception as e:
            print(f"⚠️ Error parsing product: {product_url} | {e}")


# ---------------------------
# Main scraper loop
# ---------------------------
def scrape_all_pages():
    page_number = 1
    url = BASE_URL

    while url:
        print(f"\n🚀 Scraping Page {page_number}: {url}\n")

        soup = get_soup(url)

        if not soup:
            break

        extract_catalogue_page_details(soup, url, page_number)
        print(f"\n📄 Finished catalogue page {page_number}\n")

        extract_individual_book_details(soup, url, page_number)
        print(f"\n✅ Finished detail scraping for page {page_number}\n")

        # Next page logic
        next_btn = soup.find("li", class_="next")

        if next_btn:
            next_href = next_btn.find("a")["href"]
            url = urljoin(url, next_href)
            page_number += 1
        else:
            url = None

    print("\n🎉 Scraping completed!")


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    scrape_all_pages()