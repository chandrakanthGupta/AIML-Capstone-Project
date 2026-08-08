import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/"


def get_soup(url):
    """
    Fetches the HTML of a URL with rate limiting and returns a BeautifulSoup object.
    """
    time.sleep(0.5)  # Polite pause between requests to prevent server throttling
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[ERROR] Fetching {url}: {e}")
        return None


def get_categories():
    """
    Extracts all category names and their absolute URLs from the sidebar.
    """
    soup = get_soup(BASE_URL)
    if not soup:
        return {}
    
    categories = {}
    category_links = soup.select(".side_categories ul li ul li a")
    for tag in category_links:
        name = tag.text.strip()
        url = urljoin(BASE_URL, tag["href"])
        categories[name] = url
        
    return categories


def parse_book_item(pod, category_name):
    """
    Extracts raw fields from a single <article class="product_pod"> tag.
    """
    title_tag = pod.select_one("h3 a")
    title = (
        title_tag["title"].strip()
        if (title_tag and title_tag.has_attr("title"))
        else (title_tag.text.strip() if title_tag else None)
    )
    
    price_tag = pod.select_one(".price_color")
    price = price_tag.text.strip() if price_tag else None
    
    rating_tag = pod.select_one("p.star-rating")
    rating = None
    if rating_tag and rating_tag.has_attr("class"):
        rating_classes = [c for c in rating_tag["class"] if c != "star-rating"]
        if rating_classes:
            rating = rating_classes[0]
            
    avail_tag = pod.select_one(".availability")
    availability = avail_tag.text.strip() if avail_tag else None
    
    return {
        "title": title,
        "price": price,
        "star_rating": rating,
        "availability": availability,
        "category": category_name
    }


def scrape_category(category_name, category_url):
    """
    Scrapes all books for a specific category across all its paginated pages.
    """
    books = []
    current_url = category_url
    
    while current_url:
        print(f"  [Scraping Page] {current_url}")
        soup = get_soup(current_url)
        if not soup:
            break
            
        pods = soup.select("article.product_pod")
        for pod in pods:
            book_data = parse_book_item(pod, category_name)
            books.append(book_data)
            
        next_button = soup.select_one("ul.pager li.next a")
        if next_button and next_button.has_attr("href"):
            current_url = urljoin(current_url, next_button["href"])
        else:
            current_url = None
            
    return books


def scrape_all_target_categories(target_categories):
    """
    Coordinates scraping across multiple specified categories.
    """
    all_categories = get_categories()
    all_books = []
    
    for cat_name in target_categories:
        if cat_name not in all_categories:
            print(f"[WARNING] Category '{cat_name}' not found on website.")
            continue
            
        print(f"\n[-] Fetching Category: '{cat_name}'")
        cat_url = all_categories[cat_name]
        books = scrape_category(cat_name, cat_url)
        print(f"   -> Found {len(books)} books in '{cat_name}'")
        all_books.extend(books)
        
    return all_books
