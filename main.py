import feedparser
import datetime
import pytz
import os
import random
# 使用 Google 全新版 SDK
from google import genai

# =================設定區=================
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")

rss_urls = {
    "BBC News": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "FOX News": "http://feeds.foxnews.com/foxnews/latest",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "ABC News": "https://abcnews.go.com/abcnews/topstories"
}

html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日英語新聞與閱讀測驗</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; padding: 20px; max-width: 1000px; margin: 0 auto; line-height: 1.6; }}
        header {{ text-align: center; margin-bottom: 40px; padding: 20px; background: #2c3e50; color: white; border-radius: 12px; }}
        .quiz-section {{ background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 40px; border-top: 5px solid #e67e22; }}
        .quiz-title {{ color: #e67e22; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }}
        .question-card {{ background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #eee; }}
        .question-text {{ font-weight: bold; color: #2c3e50; font-size: 1.1em; }}
        .options {{ margin: 10px 0; }}
        details {{ margin-top: 10px; cursor: pointer; background: #e8f6f3; padding: 10px; border-radius: 5px; }}
        summary {{ font-weight: bold; color: #16a085; }}
        .explanation {{ margin-top: 10px; color: #555; font-size: 0.95em; }}
        .news-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #2980b9; margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .news-item {{ margin-bottom: 15px; border-bottom: 1px dashed #eee; padding-bottom: 10px; }}
        .news-item a {{ text-decoration: none; color: #34495e; font-weight: 600; }}
        .news-item a:hover {{ color: #e67e22; }}
    </style>
</head>
<body>
    <header>
        <h1>📰 每日英語閱讀挑戰</h1>
        <div>{update_time}</div>
    </header>

    <div class="quiz-section">
        <h2 class="quiz-title">🧠 Daily Reading Comprehension Quiz (AI Generated)</h2>
        <p>請閱讀下方新聞標題與摘要，回答下列問題：</p>
        {quiz_content}
    </div>

    <div class="news-grid">
        {news_content}
    </div>
</body>
</html>
"""

def generate_quiz_with_gemini(news_summaries):
    if not GENAI_API_KEY:
        return "<p>⚠️ 請先設定 GitHub Secret (GEMINI_API_KEY)</p>"

    try:
        # 新版 SDK 的呼叫方式
        client = genai.Client(api_key=GENAI_API_KEY)
        
        prompt = f"""
        You are an English teacher. Based on the following news summaries, create 5 multiple-choice reading comprehension questions.
        
        NEWS DATA:
        {news_summaries}
        
        REQUIREMENTS:
        1. Create 5 questions.
        2. Format output as raw HTML only.
        3. Structure:
           <div class="question-card">
               <div class="question-text">Question: ...</div>
               <div class="options">A)... B)... C)... D)...</div>
               <details><summary>Check Answer</summary><div class="explanation">...</div></details>
           </div>
        4. No markdown ```html tags.
        """
        
        # 使用最新的 Gemini 1.5 Flash 模型
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        return response.text.replace("```html", "").replace("```", "")
        
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        return f"<p>AI 休息中 ({str(e)})</p>"

def fetch_news():
    cards_html = ""
    all_news_for_quiz = []
    
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    for source, url in rss_urls.items():
        try:
            feed = feedparser.parse(url)
            news_items_html = ""
            for entry in feed.entries[:5]:
                title = entry.title
                link = entry.link
                summary = entry.summary if 'summary' in entry else entry.description if 'description' in entry else ""
                clean_summary = summary.replace('<', '[').replace('>', ']')[:200]
                
                all_news_for_quiz.append(f"Source: {source}\nTitle: {title}\nSummary: {clean_summary}\n")
                
                news_items_html += f"""
                <div class="news-item">
                    <a href="{link}" target="_blank">{title}</a>
                    <div style="font-size:0.85em; color:#666;">{clean_summary}...</div>
                </div>
                """
            cards_html += f"<div class='card'><h2>{source}</h2>{news_items_html}</div>"
        except Exception as e:
            print(f"Error {source}: {e}")

    print("正在請求 Gemini AI 出題...")
    # 隨機選取新聞以避免過長
    selected_news = random.sample(all_news_for_quiz, min(len(all_news_for_quiz), 8))
    quiz_html = generate_quiz_with_gemini("\n".join(selected_news))

    final_html = html_template.format(update_time=now, quiz_content=quiz_html, news_content=cards_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("完成！")

if __name__ == "__main__":
    fetch_news()
