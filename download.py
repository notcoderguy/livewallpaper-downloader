import os
import subprocess
import threading
import argparse
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from time import sleep

# Define a lock to synchronize access to the 'download_links' list
download_links_lock = threading.Lock()

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

def download_with_aria2(link, download_dir):
    try:
        # Extract the slug from the link and construct the desired filename
        parsed_url = urlparse(link)
        slug = parsed_url.path.split('/')[-2]
        desired_filename = os.path.join(download_dir, f"{slug}.mp4")

        # Change the current working directory to the download directory
        os.chdir(download_dir)

        subprocess.run(
            ['aria2c', link, '-o', f"{slug}.mp4", '--file-allocation=none', '--check-certificate=false', '--continue=true', '--retry-wait=3', '--max-tries=3'],
            check=True
        )

        print(f'[+] Downloaded: {desired_filename}')
    except subprocess.CalledProcessError as e:
        print(f"[-] Error while downloading {link}: {e}")



def main():
    parser = argparse.ArgumentParser(description="Download videos from a list of links.")
    parser.add_argument("links_file", help="Path to the file containing video links (one link per line)")
    parser.add_argument("download_dir", help="Directory where downloaded videos will be saved")

    args = parser.parse_args()

    links_file = args.links_file
    download_dir = args.download_dir

    # Load links from the specified file
    with open(links_file, 'r') as f:
        links = [line.strip() for line in f.readlines()]

    if not links:
        print("No links found in the specified file. Please provide links to download.")
        return

    print('[+] Downloading videos with Aria2c')

    # Create the download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Change the current directory to the download directory
    os.chdir(download_dir)

    # Download the videos with multithreading
    download_threads = 4  # Adjust the number of download threads as needed
    threads = []

    for link in links:
        # Extract the final download link from the current link
        final_link = extract_final_link(link)
        if final_link:
            thread = threading.Thread(target=download_with_aria2, args=(final_link, download_dir))
            thread.start()
            threads.append(thread)

            # Limit the number of active threads to avoid overwhelming the system
            while len(threading.enumerate()) > download_threads:
                pass

    # Wait for all download threads to finish
    for thread in threads:
        thread.join()

    print('[+] Done')

def extract_final_link(link):
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        final_link = soup.find('a', class_='g1-button')
        if final_link:
            return final_link.get('href')
        return None
    except Exception as e:
        print(f"[-] Error while extracting final link from {link}: {e}")
        return None

if __name__ == '__main__':
    main()
