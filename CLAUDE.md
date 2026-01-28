# CLAUDE.md - AI協調システム実装ガイド

**このドキュメントについて**: このファイルは、Claude Codeがプロジェクトを理解し、実装を進めるための包括的なガイドです。

---

## 📋 プロジェクト概要

### プロジェクト名
生鮮品サプライチェーン最適化AI協調システム

### 目的
X402 v2プロトコル、ERC-8004、JPYCを活用したマルチエージェント決済システムの実装を通じて、スーパーマーケットの食品ロス削減（12% → 4.5%）と粗利率改善（42% → 45.2%）を実現する。

### ビジネス価値
- **年間コスト削減**: 約3億円 → 1.1億円（-63%）
- **ROI**: 2,182%（1店舗・1商品あたり）
- **意思決定時間**: 30分 → 45秒（-97.5%）

### 技術的価値
- X402 v2プロトコルの実践的理解
- ERC-8004による自律エージェント管理
- Agent-to-Agent（A2A）経済圏の実証

---

## 🎯 実装アプローチ

### フェーズ構成

#### Phase 1: MVP（現在のフェーズ）
**期間**: 1-2週間  
**スコープ**:
- エージェント: 需要予測 + 在庫最適化のみ
- ブロックチェーン: Anvil（ローカル）
- 決済: X402 exact方式のみ
- 対象: 1店舗、トマト1商品

**成功基準**:
- [x] 基本的なエージェント動作確認（完了）
- [ ] X402決済フローの実装
- [ ] 簡易レポート生成

#### Phase 2: プロトコル拡張
**期間**: 1週間  
**追加要素**:
- 価格設定エージェント追加
- ERC-8004 Identity Registry実装
- X402 upto方式決済導入
- Sepolia testnet展開

#### Phase 3: 信頼レイヤー（★重要）
**期間**: 2週間  
**追加要素**:
- DID/VC統合（品質検証エージェント）
- 総合検証エージェント
- ERC-8004 Reputation Registry実装
- ERC-8004 Validation Registry実装
- X402 deferred方式決済導入

#### Phase 4: 本番展開
**期間**: 3ヶ月  
**スコープ**: 全店舗・全商品対応、Polygon本番環境

---

## 📚 ドキュメント構成と参照順序

### 1. 最初に読むべきドキュメント（理解）

#### プロジェクト全体理解
1. **README.md** - プロジェクト概要、アーキテクチャ
2. **usecase-requirements.md** - 詳細な要件定義、ビジネスロジック
3. **system-specification.md** - 技術仕様、コンポーネント設計

#### データ設計理解
4. **database-schema.md** - DB設計、ER図
5. **data-flow-diagram.md** - データフロー、キャッシュ戦略

#### 実行フロー理解
6. **sequence-diagrams.md** - エージェント協調フロー
7. **api-specification.md** - REST API仕様

### 2. 実装時に参照すべきドキュメント（実装）

#### Phase 1実装
8. **phase1-implementation-plan.md** - Phase 1タスク詳細（このドキュメント）
9. **implementation-guide.md** - 段階的実装手順
10. **development-setup.md** - 開発環境セットアップ
11. **coding-standards.md** - コーディング規約

#### Phase 2以降
12. **tech-decisions.md** - 技術選定理由とトレードオフ

---

## 🏗️ プロジェクト構造

```
a2a-supply-chain/
├── docs/                        # ドキュメント
│   ├── CLAUDE.md               # このファイル
│   ├── README.md               # プロジェクト概要
│   ├── usecase-requirements.md # 要件定義
│   ├── system-specification.md # システム仕様
│   ├── phase1-implementation-plan.md # Phase 1実装計画
│   ├── implementation-guide.md # 実装ガイド
│   ├── development-setup.md    # 開発環境セットアップ
│   └── coding-standards.md     # コーディング規約
│
├── contracts/                   # Solidityスマートコントラクト
│   ├── src/                    # コントラクトソース
│   ├── test/                   # コントラクトテスト
│   └── script/                 # デプロイスクリプト
│
├── python/                      # Pythonエージェント実装
│   ├── agents/                 # エージェント実装
│   │   ├── __init__.py
│   │   ├── base.py            # エージェント基底クラス
│   │   ├── demand_forecast.py # 需要予測エージェント
│   │   ├── inventory_optimizer.py # 在庫最適化エージェント
│   │   ├── price_optimizer.py # 価格設定（Phase 2）
│   │   ├── supplier_quality.py # 品質検証（Phase 3）
│   │   ├── validation.py      # 総合検証（Phase 3）
│   │   └── report_generator.py # レポート生成
│   │
│   ├── protocols/              # プロトコル実装
│   │   ├── x402_client.py     # X402クライアント
│   │   └── jpyc_payment.py    # JPYC決済
│   │
│   ├── utils/                  # ユーティリティ
│   │   ├── logging.py         # ロギング
│   │   └── cache.py           # キャッシュ
│   │
│   ├── api/                    # REST API
│   │   ├── main.py            # FastAPIメインアプリ
│   │   └── routes.py          # エンドポイント定義
│   │
│   ├── config.py               # 設定管理
│   ├── database.py             # データベース接続
│   └── orchestrator.py         # エージェント協調制御
│
├── db/                          # データベース
│   ├── schema.sql              # スキーマ定義
│   └── seed_data.sql           # テストデータ
│
├── tests/                       # テスト
│   ├── test_agents.py          # エージェントテスト
│   └── test_orchestrator.py    # Orchestratorテスト
│
├── docker-compose.yml           # Docker設定
├── requirements.txt             # Python依存関係
├── .env.example                # 環境変数テンプレート
└── .gitignore
```

