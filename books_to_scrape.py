"""
Async Web Scraper with:
- Concurrency control (Semaphore)
- Dynamic rate limiting (auto speed up / slow down)
- Adaptive delay (adjust speed based on server response time)
- Clean structure and beginner-friendly comments

Target site: https://books.toscrape.com/
"""

import asyncio
import random
import aiohttp
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs4


# =========================================================
# 🔧 CONFIGURATION
# =========================================================

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Initial concurrency (how many requests at once)
concurrency_limit = 5
semaphore = asyncio.Semaphore(concurrency_limit)

# Counters used for dynamic rate control
success_count = 0
fail_count = 0

# ---------------------------
# 🕒 Adaptive Delay Settings
# ---------------------------
delay = 0.2          # starting delay between requests
min_delay = 0.1      # fastest allowed
max_delay = 3        # slowest allowed


# =========================================================
# ⚙️ DYNAMIC CONCURRENCY CONTROL
# =========================================================

def adjust_concurrency():
    """
    Dynamically adjust how many requests run in parallel.

    - Many failures → reduce concurrency (slow down)
    - Many successes → increase concurrency (speed up)
    """
    global concurrency_limit, semaphore, success_count, fail_count

    if fail_count >= 3:
        concurrency_limit = max(1, concurrency_limit - 1)
        semaphore = asyncio.Semaphore(concurrency_limit)

        print(f"🐢 Slowing down → concurrency = {concurrency_limit}")
        fail_count = 0

    elif success_count >= 10:
        concurrency_limit += 1
        semaphore = asyncio.Semaphore(concurrency_limit)

        print(f"🚀 Speeding up → concurrency = {concurrency_limit}")
        success_count = 0


# =========================================================
# ⚙️ ADAPTIVE DELAY CONTROL
# =========================================================

def adjust_delay(response_time=None, status=None):
    """
    Dynamically adjust delay between requests.

    Logic:
    - Slow response → increase delay
    - Blocked (429/403) → increase delay more
    - Fast response → decrease delay
    """
    global delay

    # 🚫 Blocked → aggressively slow down
    if status in (403, 429):
        delay = min(max_delay, delay + 0.5)
        print(f"🚫 Block detected → delay = {round(delay, 2)}s")

    # 🐢 Slow server → increase delay
    elif response_time and response_time > 1.5:
        delay = min(max_delay, delay + 0.2)
        print(f"🐢 Slow response ({round(response_time,2)}s) → delay = {round(delay, 2)}s")

    # 🚀 Fast server → reduce delay
    elif response_time and response_time < 0.5:
        delay = max(min_delay, delay - 0.05)
        print(f"🚀 Fast response ({round(response_time,2)}s) → delay = {round(delay, 2)}s")


# =========================================================
# 🌐 FETCH HTML (CORE ASYNC FUNCTION)
# =========================================================

async def fetch_soup(session, url):
    """
    Fetch a page and return BeautifulSoup object.

    Features:
    - Concurrency control (Semaphore)
    - Dynamic concurrency adjustment
    - Adaptive delay (based on response time)
    """

    global success_count, fail_count

    async with semaphore:
        start_time = time.perf_counter()  # start timer

        try:
            async with session.get(url) as response:

                end_time = time.perf_counter()
                response_time = end_time - start_time

                # ✅ Successful request
                if response.status == 200:
                    html = await response.text()
                    success_count += 1

                    adjust_concurrency()
                    adjust_delay(response_time=response_time)

                    # Apply adaptive delay (non-blocking)
                    await asyncio.sleep(delay)

                    return bs4(html, "lxml")

                # 🚫 Blocked
                elif response.status in (403, 429):
                    print(f"🚫 Blocked: {url} | {response.status}")
                    fail_count += 1

                    adjust_concurrency()
                    adjust_delay(status=response.status)

                    return None

                # ⚠️ Other failures
                else:
                    print(f"⚠️ Failed: {url} | {response.status}")
                    fail_count += 1

                    adjust_concurrency()
                    adjust_delay(response_time=response_time)

                    return None

        except Exception as e:
            print(f"⚠️ Error fetching {url} | {e}")
            fail_count += 1

            adjust_concurrency()
            adjust_delay()

            return None


# =========================================================
# 📄 PARSE CATALOGUE PAGE
# =========================================================

def parse_catalogue_page(soup, base_url):
    """
    Extract book summaries + collect product URLs
    """

    books = soup.find_all("article", class_="product_pod")
    product_urls = []

    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]
        stock = book.find("p", class_="instock availability").text.strip()

        relative_url = book.find("a")["href"]
        product_url = urljoin(base_url, relative_url)
        product_urls.append(product_url)

        print(f"Title: {title}")
        print(f"Rating: {rating}")
        print(f"Price: {price}")
        print(f"Stock: {stock}")
        print(f"Product URL: {product_url}")
        print("-" * 40)

    return product_urls


# =========================================================
# 📘 PARSE PRODUCT PAGE
# =========================================================

async def parse_product_page(session, product_url):
    """
    Fetch and extract detailed product info
    """

    soup = await fetch_soup(session, product_url)

    if not soup:
        return

    try:
        title = soup.find("h1").text.strip()

        breadcrumb = soup.find("ul", class_="breadcrumb").find_all("li")
        category = breadcrumb[2].text.strip() if len(breadcrumb) > 2 else "Unknown"

        price = soup.find("p", class_="price_color").text.strip()

        stock_text = soup.find("p", class_="instock availability").text.strip()
        stock = (
            stock_text.split("(")[1].split("available")[0].strip()
            if "(" in stock_text else "0"
        )

        rating = soup.find("p", class_="star-rating")["class"][1]

        upc = soup.find("th", string="UPC").find_next_sibling("td").text.strip()

        desc_tag = soup.find("meta", {"name": "description"})
        description = desc_tag["content"].strip() if desc_tag else "No description"

        print(f"📘 Title: {title}")
        print(f"Category: {category}")
        print(f"Rating: {rating}")
        print(f"Price: {price}")
        print(f"Stock Available: {stock}")
        print(f"UPC: {upc}")
        print(f"Description: {description}")
        print("=" * 50)

    except Exception as e:
        print(f"⚠️ Parsing error: {product_url} | {e}")


# =========================================================
# 🚀 MAIN SCRAPER LOOP
# =========================================================

async def scrape_all_pages():
    """
    Workflow:
    1. Loop catalogue pages
    2. Extract product URLs
    3. Scrape product pages concurrently
    """

    page_number = 1
    current_url = BASE_URL

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        while current_url:
            print(f"\n🚀 Scraping Page {page_number}: {current_url}\n")

            soup = await fetch_soup(session, current_url)
            if not soup:
                break

            product_urls = parse_catalogue_page(soup, current_url)

            print(f"\n📄 Finished catalogue page {page_number}\n")

            tasks = [parse_product_page(session, url) for url in product_urls]
            await asyncio.gather(*tasks)

            print(f"\n✅ Finished detail scraping for page {page_number}\n")

            next_btn = soup.find("li", class_="next")
            if next_btn:
                next_url = next_btn.find("a")["href"]
                current_url = urljoin(current_url, next_url)
                page_number += 1
            else:
                current_url = None

    print("\n🎉 Scraping completed!")


# =========================================================
# ▶️ ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(scrape_all_pages())