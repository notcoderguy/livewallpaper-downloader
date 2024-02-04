# 🎥 LiveWallpaper Downloader 🚀

## 📜 Description

Dive into a world where your favorite live wallpapers come to life right on your desktop! This project, featuring Python script 🐍 - `main.py`, empowers you to scrape video links 🌐 from a website and download those mesmerizing videos using the swift Aria2c download manager.

## ✅ Prerequisites

Before we get started, make sure you have:

- Python 3.x 🐍 installed on your machine.
- Aria2c 📥 for the smooth downloading of videos.

## 🛠 Installation

Follow these steps to set up the LiveWallpaper Downloader:

1. **Clone the repository:**

```bash
git clone https://github.com/notcoderguy/livewallpaper-downloader.git
cd livewallpaper-downloader
```

2. **Install the required Python packages:**

```bash
pip install -r requirements.txt
```

3. **Aria2c Installation:**

   - For Linux (Ubuntu/Debian) users:

        ```bash
        sudo apt-get install aria2
        ```

   - For macOS users (via Homebrew):

        ```bash
        brew install aria2
        ```

   - For windows users (via Scoop):

        ```bash
        scoop install aria2
        ```


## 🚀 Usage

### Step 1: Scraping Video Links

Execute the `main.py` script to start scraping video links from your chosen website. Customize the BASE_URL and MAX_PAGE within the script for a personalized scrape.

```bash
python main.py update
```

This generates a `links.txt` file teeming with the scraped video links.

### Step 2: Downloading Videos

With the `links.txt` filled with video URLs, trigger the `main.py` script to commence the download. Simply specify your desired download directory.

```bash
python main.py download <your_download_directory>
```

Leverage the power of Aria2c and multithreading to download the videos concurrently, bringing efficiency to your command.

## ⚙️ Configuration

Tailor the download experience by adjusting the `download_threads` variable within the `main.py` script, ensuring the download process aligns with your system's capabilities.

## 📜 License

Unleash the potential of LiveWallpaper Downloader, which stands proudly under the MIT License. Dive into the [LICENSE](LICENSE) file for all the legal details.

## 🙌 Acknowledgments

A huge shoutout to:

- [cloudscraper](https://github.com/codemanki/cloudscraper) for skillfully bypassing anti-bot protections.
- [Aria2](https://aria2.github.io/) for its unmatched efficiency in downloading files.

Embark on a journey with LiveWallpaper Downloader and transform your desktop into a dynamic canvas of your favorite visuals! 🌌✨