---

## 🚀 クイックスタート（Claude Code向け）

### 最初のステップ

```bash
# 1. プロジェクトディレクトリに移動
cd a2a-supply-chain

# 2. 環境変数をコピー
cp .env.example .env

# 3. Python依存関係をインストール
pip install -r requirements.txt

# 4. Docker環境を起動（PostgreSQL, Redis, Anvil）
docker-compose up -d

# 5. データベースを初期化（自動実行されるが、手動の場合）
# psql -U postgres -d a2a_supply_chain -f db/schema.sql
# psql -U postgres -d a2a_supply_chain -f db/seed_data.sql

# 6. テストを実行
python test_agents.py
```

### 実装の進め方

1. **Phase 1実装計画を確認**
   - `docs/phase1-implementation-plan.md` を読む
   - 現在のタスク状況を確認

2. **実装ガイドに従う**
   - `docs/implementation-guide.md` の手順に従って実装
   - コーディング規約 `docs/coding-standards.md` を遵守

3. **テストファースト開発**
   - 実装前にテストケースを作成
   - 実装後にテストを実行して検証

4. **ドキュメントを更新**
   - 実装内容に応じてドキュメントを更新
   - 特に phase1-implementation-plan.md のチェックリストを更新

---

## 🔧 技術スタック

### Phase 1で使用する技術

| カテゴリ | 技術 | 用途 |
|---------|------|------|
| **言語** | Python 3.11+ | エージェント実装 |
| **Web Framework** | FastAPI | REST API |
| **Database** | PostgreSQL 15+ | トランザクショナルデータ |
| **Cache** | Redis 7+ | キャッシュ・セッション |
| **Blockchain** | Anvil（Foundry） | ローカルブロックチェーン |
| **ML** | scikit-learn, numpy | 機械学習モデル |
| **Optimization** | scipy | 在庫最適化 |

### Phase 2以降で追加する技術

| カテゴリ | 技術 | 用途 |
|---------|------|------|
| **Smart Contract** | Solidity 0.8.20+ | ERC-8004実装 |
| **ML** | LightGBM | 需要予測精度向上 |
| **Payment** | X402 v2 SDK | マイクロペイメント |
| **DID/VC** | 既存コンソーシアム | サプライヤー認証 |

---

## 📊 Phase 1 実装状況（2025-01-23時点）

### ✅ 完了済み

#### 環境構築
- [x] プロジェクト構造作成
- [x] Docker Compose設定
- [x] Python依存関係定義
- [x] データベーススキーマ（簡易版）
- [x] テストデータ生成

#### エージェント実装
- [x] エージェント基底クラス（`Agent`）
- [x] 需要予測エージェント（`DemandForecastAgent`）
  - 7日移動平均予測
  - 信頼区間算出
  - X402 upto方式設定
- [x] 在庫最適化エージェント（`InventoryOptimizerAgent`）
  - ニュースベンダーモデル
  - サプライヤー選定
  - X402 exact方式設定
- [x] Orchestrator（エージェント協調制御）

#### テスト
- [x] モックデータベースセッション
- [x] エージェント単体テスト
- [x] 統合テスト

**テスト結果**: すべて成功（実行時間0.003秒、コスト18 JPYC）

### 🔄 次のタスク（優先順）

#### 1. レポート生成エージェント実装
- [ ] `python/agents/report_generator.py` 作成
- [ ] 最適化結果のフォーマット
- [ ] コンソール出力 + JSONファイル出力

#### 2. PostgreSQL/Redis統合
- [ ] 実際のデータベース接続テスト
- [ ] Redisキャッシュ実装
- [ ] トランザクション管理

