import random
from time import sleep

import requests
from bs4 import BeautifulSoup as bs4
baseURL = "https://books.toscrape.com/index.html"
# https://books.toscrape.com/catalogue/page-2.html
session = requests.Session()

# Create a function to extract html and soup reusable for both the catalogue and product pages
def get_soup(url):
    try:
        response = session.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = bs4(response.content, 'lxml')
        return soup
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


#function to extract the catalogue page details
def extract_catalogue_page_details(soup, page_number=1):
    if soup is not None:
        books = soup.find_all("article", class_="product_pod")
        for book in books:
            product_page_href = book.find("a", href=True)['href']
            img_src = book.find("img", src=True)['src']
            
            # Extract the title, rating, price, stock availability, product page URL, and image URL
            title = book.find("h3").find("a")['title']
            rating = book.find("p", class_="star-rating")['class'][1]
            price = book.find("p", class_="price_color").text.strip()
            stock = book.find("p", class_="instock availability").text.strip()
            product_page_url = baseURL.replace("index.html", "") + product_page_href
            img_url = baseURL.replace("index.html", "") + img_src
            
            print(f"Title: {title}")
            print(f"Rating: {rating}")
            print(f"Price: {price}")
            print(f"Stock: {stock}")
            print(f"Product Page URL: {product_page_url}")
            print(f"Image URL: {img_url}")
            print("-" * 40)
            sleep(random.uniform(0.5, 2))
    print("Successfully retrieved page 1") if page_number < 2 else print(f"Successfully retrieved page {page_number}")
    print("-" * 40)
#function to move to the next page and extract the details of the books on that page
def next_page(baseURL):
    for page_number in range(2, 51):
        url_part = f"catalogue/page-{page_number}.html"
        next_page_url = baseURL.replace("index.html", "") + url_part
        soup = get_soup(next_page_url)
        if soup is not None:
            extract_catalogue_page_details(soup, page_number)
        else:
            print(f"Failed to retrieve page {page_number}. Stopping.")
            break
# def extract_next_page_details(soup):

#function to extract the details of each book

 #function to run the main program to orchestrate the scraping process
def main():
    soup = get_soup(baseURL)
    extract_catalogue_page_details(soup)    
    next_page(baseURL)
if __name__ == "__main__":
    main()