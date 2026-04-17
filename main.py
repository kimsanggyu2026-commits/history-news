import feedparser
import requests
import os

# GitHub Secrets에서 가져올 값들
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RSS_URL = "https://history.go.kr/rss/rssfeed.do?id=000000000424"
DB_FILE = "last_link.txt"

def send_telegram(message):
    print(">>> 텔레그램으로 메시지 발송 시도 중...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=params, timeout=10)
        # 텔레그램의 답변을 로그에 찍어서 확인합니다.
        print(f">>> 텔레그램 응답 코드: {response.status_code}")
        if response.status_code != 200:
            print(f">>> 알림 발송 실패! 이유: {response.text}")
        else:
            print(">>> 알림 발송 성공!")
    except Exception as e:
        print(f">>> 에러 발생: {e}")

def main():
    print(f">>> RSS 피드 읽는 중: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print(">>> 게시글을 찾을 수 없습니다.")
        return

    latest_link = feed.entries[0].link
    latest_title = feed.entries[0].title
    print(f">>> 최신 글 발견: {latest_title}")

    # 중복 체크
    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()
    
    print(f">>> 이전 기록: {last_link}")
    print(f">>> 현재 링크: {latest_link}")

    if latest_link != last_link:
        print(">>> 새로운 글이 확인되었습니다. 알림을 보냅니다.")
        msg = f"<b>🏛️ 국편위 학회 새 소식</b>\n\n{latest_title}\n\n<a href='{latest_link}'>링크 바로가기</a>"
        send_telegram(msg)
        
        with open(DB_FILE, "w") as f:
            f.write(latest_link)
    else:
        print(">>> 최신 글이 이미 확인된 링크입니다. 알림을 보내지 않습니다.")

if __name__ == "__main__":
    main()
