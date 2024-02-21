import os
import subprocess
import threading
import argparse
import cloudscraper

from colorama import init, Fore, Style 
from rich.progress import track, Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

from urllib.parse import urlparse
from time import sleep
from bs4 import BeautifulSoup

init()
console = Console()

# Define a lock to synchronize access to the 'links' list
links_lock = threading.Lock()

def get_pages(BASE_URL, MAX_PAGE):
    links = []
    scraper = cloudscraper.create_scraper()
    threads = []

    with Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(
            complete_style="green",
            pulse_style="dim",
        ),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("Fetching Pages: ", total=MAX_PAGE)
        
        def worker(page):
            nonlocal links
            # print('[+] Getting page ' + str(page))
            page_url = f"{BASE_URL}{page}/"
            try:
                page_links = get_posts(scraper, page_url)
                with links_lock:
                    links.extend(page_links)
            except Exception as e:
                print(Fore.RED + f"[-] Error while processing page {page}: {e}" + Fore.RESET)
                
        threads = []
        for page in range(1, MAX_PAGE + 1):
            thread = threading.Thread(target=worker, args=(page,))
            threads.append(thread)
            thread.start()
            progress.update(task, advance=1)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return links

def get_posts(SCRAPER, URL):
    # Get the links to the posts
    try:
        response = SCRAPER.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes (e.g., 404)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', class_='g1-frame'):
            href = link.get('href')
            if href:
                links.append(href)
        return links
    except Exception as e:
        print(f"[-] Error while processing page {URL}: {e}")
        return []

def get_download_link(URL):
    # Get the download link for the wallpaper
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes (e.g., 404)
        soup = BeautifulSoup(response.text, 'html.parser')
        download_link = soup.find('a', class_='g1-button')
        if download_link:
            return download_link.get('href')
        else:
            return None
    except Exception as e:
        print(f"[-] Error while processing page {URL}: {e}")
        return None

def download(LINK, DOWNLOAD_DIR):
    try:
        # Get the download link for the wallpaper
        download_link = get_download_link(LINK)
        
        # Extract the slug from the link and construct the desired filename
        parsed_url = urlparse(LINK)
        slug = parsed_url.path.split('/')[-2]
        desired_filename = os.path.join(DOWNLOAD_DIR, f"{slug}.mp4")
        
        # Check if the file already exists
        if os.path.exists(desired_filename):
            # print(Fore.YELLOW + f"[!] File {desired_filename} already exists, skipping" + Fore.RESET)
            return
        
        # Change to the download directory
        os.chdir(DOWNLOAD_DIR)
        
        # Download the file using aria2c
        subprocess.run(['aria2c', download_link, '-o', f"{slug}.mp4", '--auto-file-renaming=false', '--file-allocation=none', '--check-certificate=false', '--continue=true', '--retry-wait=3', '--max-tries=3', '--quiet'], check=True)
        
        # print(f'[+] Downloaded: {desired_filename}')
        
    except Exception as e:
        print(Fore.RED + f"[-] Error while downloading {LINK}: {e}" + Fore.RESET)

def update_links(SCRAPER, LINKS, BASE_URL, MAX_PAGE):
    # Read the current links
    try:
        with open(LINKS, 'r') as f:
            links = f.read().splitlines()
    except FileNotFoundError:
        links = []
        
    # Get the new links
    new_links = get_pages(BASE_URL, MAX_PAGE)
    
    # Add the unique new links to the current links
    links.extend(link for link in new_links if link not in links)
    
    # Write the updated links to the file
    with open(LINKS, 'w') as f:
        for link in links:
            f.write(link + '\n')
            
    print(Fore.GREEN + f'[+] Updated links file: {LINKS}' + Fore.RESET)
    
def download_manager(LINKS, DOWNLOAD_DIR):
    # Load the links from the file
    with open(LINKS, 'r') as f:
        links = [line.strip() for line in f.readlines()]
        
    if not links:
        print(Fore.RED + "No links found in the specified file. Please run the 'update' action first." + Fore.RESET)
        return
    
    # Create the download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    total_tasks = len(links)  # Total number of download tasks    
    
    with Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(
            complete_style="green",
            pulse_style="dim",
        ),
        TextColumn("[progress.completed][{task.completed}/{task.total}]"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        transient=True,
        console=console
    ) as progress:
            
        download_tasks = progress.add_task(f"Downloading: ", total=total_tasks)
        
        # Download the wallpapers with multithreading
        download_threads = 4  # Adjust the number of download threads as needed
        threads = []
    
        for link in links:
            thread = threading.Thread(target=download, args=(link, DOWNLOAD_DIR))
            threads.append(thread)
            thread.start()
            
            # Limit the number of concurrent download threads
            while threading.active_count() > download_threads:
                sleep(1)
                
            progress.update(download_tasks, advance=1)
        
    # Wait for all download threads to finish
    for thread in threads:
        thread.join()
        
    # print('[+] Done')
    

def main():
    parser = argparse.ArgumentParser(description='Download wallpapers from livewallp.com')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Create a subparser for the 'update' action
    update_parser = subparsers.add_parser('update', help='Update links file')
    # No additional arguments for update

    # Create a subparser for the 'download' action
    download_parser = subparsers.add_parser('download', help='Download wallpapers')
    download_parser.add_argument('download_dir', help='Directory where downloaded wallpapers will be saved', nargs='?', default='wallpapers')

    args = parser.parse_args()

    action = args.action

    SCRAPER = cloudscraper.create_scraper()
    LINKS = 'links.txt'
    BASE_URL = 'https://livewallp.com/page/'
    MAX_PAGE = 91

    if action == 'update':
        print(Fore.GREEN + '[+] Updating links file' + Fore.RESET)
        update_links(SCRAPER, LINKS, BASE_URL, MAX_PAGE)
        print(Fore.GREEN + '[+] Done Updating links file' + Fore.RESET)
    elif action == 'download':
        download_dir = args.download_dir
        print(Fore.GREEN + f'[+] Downloading wallpapers to {download_dir}' + Fore.RESET)
        download_manager(LINKS, download_dir)
        print(Fore.GREEN + '[+] Done downloading wallpapers' + Fore.RESET)

if __name__ == '__main__':
    main()