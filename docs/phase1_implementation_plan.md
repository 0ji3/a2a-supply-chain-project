# Phase 1 実装計画

**フェーズ**: MVP（Minimum Viable Product）  
**期間**: 1-2週間  
**目標**: 基本的なエージェント動作とデータフロー確認

---

## 📊 進捗サマリー

| カテゴリ | 完了 | 総数 | 進捗率 |
|---------|-----|------|--------|
| 環境構築 | 5 | 5 | 100% |
| エージェント実装 | 3 | 6 | 50% |
| インフラ統合 | 0 | 3 | 0% |
| API実装 | 0 | 4 | 0% |
| テスト | 2 | 5 | 40% |
| **総合** | **10** | **23** | **43%** |

---

## ✅ タスク詳細

### 1. 環境構築（100% 完了）

#### 1.1 プロジェクト初期化
- [x] ディレクトリ構造作成
- [x] .gitignore設定
- [x] README.md作成

#### 1.2 依存関係管理
- [x] requirements.txt作成
- [x] Python仮想環境セットアップ
- [x] 依存パッケージインストール検証

#### 1.3 Docker環境
- [x] docker-compose.yml作成
  - PostgreSQL 15
  - Redis 7
  - Anvil（Foundry）
- [x] ヘルスチェック設定
- [x] ボリューム設定

#### 1.4 環境変数
- [x] .env.example作成
- [x] Anvilテストアカウント設定
- [x] データベース接続情報

#### 1.5 データベース
- [x] schema.sql作成（簡易版）
  - stores（店舗マスタ）
  - products（商品マスタ）
  - pos_sales（POS販売データ）
  - suppliers（サプライヤーマスタ）
  - supplier_products（サプライヤー商品関連）
  - optimization_tasks（最適化タスク）
  - agent_executions（エージェント実行履歴）
  - inventory（在庫データ）
- [x] seed_data.sql作成
  - 1店舗（東京練馬店）
  - 1商品（トマト）
  - 2サプライヤー
  - 30日分のPOSデータ

---

### 2. エージェント実装（50% 完了）

#### 2.1 基底クラス（100% 完了）
- [x] `python/agents/base.py` 実装
  - PaymentScheme Enum（exact/upto/deferred）
  - PaymentConfig dataclass
  - AgentResult dataclass
  - Agent 抽象基底クラス
  - calculate_cost()メソッド
  - _execute_with_timing()メソッド

#### 2.2 需要予測エージェント（100% 完了）
- [x] `python/agents/demand_forecast.py` 実装
  - DemandForecastAgent クラス
  - POSデータ取得（_fetch_pos_data）
  - 7日移動平均予測
  - 信頼区間算出（95%）
  - X402 upto方式設定（3 JPYC + 0.02/1000レコード）
- [x] 単体テスト実装
- [x] テスト成功確認

**テスト結果**:
```
✓ 予測販売数量: 378個
✓ 信頼区間: 264個 〜 491個
✓ 信頼度: 0.85
✓ 実行時間: 0.000秒
✓ コスト: 3 JPYC
```

#### 2.3 在庫最適化エージェント（100% 完了）
- [x] `python/agents/inventory_optimizer.py` 実装
  - InventoryOptimizerAgent クラス
  - ニュースベンダーモデル実装
  - サプライヤー選定（_get_best_supplier）
  - 発注タイミング計算（_calculate_order_time）
  - X402 exact方式設定（15 JPYC固定）
- [x] 単体テスト実装
- [x] テスト成功確認

**テスト結果**:
```
✓ 推奨発注量: 292個
✓ 推奨サプライヤー: サプライヤーA（熊本）
✓ 発注タイミング: 03:00
✓ 安全在庫: 56個
✓ 信頼度: 0.89
✓ 実行時間: 0.003秒
✓ コスト: 15 JPYC
```

#### 2.4 レポート生成エージェント（0% - 次のタスク）
- [ ] `python/agents/report_generator.py` 作成
- [ ] ReportGeneratorAgent クラス実装
  - X402 deferred方式設定（5 JPYC）
  - 最適化結果の統合
  - フォーマット済みレポート生成
- [ ] 出力フォーマット
  - コンソール出力（人間可読）
  - JSON出力（API用）
  - レポートテンプレート
- [ ] 単体テスト作成
- [ ] テスト実行