#### 3. FastAPI REST API実装
- [ ] `python/api/main.py` 作成
- [ ] エンドポイント実装
- [ ] 認証機能（JWT）

#### 4. X402決済フロー（モック実装）
- [ ] `python/protocols/x402_client.py` 作成
- [ ] 決済フローのモック実装
- [ ] ログ記録

詳細は `docs/phase1-implementation-plan.md` を参照。

---

## 🎓 重要な設計パターン

### 1. エージェント基底クラスパターン

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, name: str, payment_config: PaymentConfig):
        self.name = name
        self.payment_config = payment_config
    
    @abstractmethod
    async def execute(self, input_data: Dict) -> AgentResult:
        """エージェントのメイン処理"""
        pass
    
    def calculate_cost(self, usage_metrics: Dict) -> int:
        """コスト計算（決済スキームに応じて）"""
        pass
```

### 2. Orchestratorパターン

```python
class AgentCoordinator:
    async def execute_optimization_task(
        self, product_sku: str, store_id: str
    ) -> OptimizationResult:
        # Phase 1: 並列実行
        demand_result = await self.demand_forecast_agent.execute(...)
        
        # Phase 2: 依存関係のある順次実行
        inventory_result = await self.inventory_optimizer_agent.execute({
            "demand_forecast": demand_result,
            ...
        })
        
        return result
```

### 3. X402決済スキーム

```python
class PaymentScheme(Enum):
    EXACT = "exact"      # 固定料金（在庫最適化: 15 JPYC）
    UPTO = "upto"        # 従量課金（需要予測: 3 + 0.02/1000レコード）
    DEFERRED = "deferred"  # 後払い（レポート生成: 5 JPYC）
```

---

## ⚠️ 実装時の注意事項

### セキュリティ
- 環境変数（.env）に秘密鍵を保存、Gitにコミットしない
- APIエンドポイントには認証を実装（Phase 2）
- データベース接続は必ずコネクションプールを使用

### パフォーマンス
- データベースクエリは必ずインデックスを活用
- キャッシュは適切なTTLを設定（需要予測: 24h、サプライヤー品質: 7日）
- エージェント実行は並列化可能な部分は並列実行

### エラーハンドリング
- すべての外部API呼び出しはtry-exceptで囲む
- エラー時は適切なログ出力とユーザーフィードバック
- リトライロジックを実装（特にブロックチェーン操作）

### テスト
- ユニットテストのカバレッジ目標: 80%以上
- 統合テストは必須（エージェント間通信）
- モックを活用して外部依存を排除

---

## 📈 進捗管理

### タスク管理
- `docs/phase1-implementation-plan.md` のチェックリストを更新
- 完了したタスクは `[x]` にマーク
- ブロッカーがあればドキュメントに記録

### コード品質
```bash
# コードフォーマット
black python/
isort python/

# 型チェック
mypy python/

# テスト実行
pytest tests/ -v --cov
```

### Gitコミット規約
```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
test: テスト追加・修正
refactor: リファクタリング
```

---

## 🆘 トラブルシューティング

### Docker Composeが起動しない
```bash
# コンテナの状態確認
docker-compose ps

# ログ確認
docker-compose logs postgres

# 再起動
docker-compose down && docker-compose up -d
```

### データベース接続エラー
```bash
# PostgreSQL接続確認
psql -U postgres -h localhost -p 5432 -d a2a_supply_chain

# スキーマ確認
\dt
```

### Pythonパッケージのインストールエラー
```bash
# 仮想環境を使用
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📞 サポート

### ドキュメント不明点
- 該当するドキュメント（system-specification.mdなど）を再確認
- 不明点があればドキュメントに追記

### 実装方針の相談
- `docs/tech-decisions.md` に技術選定理由を記録
- アーキテクチャ変更が必要な場合はドキュメントを更新

---

## 🎯 最終ゴール（Phase 1）

Phase 1完了時点で以下が動作していること:

1. ✅ 2つのエージェント（需要予測・在庫最適化）が正常動作
2. ⏳ レポート生成エージェントが動作
3. ⏳ REST APIで最適化タスクを実行可能
4. ⏳ PostgreSQL/Redisに実際に接続して動作
5. ⏳ 基本的なエラーハンドリングとログ出力
6. ⏳ X402決済フローのモック実装

完了基準:
- 実行時間: < 60秒
- コスト: ≤ 55 JPYC（Phase 1は18 JPYC）
- テスト成功率: 100%
- API レスポンスタイム: < 1秒

---

**このドキュメントの更新**: 実装の進捗に応じて適宜更新してください。

**最終更新**: 2025-01-23  
**次回更新予定**: レポート生成実装後