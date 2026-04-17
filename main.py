import feedparser
import requests
import os

# 환경 변수 로드
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 🌟 관리할 게시판 목록 (이름, RSS 주소, 기록 저장용 파일명)
BOARDS = {
    "🏛️ 국편위 공지사항": {
        "url": "https://www.history.go.kr/rss/rssfeed.do?id=000000000421",
        "file": "last_link_notice.txt"
    },
    "📜 국편위 학술소식": {
        "url": "https://www.history.go.kr/rss/rssfeed.do?id=000000000424",
        "file": "last_link_academic.txt"
    }
}

def send_telegram(board_name, title, link):
    """텔레그램 메시지를 전송하는 함수"""
    print(f">>> [{board_name}] 알림 발송을 시도합니다...")
    msg = f"<b>{board_name} 새 소식</b>\n\n{title}\n\n<a href='{link}'>링크 바로가기</a>"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    
    try:
        res = requests.post(url, data=params, timeout=10)
        if res.status_code == 200:
            print(f">>> [{board_name}] 전송 성공!")
        else:
            print(f">>> [{board_name}] 전송 실패 (응답 코드: {res.status_code})")
    except Exception as e:
        print(f">>> [{board_name}] 전송 중 에러 발생: {e}")

def main():
    # 서버 접속 시 브라우저처럼 보이게 하는 설정 (접속 차단 방지)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for name, info in BOARDS.items():
        print(f"\n--- {name} 체크 중 ---")
        try:
            # RSS 데이터 가져오기
            response = requests.get(info["url"], headers=headers, timeout=15)
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                print(f"    가져올 데이터가 없습니다.")
                continue

            # 최신 글 정보 추출
            latest_link = feed.entries[0].link
            latest_title = feed.entries[0].title
            
            # 이전 기록(마지막 알림 링크) 확인
            last_link = ""
            if os.path.exists(info["file"]):
                with open(info["file"], "r") as f:
                    last_link = f.read().strip()
            
            print(f"    최신 제목: {latest_title}")
            print(f"    마지막 기록: {last_link}")

            # 새로운 글인지 비교
            if latest_link != last_link:
                print(f"    [발견] 새로운 글입니다! 알림을 보냅니다.")
                send_telegram(name, latest_title, latest_link)
                # 새로운 링크를 각 게시판 전용 파일에 저장
                with open(info["file"], "w") as f:
                    f.write(latest_link)
            else:
                print(f"    이미 확인한 소식입니다.")

        except Exception as e:
            print(f"    [{name}] 작업 중 오류가 발생했습니다: {e}")
            
    print("\n--- 모든 게시판 확인 완료 ---")

if __name__ == "__main__":
    main()
