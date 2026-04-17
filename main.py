import feedparser
import requests
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RSS_URL = "https://history.go.kr/rss/rssfeed.do?id=000000000424"
DB_FILE = "last_link.txt"

def send_telegram(message):
    print(">>> 텔레그램 전송 시도...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=params, timeout=10)
        print(f">>> 텔레그램 서버 응답: {res.status_code}")
    except Exception as e:
        print(f">>> 텔레그램 전송 에러: {e}")

def main():
    print(">>> 국편위 소식 가져오는 중...")
    # 🌟 핵심: 브라우저인 척 속여야 서버가 대답해줍니다.
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(RSS_URL, headers=headers, timeout=15)
        feed = feedparser.parse(resp.text)
        print(f">>> 찾은 게시글 수: {len(feed.entries)}개")
    except Exception as e:
        print(f">>> RSS 가져오기 실패: {e}")
        return

    if not feed.entries:
        print(">>> 게시글이 없습니다. 서버가 막았을 가능성이 커요.")
        return

    latest_link = feed.entries[0].link
    latest_title = feed.entries[0].title
    print(f">>> 최신 글 발견: {latest_title}")

    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()
    
    print(f">>> 마지막 기록된 링크: '{last_link}'")

    if latest_link != last_link:
        print(">>> [새 글!] 알림을 보냅니다.")
        msg = f"<b>🏛️ 국편위 학회 새 소식</b>\n\n{latest_title}\n\n<a href='{latest_link}'>링크 바로가기</a>"
        send_telegram(msg)
        with open(DB_FILE, "w") as f:
            f.write(latest_link)
    else:
        print(">>> 이미 확인한 소식입니다.")

if __name__ == "__main__":
    main()
