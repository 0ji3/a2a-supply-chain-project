# 開発環境セットアップガイド

このドキュメントは、ローカル開発環境のセットアップ手順を説明します。

---

## 📋 前提条件

### 必須ソフトウェア

| ソフトウェア | 最小バージョン | 確認コマンド |
|------------|--------------|-------------|
| Python | 3.11+ | `python --version` |
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker-compose --version` |
| Git | 2.30+ | `git --version` |
| Foundry (forge) | Latest | `forge --version` |

### オプションソフトウェア

- **PostgreSQL Client**: データベース操作用（`psql`）
- **Redis Client**: キャッシュ確認用（`redis-cli`）
- **curl or httpie**: API テスト用

---

## 🚀 セットアップ手順

### ステップ1: リポジトリのクローン

```bash
# リポジトリをクローン（実際のURLに置き換え）
git clone <repository-url>
cd a2a-supply-chain

# ブランチ確認
git branch
```

### ステップ2: Python環境のセットアップ

#### 2.1 仮想環境の作成

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境の有効化
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 仮想環境が有効になっていることを確認
which python  # macOS/Linux
where python  # Windows
```

#### 2.2 依存パッケージのインストール

```bash
# 依存パッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt

# インストール確認
pip list
```

**主要パッケージの確認**:
```bash
# Web3
python -c "import web3; print('web3:', web3.__version__)"

# FastAPI
python -c "import fastapi; print('fastapi:', fastapi.__version__)"

# SQLAlchemy
python -c "import sqlalchemy; print('sqlalchemy:', sqlalchemy.__version__)"

# scikit-learn
python -c "import sklearn; print('sklearn:', sklearn.__version__)"

# scipy
python -c "import scipy; print('scipy:', scipy.__version__)"
```

### ステップ3: 環境変数の設定

```bash
# .env.example を .env にコピー
cp .env.example .env

# .envファイルを編集（必要に応じて）
# 多くの設定はデフォルトで動作するが、以下は確認推奨:
# - DEPLOYER_PRIVATE_KEY (Anvilのテストアカウント)
# - DATABASE_URL (PostgreSQL接続情報)
# - REDIS_URL (Redis接続情報)
```

**.env の主要設定**:
```bash
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/a2a_supply_chain

# Redis
REDIS_URL=redis://localhost:6379

# Blockchain
ANVIL_RPC_URL=http://localhost:8545
CHAIN_ID=31337

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

### ステップ4: Docker環境の起動

```bash
# すべてのサービスを起動
docker-compose up -d

# サービスの状態確認
docker-compose ps

# ログ確認
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f anvil
```

**期待される出力**:
```
NAME                IMAGE                               STATUS
a2a-postgres        postgres:15-alpine                  Up
a2a-redis           redis:7-alpine                      Up
a2a-anvil           ghcr.io/foundry-rs/foundry:latest  Up
```

#### 4.1 PostgreSQL接続確認

```bash
# PostgreSQLコンテナに接続
docker-compose exec postgres psql -U postgres -d a2a_supply_chain

# テーブル一覧表示
\dt

# データ確認
SELECT COUNT(*) FROM pos_sales;
SELECT * FROM stores;
SELECT * FROM products;

# 終了
\q
```

**期待される出力**:
- pos_sales: 30行（30日分のデータ）
- stores: 1行（東京練馬店）
- products: 1行（トマト）

#### 4.2 Redis接続確認

```bash
# Redisコンテナに接続
docker-compose exec redis redis-cli

# 疎通確認
PING

# 終了
EXIT
```

**期待される出力**: `PONG`

#### 4.3 Anvil接続確認

```bash
# Anvilの状態確認
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

**期待される出力**:
```json
{"jsonrpc":"2.0","id":1,"result":"0x0"}
```

### ステップ5: データベース初期化（自動実行済み）

Docker ComposeでPostgreSQLが起動すると、以下のスクリプトが自動実行されます:
1. `db/schema.sql` - スキーマ作成
2. `db/seed_data.sql` - テストデータ投入

手動で再初期化する場合:
```bash
# PostgreSQLコンテナ内で実行
docker-compose exec postgres psql -U postgres -d a2a_supply_chain -f /docker-entrypoint-initdb.d/01_schema.sql
docker-compose exec postgres psql -U postgres -d a2a_supply_chain -f /docker-entrypoint-initdb.d/02_seed_data.sql
```

### ステップ6: Foundryのセットアップ（Phase 2以降）

Phase 1ではブロックチェーン機能は使用しませんが、準備として:

```bash
# Foundryのインストール（未インストールの場合）
curl -L https://foundry.paradigm.xyz | bash
foundryup

# バージョン確認
forge --version
anvil --version
cast --version

# Foundryプロジェクトの初期化（contracts/ディレクトリ）
cd contracts
forge init --no-git --force .
forge build
```

---

## ✅ 動作確認

### テストスクリプトの実行

```bash
# プロジェクトルートディレクトリで実行
python test_agents.py
```

**期待される出力**:
```
🚀 Phase 1 エージェント動作テスト開始

============================================================
需要予測エージェントテスト
============================================================

✓ 実行成功: True
✓ 予測販売数量: 378個
✓ 信頼区間: {'lower': 264, 'upper': 491}
✓ 信頼度: 0.85
✓ 実行時間: 0.000秒
✓ コスト: 3 JPYC

============================================================
在庫最適化エージェントテスト
============================================================

✓ 実行成功: True
✓ 推奨発注量: 292個
✓ 推奨サプライヤー: サプライヤーA（熊本）
✓ 発注タイミング: 03:00
✓ 安全在庫: 56個
✓ 信頼度: 0.89
✓ 実行時間: 0.003秒
✓ コスト: 15 JPYC

============================================================
総合結果
============================================================

✓ 合計コスト: 18 JPYC
✓ 合計実行時間: 0.003秒

✅ すべてのテストが成功しました！
```

