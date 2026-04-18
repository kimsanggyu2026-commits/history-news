import feedparser
import requests
import os

# 환경 변수 설정
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 🌟 명칭과 저장 파일명을 정확히 매칭했습니다.
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
    print(f">>> [{board_name}] 알림 발송 시도...")
    msg = f"<b>{board_name} 새 소식</b>\n\n{title}\n\n<a href='{link}'>링크 바로가기</a>"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    
    try:
        res = requests.post(url, data=params, timeout=10)
        if res.status_code == 200:
            print(f">>> [{board_name}] 전송 성공")
    except Exception as e:
        print(f">>> 전송 에러: {e}")

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for name, info in BOARDS.items():
        print(f"\n--- {name} 확인 중 ---")
        try:
            response = requests.get(info["url"], headers=headers, timeout=15)
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                continue

            latest_link = feed.entries[0].link
            latest_title = feed.entries[0].title
            
            # 이전 기록 확인
            last_link = ""
            if os.path.exists(info["file"]):
                with open(info["file"], "r") as f:
                    last_link = f.read().strip()
            
            # 비교 후 알림
            if latest_link != last_link:
                print(f"    [발견] 새 글: {latest_title}")
                send_telegram(name, latest_title, latest_link)
                # 🌟 파일에 기록 (로봇의 기억)
                with open(info["file"], "w") as f:
                    f.write(latest_link)
            else:
                print(f"    이미 확인한 소식입니다.")

        except Exception as e:
            print(f"    에러 발생: {e}")

if __name__ == "__main__":
    main()