**期待される出力例**:
```
🍅 トマト（中玉・国産）最適化レポート
実行日：2025-01-24（金）

📦 推奨発注量：280個
🏪 発注先：サプライヤーA（信頼度95点）
⏰ 発注時刻：午前5:00
💰 調達単価：95円/個

💴 推奨販売価格：198円

📊 予測結果：
  - 販売予測：350個（±30個）
  - 廃棄予測：8個（2.3%）
  - 期待粗利：¥18,200

✅ コスト：18 JPYC
⏱️ 実行時間：0.003秒
```

#### 2.5 Orchestrator（100% 完了）
- [x] `python/orchestrator.py` 実装
  - AgentCoordinator クラス
  - execute_optimization_task()メソッド
  - タスクレコード管理
  - エージェント実行履歴記録
- [x] 統合テスト実装
- [x] テスト成功確認

#### 2.6 価格設定エージェント（Phase 2）
Phase 2で実装予定

---

### 3. インフラ統合（0% - 優先タスク）

#### 3.1 データベース統合
- [ ] PostgreSQL接続テスト
  - docker-compose up実行
  - 接続確認
  - スキーマ作成確認
  - テストデータ投入確認
- [ ] SQLAlchemy ORM設定
  - `python/database.py` の動作確認
  - モデルクラス作成（必要に応じて）
  - セッション管理テスト
- [ ] トランザクション管理
  - コミット/ロールバック処理
  - エラー時のリカバリ
- [ ] マイグレーション（Optional Phase 1）
  - Alembic設定（Phase 2で本格的に）

**検証項目**:
```bash
# PostgreSQL接続確認
docker-compose ps
psql -U postgres -h localhost -p 5432 -d a2a_supply_chain

# テーブル確認
\dt

# データ確認
SELECT COUNT(*) FROM pos_sales;
SELECT * FROM stores;
SELECT * FROM products;
```

#### 3.2 Redis統合
- [ ] Redis接続テスト
  - docker-compose up実行
  - 接続確認
- [ ] キャッシュ実装
  - `python/utils/cache.py` 作成
  - キャッシュキー設計
    - 需要予測: `df:{product_sku}:{store_id}:{date}` (TTL: 24h)
    - サプライヤー品質: `sq:{supplier_id}` (TTL: 7日)
  - get/set/delete実装
- [ ] キャッシュ統合テスト
  - エージェントからのキャッシュ利用
  - TTL動作確認

**検証項目**:
```bash
# Redis接続確認
docker-compose exec redis redis-cli ping

# キャッシュ確認
docker-compose exec redis redis-cli
> KEYS *
> GET df:tomato-medium-domestic:S001:2025-01-24
```

#### 3.3 Anvil統合（Phase 2で本格化）
- [ ] Anvil起動確認
  - docker-compose up実行
  - RPC接続確認
- [ ] web3.py接続テスト
  - `python/utils/blockchain.py` 作成
  - テストアカウント接続
  - 簡易トランザクション送信

