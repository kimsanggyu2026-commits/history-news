import feedparser
import requests
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

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
    msg = f"<b>{board_name} 새 소식</b>\n\n{title}\n\n<a href='{link}'>링크 바로가기</a>"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, data=params, timeout=10)

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for name, info in BOARDS.items():
        try:
            response = requests.get(info["url"], headers=headers, timeout=15)
            feed = feedparser.parse(response.text)
            if not feed.entries: continue

            last_link = ""
            if os.path.exists(info["file"]):
                with open(info["file"], "r") as f:
                    last_link = f.read().strip()
            
            # 🌟 핵심: 새 소식들을 담을 리스트를 만듭니다.
            new_posts = []
            for entry in feed.entries:
                if entry.link == last_link: # 아까 본 글을 만나면 중단!
                    break
                new_posts.append(entry)
            
            # 🌟 오래된 글부터 순서대로 보내기 위해 리스트를 뒤집습니다.
            for post in reversed(new_posts):
                send_telegram(name, post.title, post.link)
                print(f"    [발송] {post.title}")

            # 가장 최신 글 링크를 저장합니다.
            if new_posts:
                with open(info["file"], "w") as f:
                    f.write(feed.entries[0].link)

        except Exception as e:
            print(f"    에러: {e}")

if __name__ == "__main__":
    main()
