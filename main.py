import feedparser
import datetime
import pytz

# 1. 定義新聞來源 (你可以隨時增加或刪除這裡的連結)
rss_urls = {
    "BBC News": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "FOX News": "http://feeds.foxnews.com/foxnews/latest",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "ABC News": "https://abcnews.go.com/abcnews/topstories"
}

# 2. 定義網頁的外觀 (HTML 模板)
# 這裡面的 CSS 決定了網頁長什麼樣子
html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日國際新聞晨報</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background-color: #333; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .update-time {{ color: #ccc; font-size: 0.9em; margin-top: 5px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding: 20px; background: white; border-radius: 0 0 8px 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .card {{ border: 1px solid #eee; padding: 15px; border-radius: 8px; }}
        .card h2 {{ color: #d32f2f; margin-top: 0; border-bottom: 2px solid #f4f4f4; padding-bottom: 10px; font-size: 1.2em; }}
        .news-list {{ list-style: none; padding: 0; }}
        .news-item {{ margin-bottom: 12px; }}
        .news-item a {{ text-decoration: none; color: #333; font-weight: 500; display: block; }}
        .news-item a:hover {{ color: #0056b3; text-decoration: underline; }}
        .date {{ font-size: 0.8em; color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 每日國際新聞彙整</h1>
            <div class="update-time">最後更新 (台灣時間): {update_time}</div>
        </header>
        <div class="grid">
            {content}
        </div>
    </div>
</body>
</html>
"""

def fetch_news():
    cards_html = ""
    # 設定台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    # 開始一個一個抓取新聞
    for source_name, url in rss_urls.items():
        print(f"正在抓取: {source_name}...")
        
        try:
            # 使用 feedparser 下載並分析 RSS
            feed = feedparser.parse(url)
            
            news_items_html = "<ul class='news-list'>"
            
            # 只取前 5 則新聞
            for entry in feed.entries[:5]:
                title = entry.title
                link = entry.link
                # 嘗試抓取發布時間，如果沒有就留空
                pub_date = entry.published if 'published' in entry else ""
                
                # 組合每一則新聞的 HTML
                news_items_html += f"""
                <li class="news-item">
                    <a href="{link}" target="_blank">➤ {title}</a>
                    <span class="date">{pub_date}</span>
                </li>
                """
            news_items_html += "</ul>"

            # 將這家媒體的內容包成一張卡片
            cards_html += f"""
            <div class="card">
                <h2>{source_name}</h2>
                {news_items_html}
            </div>
            """
            
        except Exception as e:
            print(f"抓取 {source_name} 時發生錯誤: {e}")
            cards_html += f"<div class='card'><h2>{source_name}</h2><p>暫時無法讀取內容。</p></div>"

    # 將抓到的內容填入模板
    final_html = html_template.format(update_time=current_time, content=cards_html)
    
    # 存檔為 index.html (這就是我們最後看到的網頁)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("成功！index.html 已生成。")

if __name__ == "__main__":
    fetch_news()