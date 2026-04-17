import feedparser
import requests
import os

# 환경 변수 로드
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 🌟 명칭을 요청하신 대로 변경하고 RSS ID를 정확히 매칭했습니다.
BOARDS = {
    "📢 공지사항": {
        "url": "https://www.history.go.kr/rss/rssfeed.do?id=000000000421",
        "file": "last_link_notice.txt"
    },
    "🏛️ 한국사 관련 학회 소식": {
        "url": "https://www.history.go.kr/rss/rssfeed.do?id=000000000424",
        "file": "last_link_academic.txt"
    }
}

def send_telegram(board_name, title, link):
    """텔레그램 메시지 전송 함수"""
    print(f">>> [{board_name}] 알림 발송 시도...")
    # 알림 메시지 상단에 명칭이 굵게 표시됩니다.
    msg = f"<b>{board_name} 새 소식</b>\n\n{title}\n\n<a href='{link}'>링크 바로가기</a>"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    
    try:
        res = requests.post(url, data=params, timeout=10)
        if res.status_code == 200:
            print(f">>> [{board_name}] 전송 성공")
    except:
        pass

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for name, info in BOARDS.items():
        print(f"\n--- {name} 확인 ---")
        try:
            response = requests.get(info["url"], headers=headers, timeout=15)
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                continue

            latest_link = feed.entries[0].link
            latest_title = feed.entries[0].title
            
            last_link = ""
            if os.path.exists(info["file"]):
                with open(info["file"], "r") as f:
                    last_link = f.read().strip()
            
            if latest_link != last_link:
                print(f"    새 글: {latest_title}")
                send_telegram(name, latest_title, latest_link)
                with open(info["file"], "w") as f:
                    f.write(latest_link)
            else:
                print(f"    변동 없음")

        except Exception as e:
            print(f"    에러: {e}")

if __name__ == "__main__":
    main()
