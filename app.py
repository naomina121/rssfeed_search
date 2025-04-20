import os
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

app = Flask(__name__)

# ロギング設定 (Gunicorn 等を使う場合、そちらの設定も考慮)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    # templates/index.html を表示
    return render_template('index.html')

@app.route('/check_feed', methods=['POST'])
def check_feed():
    data = request.get_json()
    website_url = data.get('website_url') if data else None

    if not website_url:
        app.logger.warning("URLが空でリクエストがありました。")
        return jsonify({'error': 'URLが入力されていません。'}), 400

    # URL形式の基本チェック
    try:
        parsed_url = urlparse(website_url)
        if not all([parsed_url.scheme, parsed_url.netloc]) or parsed_url.scheme not in ['http', 'https']:
            raise ValueError("無効なURL形式です (http/httpsではありません)。")
    except ValueError as e:
        app.logger.warning(f"無効なURL形式: {website_url} - {e}")
        return jsonify({'error': str(e)}), 400

    app.logger.info(f"フィードURLをチェック中: {website_url}")
    feed_url = find_feed_url(website_url)

    if feed_url:
        app.logger.info(f"フィードURL発見: {feed_url} (元URL: {website_url})")
        return jsonify({'feed_url': feed_url})
    else:
        app.logger.warning(f"フィードURLが見つかりませんでした: {website_url}")
        # 見つからなかった場合でも成功としてNoneを返す
        return jsonify({'feed_url': None})

def find_feed_url(url):
    """指定されたURLからRSS/AtomフィードのURLを探す"""
    try:
        headers = {
            # 偽装ユーザーエージェント (正直に名乗るのが望ましい場合も)
            'User-Agent': 'Mozilla/5.0 (compatible; FeedCheckerBot/1.0)'
        }
        # タイムアウトを10秒に設定
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        # エラーがあれば例外発生
        response.raise_for_status()

        # リダイレクト後の最終的なURLを基準にする
        final_url = response.url
        soup = BeautifulSoup(response.content, 'html.parser')

        # <link rel="alternate"> タグを探す
        feed_link = soup.find('link', rel='alternate', type=lambda t: t and ('rss+xml' in t or 'atom+xml' in t))
        if feed_link and feed_link.get('href'):
            # 絶対URLに変換して返す
            return urljoin(final_url, feed_link.get('href'))

        # --- ここに他の検出ロジックを追加可能 ---
        # 例: 一般的なパスを試す
        # common_paths = ['/feed', '/rss', '/atom.xml', '/feed.xml']
        # for path in common_paths:
        #     potential_feed_url = urljoin(final_url, path)
        #     try:
        #         # HEADリクエストで存在確認だけ行う
        #         head_res = requests.head(potential_feed_url, headers=headers, timeout=5, allow_redirects=True)
        #         if head_res.status_code == 200:
        #             # Content-Typeも確認するとより確実
        #             # content_type = head_res.headers.get('Content-Type', '').lower()
        #             # if 'xml' in content_type or 'application/rss' in content_type or 'application/atom' in content_type:
        #             app.logger.info(f"一般的なパスでフィードURL発見: {potential_feed_url}")
        #             return potential_feed_url
        #     except requests.exceptions.RequestException:
        #         continue # 試してダメなら次へ
        # -----------------------------------------

        return None

    except requests.exceptions.Timeout:
        app.logger.error(f"タイムアウト発生: {url}")
        return None
    except requests.exceptions.RequestException as e:
        app.logger.error(f"リクエストエラー ({url}): {e}")
        return None
    except Exception as e:
        # BeautifulSoupのパースエラーなども含む
        app.logger.error(f"予期せぬエラー ({url}): {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')