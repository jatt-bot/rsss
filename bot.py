import requests
import time
from bs4 import BeautifulSoup
from telegram import Bot

# === Config ===
BOT_TOKEN = "7975556997:AAEpcnKzScmOnNqX4j1aJVtQ-iDHuF2BcX8"  # Replace with your bot token
CHANNEL_ID = -1002550488757  # Replace with your Telegram channel ID
POSTED_FILE = "posted.txt"  # File to store posted URLs

bot = Bot(token=BOT_TOKEN)

# === Scrape DDL links from movie post ===
def scrape_hdhub4u(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find("h1", class_="entry-title")
    title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".mkv") or "r2.dev" in href:
            links.append(href)

    if not links:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "hub" in href or "file" in href:
                links.append(href)

    return title, links

# === Scrape latest posts from home page ===
def get_latest_posts():
    url = "https://hdhub4u.family/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    posts = []
    for article in soup.find_all("article"):
        link_tag = article.find("a", href=True)
        if link_tag:
            title = link_tag.get_text(strip=True)
            url = link_tag['href']
            posts.append((title, url))

    return posts[:5]  # Limit to latest 5 posts

# === Load posted URLs from file ===
def load_posted_urls():
    try:
        with open(POSTED_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

# === Save new URL to file ===
def save_posted_url(url):
    with open(POSTED_FILE, "a") as f:
        f.write(url + "\n")

# === Main Bot Logic ===
def main():
    posted_urls = load_posted_urls()
    latest_posts = get_latest_posts()

    for title, url in latest_posts:
        if url in posted_urls:
            continue

        print(f"New post: {title}")
        title_scraped, links = scrape_hdhub4u(url)

        if links:
            message = f"🎬 <b>{title_scraped}</b>\n\n"
            message += "📦 <b>DDL Links:</b>\n"
            for link in links:
                message += f"<code>{link}</code>\n"

            try:
                bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='HTML')
                print("Posted to Telegram.")
                save_posted_url(url)
            except Exception as e:
                print(f"Failed to post: {e}")
        else:
            print("No DDL links found.")

# === Looping every 30 minutes ===
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Error:", e)
        time.sleep(1800)  # Wait 30 minutes
