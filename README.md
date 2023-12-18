# LiveWallpaper Downloader

## Description

This project consists of two Python scripts, `links.py` and `downloads.py`, which work together to scrape video links from a website and download the corresponding videos using the Aria2c download manager.

## Prerequisites

- Python 3.x
- Aria2c (for downloading videos)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/your-project.git
cd your-project
```

2. Install the required Python packages:

```bash
pip install cloudscraper beautifulsoup4
```

3. Install Aria2c (if not already installed):

   - For Linux (Ubuntu/Debian):

        ```bash
        sudo apt-get install aria2
        ```

   - For macOS (using Homebrew):

        ```bash
        brew install aria2
        ```

## Usage

### Step 1: Scraping Video Links

Run the `links.py` script to scrape video links from a specific website. You can customize the website URL and the number of pages to scrape within the script.

```bash
python links.py
```

The script will create a `links.txt` file containing the scraped video links.

### Step 2: Downloading Videos

Run the `downloads.py` script to download videos from the links saved in the `links.txt` file. Provide the path to the `links.txt` file and the download directory as command-line arguments.

```bash
python downloads.py links.txt /path/to/download/directory
```

The script will download the videos concurrently using Aria2c with multithreading.

## Configuration

You can adjust the number of download threads in the `downloads.py` script by modifying the `download_threads` variable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [cloudscraper](https://github.com/codemanki/cloudscraper) for bypassing anti-bot protection on websites.
- [Aria2](https://aria2.github.io/) for efficient downloading of files.
