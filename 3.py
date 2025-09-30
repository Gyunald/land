import requests
from bs4 import BeautifulSoup
import time
import os

date = "20250930"
url = f"https://finance.naver.com/news/news_list.naver?mode=RANK&date={date}"
main_link = "https://finance.naver.com"
filename = "f_news.txt"

def load_existing_links():
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip().split('\t')[1] for line in f if '\t' in line)

def save_news(news):
    with open(filename, "a", encoding="utf-8") as f:
        for item in news:
            f.write(f"{item['news_title']}\t{item['news_link']}\n")

while True:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("#contentarea_left > div.hotNewsList > ul > li > ul > li > a")
    data = [
        {
            "news_title": item.get_text(strip=True),
            "news_link": main_link + item["href"]
        }
        for item in items
    ]
    existing_links = load_existing_links()
    new_news = [item for item in data if item['news_link'] not in existing_links]
    if new_news:
        save_news(new_news)
        print(f"{len(new_news)} new news saved.")
    else:
        print("No new news.")
    time.sleep(300)  # 5분 대기
