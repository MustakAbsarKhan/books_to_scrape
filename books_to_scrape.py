"""
=========================================================
ASYNC WEB SCRAPER (BEGINNER-FRIENDLY VERSION)
=========================================================

This script scrapes book data from:
👉 https://books.toscrape.com/

It demonstrates:
- Async scraping (aiohttp)
- Concurrency control (Semaphore)
- Adaptive delay (changes speed based on server response)
- Dynamic performance tuning
- CSV export (final dataset)

---------------------------------------------------------
WHY THIS SCRIPT EXISTS:
---------------------------------------------------------
Real-world websites:
- block too many requests
- respond differently based on load
- require controlled scraping speed

So this scraper:
👉 automatically adapts like a "smart system"
"""

# =========================================================
# 📦 IMPORTS (libraries used)
# =========================================================

import asyncio          # for async programming (concurrent tasks)
import aiohttp         # for async HTTP requests
import time            # to measure response speed
import csv             # for saving final data to CSV
from urllib.parse import urljoin  # to build full URLs
from bs4 import BeautifulSoup as bs4  # to parse HTML


# =========================================================
# 🌍 BASE CONFIGURATION
# =========================================================

BASE_URL = "https://books.toscrape.com/"

# Headers make our request look like a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


# =========================================================
# ⚡ CONCURRENCY CONTROL (HOW MANY REQUESTS AT ONCE)
# =========================================================

concurrency_limit = 5
semaphore = asyncio.Semaphore(concurrency_limit)

"""
WHY THIS EXISTS:
- Without this → we may send TOO many requests at once
- Websites may block us (429 / 403 errors)
"""


# =========================================================
# 📊 PERFORMANCE TRACKING VARIABLES
# =========================================================

success_count = 0
fail_count = 0

"""
WHY THIS EXISTS:
We use these counters to:
- detect if scraping is too fast (success)
- detect if scraping is getting blocked (fail)
"""


# =========================================================
# 🕒 ADAPTIVE DELAY SETTINGS
# =========================================================

delay = 0.2        # starting delay between requests
min_delay = 0.1    # fastest allowed speed
max_delay = 3      # slowest allowed speed

"""
WHY THIS EXISTS:
- Too fast → risk blocking
- Too slow → inefficient scraping
So we automatically adjust speed.
"""


# =========================================================
# ⚙️ CONCURRENCY ADAPTATION LOGIC
# =========================================================

def adjust_concurrency():
    """
    This function changes how many requests run at the same time.

    THINK OF IT LIKE:
    - too many errors → slow down system
    - too many successes → speed up system
    """

    global concurrency_limit, semaphore, success_count, fail_count

    # 🚫 If scraping is failing often → reduce speed
    if fail_count >= 3:
        concurrency_limit = max(1, concurrency_limit - 1)
        semaphore = asyncio.Semaphore(concurrency_limit)

        print(f"🐢 Slowing down → concurrency = {concurrency_limit}")

        fail_count = 0  # reset counter

    # 🚀 If everything is smooth → increase speed
    elif success_count >= 10:
        concurrency_limit += 1
        semaphore = asyncio.Semaphore(concurrency_limit)

        print(f"🚀 Speeding up → concurrency = {concurrency_limit}")

        success_count = 0  # reset counter


# =========================================================
# ⚙️ ADAPTIVE DELAY LOGIC (VERY IMPORTANT)
# =========================================================

def adjust_delay(response_time=None, status=None):
    """
    This function adjusts WAIT TIME between requests.

    WHY THIS IS NEEDED:
    - Some servers slow down under load
    - Some block too many requests
    - Some respond fast and allow speed-up
    """

    global delay

    # 🚫 If blocked → slow down heavily
    if status in (403, 429):
        delay = min(max_delay, delay + 0.5)
        print(f"🚫 Block detected → delay increased to {round(delay,2)}s")

    # 🐢 If server is slow → increase delay slightly
    elif response_time and response_time > 1.5:
        delay = min(max_delay, delay + 0.2)
        print(f"🐢 Slow response → delay = {round(delay,2)}s")

    # 🚀 If server is fast → reduce delay
    elif response_time and response_time < 0.5:
        delay = max(min_delay, delay - 0.05)
        print(f"🚀 Fast response → delay = {round(delay,2)}s")


# =========================================================
# 🌐 FETCH PAGE (CORE NETWORK FUNCTION)
# =========================================================

