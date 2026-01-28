# A2A Supply Chain Optimization - Python Application
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システムパッケージ更新
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
# requirements.txtは親ディレクトリにあるため、docker-compose経由でマウント
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY python/ .

# 環境変数
ENV PYTHONUNBUFFERED=1

# デフォルトコマンド
CMD ["python", "main.py"]
