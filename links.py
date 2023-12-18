import cloudscraper
from bs4 import BeautifulSoup
import threading

# Define a lock to synchronize access to the 'links' list
links_lock = threading.Lock()

def get_all_links(base_url, max_page):
    links = []
    scraper = cloudscraper.create_scraper()
    threads = []

    def worker(page):
        nonlocal links
        print('[+] Getting page ' + str(page))
        page_url = f"{base_url}{page}/"
        try:
            page_links = get_page_links(scraper, page_url)
            with links_lock:
                links.extend(page_links)
        except Exception as e:
            print(f"[-] Error while fetching links for page {page}: {e}")

    for page in range(1, max_page + 1):
        thread = threading.Thread(target=worker, args=(page,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return links

def get_page_links(scraper, url):
    try:
        response = scraper.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (e.g., 404)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', class_='g1-frame'):
            href = link.get('href')
            if href:
                links.append(href)
        return links
    except Exception as e:
        print(f"[-] Error while processing page {url}: {e}")
        return []

def main():
    base_url = 'https://livewallp.com/page/'
    max_page = 85
    links = get_all_links(base_url, max_page)
    print('[+] Writing links to file')
    with open('links.txt', 'w') as f:
        for link in links:
            f.write(link + '\n')
    print('[+] Done')

if __name__ == '__main__':
    main()
