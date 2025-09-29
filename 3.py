import requests
import time
from datetime import datetime
import os

# === 설정값 ===
BASE_DATE = datetime.today().strftime("%Y-%m-%d")
MAX_PAGES = 1
DELAY = 0.5
INTERVAL = 300

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}

NEWS_FILE = "sdcard/news/news.txt"

def fetch_news(base_date=BASE_DATE, max_pages=MAX_PAGES, delay=DELAY):
    """네이버 부동산 뉴스 크롤링 함수"""
    all_articles = []

    for page in range(1, max_pages + 1):
        url = f"https://land.naver.com/news/airsList.naver?baseDate={base_date}&page={page}&size=5"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"⚠️ {page} 페이지 요청 실패: {e}")
            break

        if not data or not data.get("list"):
            break

        articles = [
            {
                "date": a.get("publishDateTime", "")[:10],
                "title": a.get("title", ""),
                "link": a.get("linkUrl", ""),
                "summary": (a.get("summaryContent", "").split(".")[0] + ".") if a.get("summaryContent") else "",
            }
            for a in data.get("list", [])
        ]
        all_articles.extend(articles)
        time.sleep(delay)

    return all_articles

def load_seen_links():
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen_links(seen_links):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        f.writelines(link + "\n" for link in seen_links)

def main_loop():
    seen_links = load_seen_links()

    while True:
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 크롤링 시작")
        news = fetch_news()
        new_articles = [n for n in news if n["link"] and n["link"] not in seen_links]

        if new_articles:
            print(f"🆕 새 뉴스 {len(new_articles)}건 발견!")
            for n in new_articles:
                print(f"- {n['date']} | {n['title']} ({n['link']})")
                seen_links.add(n["link"])
            save_seen_links(seen_links)
        else:
            print("새로운 뉴스 없음.")

        print(f"💤 {INTERVAL/60}분 대기...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main_loop()
