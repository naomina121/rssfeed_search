from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# HTMLフォームのテンプレート
form_html = '''
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>URL入力フォーム</title>
</head>
<body>
  <h1>フィードURL確認フォーム</h1>
  <form action="/check_feed" method="post">
    <label for="website_url">ウェブサイトのURLを入力してください:</label>
    <input type="url" id="website_url" name="website_url" placeholder="https://example.com" required>
    <button type="submit">送信</button>
  </form>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(form_html)

@app.route('/check_feed', methods=['POST'])
def check_feed():
    website_url = request.form.get('website_url')
    if not website_url:
        return "URLが入力されていません。", 400

    feed_url = get_feed_url(website_url)
    if feed_url:
        result = f"Feed URL: {feed_url}"
    else:
        result = "取得できませんでした"
    return result

def get_feed_url(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        # RSSやAtomフィードの<link>タグを検索
        feed_link = soup.find('link', rel='alternate', type=lambda t: t and ('rss+xml' in t or 'atom+xml' in t))
        if feed_link and feed_link.get('href'):
            return urljoin(url, feed_link.get('href'))
    except Exception as e:
        print("Error:", e)
    return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