async def fetch_soup(session, url):
    """
    This function:
    1. Sends HTTP request
    2. Measures response time
    3. Applies concurrency control
    4. Applies adaptive delay
    5. Returns parsed HTML (BeautifulSoup)
    """

    global success_count, fail_count

    # limit number of simultaneous requests
    async with semaphore:

        # start timer
        start_time = time.perf_counter()

        try:
            async with session.get(url) as response:

                # measure how long request took
                end_time = time.perf_counter()
                response_time = end_time - start_time

                # =========================
                # CASE 1: SUCCESS
                # =========================
                if response.status == 200:
                    raw = await response.read()
                    html = raw.decode("utf-8-sig", errors="ignore")
                    success_count += 1

                    adjust_concurrency()
                    adjust_delay(response_time=response_time)

                    # small pause to behave more naturally
                    await asyncio.sleep(delay)

                    return bs4(html, "lxml")

                # =========================
                # CASE 2: BLOCKED
                # =========================
                elif response.status in (403, 429):
                    print(f"🚫 Blocked: {url} | {response.status}")
                    fail_count += 1

                    adjust_concurrency()
                    adjust_delay(status=response.status)

                    return None

                # =========================
                # CASE 3: OTHER ERRORS
                # =========================
                else:
                    print(f"⚠️ Failed: {url} | {response.status}")
                    fail_count += 1

                    adjust_concurrency()
                    adjust_delay(response_time=response_time)

                    return None

        except Exception as e:
            # network failure / timeout / DNS error etc.
            print(f"⚠️ Error: {url} | {e}")
            fail_count += 1

            adjust_concurrency()
            adjust_delay()

            return None


# =========================================================
# 📄 PARSE CATALOGUE PAGE (LIST PAGE)
# =========================================================

def parse_catalogue_page(soup, base_url):
    """
    This function extracts:
    - basic book info (title, price, rating)
    - product URLs (for detailed pages)
    """

    books = soup.find_all("article", class_="product_pod")

    product_urls = []

    for book in books:

        # extract product page URL
        product_url = urljoin(base_url, book.find("a")["href"])
        product_urls.append(product_url)

    return product_urls


# =========================================================
# 📘 PARSE PRODUCT PAGE (DETAILED DATA)
# =========================================================

all_books = []  # 📦 FINAL STORAGE (important for CSV export)

async def parse_product_page(session, product_url):
    """
    Extract full book details from individual product page
    """

    soup = await fetch_soup(session, product_url)

    if not soup:
        return

    try:
        # -------------------------
        # BASIC BOOK INFORMATION
        # -------------------------
        title = soup.find("h1").text.strip()

        breadcrumb = soup.find("ul", class_="breadcrumb").find_all("li")
        category = breadcrumb[2].text.strip() if len(breadcrumb) > 2 else "Unknown"

        price = soup.find("p", class_="price_color").text.strip()

        stock_text = soup.find("p", class_="instock availability").text.strip()
        stock = stock_text.split("(")[1].split("available")[0].strip() if "(" in stock_text else "0"

        rating = soup.find("p", class_="star-rating")["class"][1]

        upc = soup.find("th", string="UPC").find_next_sibling("td").text.strip()

        desc_tag = soup.find("meta", {"name": "description"})
        description = desc_tag["content"].strip() if desc_tag else "No description"

        # -------------------------
        # STORE CLEAN STRUCTURED DATA
        # -------------------------
        all_books.append({
            "Title": title,
            "Category": category,
            "Price": price,
            "Rating": rating,
            "Stock": stock,
            "UPC": upc,
            "Description": description,
            "URL": product_url
        })

    except Exception as e:
        print(f"⚠️ Parsing error: {product_url} | {e}")


# =========================================================
# 💾 SAVE DATA TO CSV (FINAL STEP)
# =========================================================

def save_to_csv(filename="books.csv"):
    """
    Converts collected data into a CSV file

    WHY THIS IS IMPORTANT:
    - CSV = universal format
    - can open in Excel, Google Sheets, Python, ML tools
    """

    if not all_books:
        print("⚠️ No data to save")
        return
    
    # get CSV headers from keys of first record
    keys = all_books[0].keys()

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_books)

    print(f"\n📁 Saved {len(all_books)} records → {filename}")


# =========================================================
# 🚀 MAIN SCRAPER WORKFLOW
# =========================================================

async def scrape_all_pages():
    """
    FULL PROCESS:

    1. Open website
    2. Go page by page
    3. Extract product URLs
    4. Scrape product pages concurrently
    5. Store data in memory
    6. Export to CSV at end
    """

    page_number = 1
    current_url = BASE_URL

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        while current_url:

            print(f"\n🚀 Scraping Page {page_number}: {current_url}\n")

            # get catalogue page
            soup = await fetch_soup(session, current_url)

            if not soup:
                break

            # extract product links
            product_urls = parse_catalogue_page(soup, current_url)

            # scrape product pages concurrently
            tasks = [
                parse_product_page(session, url)
                for url in product_urls
            ]

            await asyncio.gather(*tasks)

            # move to next page
            next_btn = soup.find("li", class_="next")

            if next_btn:
                current_url = urljoin(current_url, next_btn.find("a")["href"])
                page_number += 1
            else:
                current_url = None

    # export after scraping completes
    save_to_csv()


# =========================================================
# ▶️ START PROGRAM
# =========================================================

if __name__ == "__main__":
    asyncio.run(scrape_all_pages())