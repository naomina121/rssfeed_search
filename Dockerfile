# ベースイメージとしてPython 3.9-slimを使用
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存パッケージのコピーとインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Flaskのデフォルトポートを公開
EXPOSE 5000

# コンテナ起動時のコマンド
CMD ["python", "app.py"]