### pytestの実行（Phase 1.5以降）

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ付きで実行
pytest tests/ -v --cov=python --cov-report=html

# 特定のテストのみ実行
pytest tests/test_agents.py -v
```

---

## 🔧 開発ツールのセットアップ

### コードフォーマッター

```bash
# Blackのインストール（requirements.txtに含まれている）
black --version

# コードフォーマット実行
black python/

# 確認のみ（変更なし）
black python/ --check
```

### インポート整理

```bash
# isortのインストール（requirements.txtに含まれている）
isort --version

# インポート整理実行
isort python/

# 確認のみ
isort python/ --check-only
```

### 型チェック

```bash
# mypyのインストール（requirements.txtに含まれている）
mypy --version

# 型チェック実行
mypy python/
```

### リンター

```bash
# flake8のインストール（requirements.txtに含まれている）
flake8 --version

# リント実行
flake8 python/ --max-line-length=100
```

### pre-commitフック（Optional）

```bash
# pre-commitのインストール
pip install pre-commit

# .pre-commit-config.yaml作成
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
EOF

# フックのインストール
pre-commit install

# 手動実行
pre-commit run --all-files
```

---

## 🆘 トラブルシューティング

### Docker関連

#### Dockerコンテナが起動しない
```bash
# コンテナの状態確認
docker-compose ps

# ログ確認
docker-compose logs postgres
docker-compose logs redis
docker-compose logs anvil

# コンテナの再起動
docker-compose down
docker-compose up -d
```

#### ポートが既に使用されている
```bash
# ポート使用状況確認
# macOS/Linux:
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8545  # Anvil

# Windows:
netstat -ano | findstr :5432
netstat -ano | findstr :6379
netstat -ano | findstr :8545

# 既存プロセスを停止するか、docker-compose.ymlのポート番号を変更
```

#### ボリュームのクリア
```bash
# すべてのコンテナとボリュームを削除して再作成
docker-compose down -v
docker-compose up -d
```

### Python関連

#### パッケージのインストールエラー
```bash
# pipのアップグレード
pip install --upgrade pip

# キャッシュクリア
pip cache purge

# 再インストール
pip install -r requirements.txt --no-cache-dir
```

#### モジュールが見つからない
```bash
# Pythonパスの確認
python -c "import sys; print('\n'.join(sys.path))"

# プロジェクトルートをPYTHONPATHに追加
# Linux/macOS:
export PYTHONPATH="${PYTHONPATH}:/path/to/a2a-supply-chain"

# Windows:
set PYTHONPATH=%PYTHONPATH%;C:\path\to\a2a-supply-chain
```

#### 仮想環境が有効にならない
```bash
# 仮想環境を削除して再作成
rm -rf venv
python -m venv venv
source venv/bin/activate  # または venv\Scripts\activate
pip install -r requirements.txt
```

### データベース関連

#### PostgreSQL接続エラー
```bash
# PostgreSQLが起動しているか確認
docker-compose ps postgres

# ログ確認
docker-compose logs postgres

# 接続情報の確認
cat .env | grep DATABASE_URL

# 手動接続テスト
psql postgresql://postgres:password@localhost:5432/a2a_supply_chain
```

#### スキーマが作成されていない
```bash
# 手動でスキーマ実行
docker-compose exec postgres psql -U postgres -d a2a_supply_chain < db/schema.sql

# または、コンテナを再作成
docker-compose down
docker-compose up -d postgres
```

### Redis関連

#### Redis接続エラー
```bash
# Redisが起動しているか確認
docker-compose ps redis

# ログ確認
docker-compose logs redis

# 手動接続テスト
docker-compose exec redis redis-cli ping
```

---

## 📊 環境の検証

以下のスクリプトで環境が正しくセットアップされているか確認:

```bash
# 環境検証スクリプト
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "🔍 環境検証スクリプト"
echo "================================"

# Python確認
echo "✓ Python:"
python --version || echo "❌ Python not found"

# Docker確認
echo "✓ Docker:"
docker --version || echo "❌ Docker not found"

# Docker Compose確認
echo "✓ Docker Compose:"
docker-compose --version || echo "❌ Docker Compose not found"

# PostgreSQL確認
echo "✓ PostgreSQL:"
docker-compose exec postgres psql -U postgres -d a2a_supply_chain -c "SELECT 1" > /dev/null 2>&1 && echo "Connected" || echo "❌ Connection failed"

# Redis確認
echo "✓ Redis:"
docker-compose exec redis redis-cli PING > /dev/null 2>&1 && echo "Connected" || echo "❌ Connection failed"

# Anvil確認
echo "✓ Anvil:"
curl -s -X POST http://localhost:8545 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null && echo "Connected" || echo "❌ Connection failed"

echo "================================"
echo "検証完了"
EOF

chmod +x verify_setup.sh
./verify_setup.sh
```

---

## 🎓 次のステップ

環境セットアップが完了したら:

1. **ドキュメントを読む**
   - `docs/CLAUDE.md` - プロジェクト全体の理解
   - `docs/phase1-implementation-plan.md` - 現在のタスク確認

2. **実装を開始**
   - `docs/implementation-guide.md` を参照
   - Phase 1のタスクから着手

3. **コーディング規約を確認**
   - `docs/coding-standards.md` を参照

---

**最終更新**: 2025-01-23  
**次回更新予定**: Phase 2準備時