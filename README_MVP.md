# A2A Supply Chain Optimization System - MVP

生鮮品サプライチェーン最適化AI協調システムのMVP（最小実用製品）実装

## 🎯 プロジェクト概要

X402 v2プロトコル、ERC-8004、JPYCを活用したマルチエージェント決済システムのサンプル実装。
AIエージェントが協調して、スーパーマーケットの在庫・発注を最適化します。

### MVP版の機能
- ✅ 需要予測エージェント（7日移動平均ベース）
- ✅ 在庫最適化エージェント（ニュースベンダーモデル）
- ✅ エージェント協調制御（Orchestrator）
- ✅ PostgreSQLデータベース（30日分のPOSデータ）
- ✅ コンソール結果表示

## 🚀 クイックスタート

### 前提条件
- Docker Desktop
- Python 3.11+（推奨: 3.12）
- Git

### 1. 環境起動（初回のみ）

既に環境が構築済みのため、この手順はスキップできます。

```bash
# Docker起動
docker-compose up -d

# 起動確認（5秒待機）
sleep 5
docker-compose ps
```

### 2. MVPアプリケーション実行

```bash
# 簡易実行スクリプト
./run.sh

# または直接実行
./venv/bin/python python/main.py
```

### 3. 結果確認

コンソールに以下のような結果が表示されます：

```
======================================================================
📊 最適化結果レポート
======================================================================

商品: tomato-medium-domestic
店舗: S001
実行時刻: 2026-01-27 18:57:05

--- 需要予測 ---
  予測販売数量: 386 個
  信頼区間: 351 ~ 420 個
  信頼度: 85.0%
  コスト: 3 JPYC

--- 在庫最適化 ---
  推奨発注量: 301 個
  推奨サプライヤー: 静岡農協
  単価: 120.00 円
  リードタイム: 8 時間
  期待廃棄量: 0 個
  期待欠品量: 4 個
  信頼度: 89.0%
  コスト: 15 JPYC

--- サマリー ---
  合計コスト: 18 JPYC
  実行時間: 0.013 秒
  総合信頼度: 87.0%
```

## 📁 プロジェクト構成

```
a2a-supply-chain-project/
├── python/                      # Pythonエージェント実装
│   ├── agents/
│   │   ├── base.py             # エージェント基底クラス
│   │   ├── demand_forecast.py  # 需要予測エージェント
│   │   └── inventory_optimizer.py # 在庫最適化エージェント
│   ├── config.py               # 設定管理
│   ├── database.py             # データベース接続
│   ├── orchestrator.py         # エージェント協調制御
│   └── main.py                 # メインスクリプト
├── db/
│   ├── schema.sql              # データベーススキーマ
│   └── seed_data.sql           # テストデータ
├── docs/                        # 詳細ドキュメント
├── docker-compose.yml           # Docker設定
├── requirements.txt             # Python依存関係
├── .env                         # 環境変数
└── run.sh                       # 実行スクリプト
```

## 🔧 開発コマンド

### データベース確認

```bash
# PostgreSQLに接続
docker-compose exec postgres psql -U postgres -d a2a_supply_chain

# テーブル一覧
\dt

# POS販売データ確認
SELECT date, sales_quantity, price
FROM pos_sales
ORDER BY date DESC
LIMIT 10;

# 終了
\q
```

### Docker操作

```bash
# コンテナ状態確認
docker-compose ps

# ログ確認
docker-compose logs postgres

# 停止
docker-compose down

# 再起動
docker-compose up -d
```

### コード品質チェック

```bash
# コードフォーマット
./venv/bin/black python/

# インポート整理
./venv/bin/isort python/

# リント
./venv/bin/flake8 python/ --max-line-length=100
```

## 📊 技術スタック

| カテゴリ | 技術 | 用途 |
|---------|------|------|
| **言語** | Python 3.12 | エージェント実装 |
| **Database** | PostgreSQL 15 | POSデータ保存 |
| **ML** | scikit-learn, scipy | 需要予測・最適化 |
| **Data** | pandas, numpy | データ処理 |
| **Container** | Docker Compose | 環境構築 |

## 🎓 アーキテクチャ

### エージェントフロー

```
1. 需要予測エージェント
   ↓ (過去30日のPOSデータから7日移動平均で予測)
   ↓
2. 在庫最適化エージェント
   ↓ (ニュースベンダーモデルで最適発注量を計算)
   ↓
3. Orchestrator
   ↓ (結果を集約)
   ↓
4. レポート出力
```

### 決済スキーム（コンセプト）

- **需要予測**: UPTO方式（3 JPYC + 0.02 JPYC/1000レコード）
- **在庫最適化**: EXACT方式（15 JPYC固定）

## 📈 パフォーマンス

- **実行時間**: 0.013秒（目標60秒）✅
- **コスト**: 18 JPYC（目標55 JPYC）✅
- **信頼度**: 87.0%

## 🚧 Phase 2以降の追加予定機能

- FastAPI REST API
- Redis キャッシュ
- X402決済フロー（実際の決済）
- ERC-8004スマートコントラクト
- 価格設定エージェント
- DID/VC統合（サプライヤー認証）
- 総合検証エージェント

## 📚 詳細ドキュメント

- [CLAUDE.md](CLAUDE.md) - プロジェクト全体ガイド
- [docs/phase1_implementation_plan.md](docs/phase1_implementation_plan.md) - Phase 1実装計画
- [docs/system-specification.md](docs/specifications/system-specification.md) - システム仕様書

## 📝 ライセンス

このプロジェクトはサンプル実装です。

---

**最終更新**: 2026-01-27
**ステータス**: MVP実装完了 ✅
