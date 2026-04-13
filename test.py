import requests
from bs4 import BeautifulSoup as bs4

baseURL = "https://books.toscrape.com/index.html"


# Extract the details of each book and print them
def extract_all_book_details(books):
    # Loop through each book container and extract the title and price
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
            next_page_url = baseURL.replace("index.html", "") + soup.find("li", class_="next").find("a")['href'] if soup.find("li", class_="next") else None
            
            print(f"Title: {title}")
            print(f"Rating: {rating}")
            print(f"Price: {price}")
            print(f"Stock: {stock}")
            print(f"Product Page URL: {product_page_url}")
            print(f"Image URL: {img_url}")
            print("-" * 40)
    return product_page_url, next_page_url

# Extract the Individual book details from the product page
def extract_individual_book_details(product_page_url):    
        product_response = session.get(product_page_url)
        product_soup = bs4(product_response.content, 'lxml')
        
        title = product_soup.find("div", class_="product_main").find("h1").text.strip()
        genre = product_soup.find("ul", class_="breadcrumb").find_all("li")[2].text.strip()
        stock = product_soup.find("p", class_="instock availability").text.strip()
        # take the content within the () in the stock string
        stock = stock[stock.find("(")+1:stock.find(")")]
        price = product_soup.find("p", class_="price_color").text.strip()
        upc = product_soup.find("th", text="UPC").find_next_sibling("td").text.strip()
        description = product_soup.find("div", id="product_description").find_next_sibling("p").text.strip()
        
        print(f"Title: {title}")
        print(f"Genre: {genre}")
        print(f"Stock: {stock}")
        print(f"Price: {price}")
        print(f"UPC: {upc}")
        print(f"Description: {description}") if description else print("No description available.")
        print("=" * 40)
        
# Main function to orchestrate the scraping process
def read_all_pages(books):
    # Extract the details of the books on the first page and get the product page URL and next page URL
    product_page_url, next_page_url = extract_all_book_details(books)
    
    extract_individual_book_details(product_page_url)
    
    # Loop through the next pages until there are no more
    while next_page_url:
        response = session.get(next_page_url)
        soup = bs4(response.content, 'lxml')
        books = soup.find_all('article', class_='product_pod')
        product_page_url, next_page_url = extract_all_book_details(books)



# Function to fetch the HTML content of the page and process it
def fetch_process_html():
    # Initializng a session to persist certain parameters across requests
    session = requests.session()

    #Headers to mimic a real browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    #add headers to the session
    session.headers.update(headers)

    # Get the HTML content of the page
    response = session.get(baseURL)
    soup = bs4(response.content, 'lxml')

    # Find all the book containers on the page
    books = soup.find_all('article', class_='product_pod')
    return books, session, soup



# Start the scraping process 
books, session, soup = fetch_process_html()
read_all_pages(books)


