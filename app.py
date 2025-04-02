from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# HTMLテンプレート（CSSとJavaScriptを含む）
html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>フィードURL確認フォーム</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f7f7f7;
      margin: 0;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    h1 {
      color: #333;
    }
    form {
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
      max-width: 400px;
      width: 100%;
    }
    input[type="url"] {
      width: calc(100% - 22px);
      padding: 10px;
      margin-bottom: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    button {
      padding: 10px 15px;
      border: none;
      background: #007BFF;
      color: #fff;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover {
      background: #0056b3;
    }
    #result {
      margin-top: 20px;
      padding: 15px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
      max-width: 400px;
      width: 100%;
      word-break: break-all;
    }
  </style>
</head>
<body>
  <h1>フィードURL確認フォーム</h1>
  <form id="feedForm">
    <label for="website_url">ウェブサイトのURLを入力してください:</label>
    <input type="url" id="website_url" name="website_url" placeholder="https://example.com" required>
    <button type="submit">送信</button>
  </form>
  <div id="result"></div>

  <script>
    document.getElementById('feedForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const urlInput = document.getElementById('website_url');
      const resultDiv = document.getElementById('result');

      resultDiv.innerHTML = 'チェック中...';

      fetch('/check_feed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ website_url: urlInput.value })
      })
      .then(response => response.json())
      .then(data => {
        if(data.feed_url) {
          resultDiv.innerHTML = `<strong>Feed URL:</strong> <a href="${data.feed_url}" target="_blank">${data.feed_url}</a>`;
        } else {
          resultDiv.innerHTML = '取得できませんでした';
        }
      })
      .catch(error => {
        resultDiv.innerHTML = 'エラーが発生しました';
        console.error(error);
      });
    });
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(html_template)

@app.route('/check_feed', methods=['POST'])
def check_feed():
    data = request.get_json()
    website_url = data.get('website_url') if data else None
    if not website_url:
        return jsonify({'error': 'URLが入力されていません。'}), 400

    feed_url = get_feed_url(website_url)
    return jsonify({'feed_url': feed_url})

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