**検証項目**:
```bash
# Anvil接続確認
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

---

### 4. API実装（0% - 次のタスク）

#### 4.1 FastAPI基本セットアップ
- [ ] `python/api/main.py` 作成
  - FastAPIアプリ初期化
  - CORS設定
  - ロギング設定
  - ヘルスチェックエンドポイント
- [ ] `python/api/routes.py` 作成
  - ルーター登録
- [ ] 起動確認
  ```bash
  uvicorn api.main:app --reload --port 8000
  ```

#### 4.2 最適化APIエンドポイント
- [ ] POST /api/v1/optimize 実装
  - リクエストバリデーション（Pydantic）
  - バックグラウンドタスク登録
  - execution_id返却
- [ ] GET /api/v1/optimize/{execution_id} 実装
  - タスクステータス取得
  - 結果取得
- [ ] GET /api/v1/optimize 実装
  - タスク一覧取得
  - フィルタ機能（status, product_sku, store_id）
- [ ] APIテスト
  ```bash
  # タスク作成
  curl -X POST http://localhost:8000/api/v1/optimize \
    -H "Content-Type: application/json" \
    -d '{"product_sku": "tomato-medium-domestic", "store_id": "S001"}'
  
  # 結果取得
  curl http://localhost:8000/api/v1/optimize/{execution_id}
  ```

#### 4.3 レポートAPIエンドポイント（Phase 1.5）
- [ ] GET /api/v1/reports/{execution_id} 実装
- [ ] GET /api/v1/reports/{execution_id}/download 実装
  - PDF生成（Optional）
  - JSON出力

#### 4.4 認証実装（Phase 2）
JWT認証はPhase 2で実装

---

### 5. テスト（40% 完了）

#### 5.1 ユニットテスト
- [x] エージェント基底クラステスト
  - PaymentScheme動作確認
  - コスト計算ロジック
- [x] 需要予測エージェントテスト
  - モックDBでのテスト
  - 予測精度確認
- [x] 在庫最適化エージェントテスト
  - ニュースベンダーモデル検証
- [ ] レポート生成エージェントテスト
- [ ] Orchestratorテスト（詳細）

**カバレッジ目標**: 60%以上

#### 5.2 統合テスト
- [x] エージェント間通信テスト（基本）
  - 需要予測 → 在庫最適化
- [ ] エージェント間通信テスト（完全版）
  - 需要予測 → 在庫最適化 → レポート生成
- [ ] データベース統合テスト
  - 実際のPostgreSQL使用
  - トランザクション確認
- [ ] キャッシュ統合テスト
  - Redis使用
  - キャッシュヒット/ミス確認

#### 5.3 APIテスト
- [ ] エンドポイントテスト
  - 正常系
  - 異常系（バリデーションエラー）
- [ ] パフォーマンステスト
  - レスポンスタイム確認
  - 同時実行テスト

#### 5.4 エンドツーエンドテスト
- [ ] フルフロー実行
  1. API経由でタスク作成
  2. エージェント実行
  3. 結果取得
  4. レポート生成
- [ ] エラーハンドリング確認
  - データベース接続エラー
  - エージェント実行エラー
  - タイムアウト

#### 5.5 テスト自動化
- [ ] pytest設定
- [ ] GitHub Actions（Optional Phase 1）
- [ ] カバレッジレポート

---

## 📋 次の1週間のタスク（優先順）

### Day 1-2: レポート生成 + DB統合
1. ✅ レポート生成エージェント実装
2. ✅ PostgreSQL実接続テスト
3. ✅ エージェント → PostgreSQL統合

### Day 3-4: キャッシュ + API基本
4. ✅ Redis統合実装
5. ✅ FastAPI基本セットアップ
6. ✅ ヘルスチェックエンドポイント

### Day 5-6: API実装
7. ✅ POST /api/v1/optimize 実装
8. ✅ GET /api/v1/optimize/{execution_id} 実装
9. ✅ 統合テスト

### Day 7: テスト + ドキュメント
10. ✅ エンドツーエンドテスト
11. ✅ ドキュメント更新
12. ✅ Phase 1完了レビュー

---

## 🎯 Phase 1 完了基準

### 機能要件
- [x] 需要予測エージェントが動作
- [x] 在庫最適化エージェントが動作
- [ ] レポート生成エージェントが動作
- [ ] REST APIで最適化タスクを実行可能
- [ ] PostgreSQL/Redisに実際に接続して動作

### 非機能要件
- [ ] 実行時間: < 60秒
- [x] コスト: ≤ 55 JPYC（現在18 JPYC）
- [x] テスト成功率: 100%
- [ ] API レスポンスタイム: < 1秒

### ドキュメント
- [x] CLAUDE.md
- [x] phase1-implementation-plan.md
- [ ] implementation-guide.md
- [ ] development-setup.md
- [ ] coding-standards.md

---

## 🚫 Phase 1スコープ外

以下はPhase 2以降で実装:
- ERC-8004スマートコントラクト
- X402決済フローの実装（Phase 1はモックのみ）
- 価格設定エージェント
- JWT認証
- LightGBMモデル（Phase 1は移動平均）
- Sepoliaテストネット

---

## 📊 進捗トラッキング

### 日次更新
毎日の作業終了時に以下を更新:
- 完了タスクを `[x]` にマーク
- 進捗サマリーの数値更新
- ブロッカーがあれば記録

### 週次レビュー
毎週金曜日:
- 進捗率確認
- 次週の計画調整
- ドキュメント更新

---

**最終更新**: 2025-01-23  
**現在のフェーズ**: Phase 1（43% 完了）  
**次回更新予定**: 2025-01-24（レポート生成実装後）