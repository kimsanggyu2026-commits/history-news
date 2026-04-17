import feedparser
import requests
import os

# 설정값
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RSS_URL = "https://history.go.kr/rss/rssfeed.do?id=000000000424"
DB_FILE = "last_link.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=params, timeout=10)
    except:
        pass

def main():
    # 브라우저처럼 보이게 헤더 추가 (속도 개선 핵심)
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        feed = feedparser.parse(response.text)
    except:
        return

    if not feed.entries: return

    latest_link = feed.entries[0].link
    latest_title = feed.entries[0].title

    # 중복 체크
    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()

    if latest_link != last_link:
        msg = f"<b>🏛️ 국편위 학회 새 소식</b>\n\n{latest_title}\n\n<a href='{latest_link}'>링크 바로가기</a>"
        send_telegram(msg)
        with open(DB_FILE, "w") as f:
            f.write(latest_link)

if __name__ == "__main__":
    main()
