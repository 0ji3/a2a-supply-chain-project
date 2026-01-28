# Phase 3 実装計画：LLMエージェント実装

**作成日**: 2026-01-28
**ステータス**: 計画中
**前提**: Phase 2（ブロックチェーン基盤）完了

---

## 📋 目標

Phase 3では、**実際のLLMを使用した自律エージェント**を実装し、エージェント間通信とX402決済フローを実現します。

### 成功基準

1. ✅ 最低2つのLLMベースエージェントが動作
2. ✅ エージェント同士がメッセージをやり取り
3. ✅ X402 v2プロトコルで決済フロー実装
4. ✅ JPYC（テストネット）で実際に決済実行
5. ✅ ブロックチェーン上にトランザクション記録

---

## 🛠️ 技術スタック

### フレームワーク: CrewAI

**選定理由**:
- マルチエージェント協調に特化した設計
- エージェント間のタスク委譲が容易
- Role-based agent design（役割ベース設計）
- 今回のユースケース（Supply Chain最適化）に最適

**主要機能**:
- Agent（エージェント定義）
- Task（タスク定義）
- Crew（エージェントチーム編成）
- Tools（エージェントが使用できるツール）

### LLMプロバイダー

#### Phase 3-A: Ollama（ローカルLLM）【優先】

**選定理由**:
- 完全にローカルで動作（APIキー不要）
- コスト0
- プライバシー確保
- デモアプリとして理想的

**推奨モデル**:
- `mistral:7b` - バランスの良い性能
- `llama3.1:8b` - Meta製、高性能
- `qwen2.5:7b` - 日本語対応良好

**技術的要件**:
- Docker内でOllamaを実行
- メモリ: 8GB以上推奨
- ストレージ: モデルサイズ（4-5GB）

#### Phase 3-B: LangChain + Claude API【フォールバック】

**使用条件**:
- Ollamaのパフォーマンスが不十分
- メモリ/ストレージの制約がある場合
- レスポンス品質を優先する場合

---

## 🏗️ アーキテクチャ設計

### システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│                   (FastAPI REST API)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CrewAI Orchestrator                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Demand Agent │  │ Inventory    │  │ Report Agent │      │
│  │              │──│ Agent        │──│              │      │
│  │ (LLM-based)  │  │ (LLM-based)  │  │ (LLM-based)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         │   X402 Payment Protocol           │              │
│         └─────────────────┼─────────────────┘              │
└───────────────────────────┼────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Blockchain Layer (Anvil)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ERC8004      │  │ ERC8004      │  │ MockJPYC     │      │
│  │ Identity     │  │ Reputation   │  │ (ERC-20)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Ollama LLM Server                        │
│              (mistral:7b / llama3.1:8b)                     │
└─────────────────────────────────────────────────────────────┘
```

### エージェント設計

#### 1. Demand Forecast Agent（需要予測エージェント）

**役割**: 過去のデータから需要を予測

**LLM使用箇所**:
- 季節性パターンの分析
- 外部要因（天候、イベント）の考慮
- 予測結果の説明文生成

**ツール**:
- Database Query Tool（過去データ取得）
- Statistical Analysis Tool（統計分析）
- Weather API Tool（天候情報取得）

**入力**: 商品SKU, 店舗ID, 期間
**出力**: 予測需要量、信頼区間、説明文

#### 2. Inventory Optimizer Agent（在庫最適化エージェント）

**役割**: 需要予測を基に最適な発注量を計算

**LLM使用箇所**:
- サプライヤー選定の意思決定
- 在庫戦略の提案
- 最適化ロジックの説明

**ツール**:
- Optimization Tool（最適化計算）
- Supplier Database Tool（サプライヤー情報取得）
- Blockchain Tool（コントラクト呼び出し）

**入力**: 需要予測結果
**出力**: 推奨発注量、サプライヤー、コスト

#### 3. Report Generator Agent（レポート生成エージェント）

**役割**: 最適化結果を分かりやすくレポート化

**LLM使用箇所**:
- 日本語レポート生成
- 改善提案の生成
- エグゼクティブサマリー作成

**ツール**:
- Markdown Generator Tool
- Chart Generator Tool
- PDF Export Tool（Phase 4）

**入力**: 需要予測結果、在庫最適化結果
**出力**: マークダウンレポート、サマリー

---

## 💰 X402 v2決済フロー設計

### 決済スキーム

| エージェント | 決済方式 | 料金 | タイミング |
|------------|---------|------|----------|
| Demand Forecast | `upto` | 3 JPYC + 0.02/1000レコード | タスク完了後 |
| Inventory Optimizer | `exact` | 15 JPYC | タスク完了後 |
| Report Generator | `deferred` | 5 JPYC | レポート確認後 |

### X402実装手順

1. **クライアント（Orchestrator）**:
   - エージェントにタスクを依頼
   - X402リクエストを送信（決済情報含む）

2. **エージェント**:
   - タスクを実行
   - 実行コストを計算
   - X402レスポンスを返す（決済要求）

3. **決済実行**:
   - JPYCトークンを転送（ERC-20 transfer）
   - ブロックチェーンにトランザクション記録
   - ERC8004 Reputationにフィードバック送信

### 実装クラス設計

```python
class X402Payment:
    """X402決済プロトコル実装"""

    def __init__(self, blockchain_service: BlockchainService):
        self.blockchain = blockchain_service

    async def request_service(
        self,
        agent_id: int,
        task: str,
        payment_scheme: PaymentScheme,
        max_amount: int
    ) -> X402Request:
        """サービスリクエスト（X402）"""
        pass

    async def execute_payment(
        self,
        agent_id: int,
        amount: int,
        task_result: dict
    ) -> str:
        """決済実行（JPYC転送）"""
        # JPYCトークンを転送
        tx_hash = self.blockchain.transfer_jpyc(
            to_address=agent_wallet,
            amount=amount
        )

        # フィードバック送信
        self.blockchain.submit_feedback(
            agent_id=agent_id,
            score=calculate_score(task_result),
            tags=["accurate", "fast"],
            report_uri=f"ipfs://{task_result['report_hash']}"
        )

        return tx_hash
```

---

## 📁 ディレクトリ構成（Phase 3追加分）

```
python/
├── agents/
│   ├── llm/                    # 新規: LLMエージェント
│   │   ├── __init__.py
│   │   ├── demand_forecast_llm.py   # LLM版 需要予測
│   │   ├── inventory_optimizer_llm.py # LLM版 在庫最適化
│   │   └── report_generator_llm.py  # LLM版 レポート生成
│   └── tools/                  # 新規: エージェントツール
│       ├── __init__.py
│       ├── database_tool.py   # DB検索ツール
│       ├── optimization_tool.py # 最適化計算ツール
│       └── blockchain_tool.py # ブロックチェーンツール
│
├── protocols/
│   ├── x402/                   # 新規: X402実装
│   │   ├── __init__.py
│   │   ├── client.py          # X402クライアント
│   │   ├── server.py          # X402サーバー
│   │   └── models.py          # X402データモデル
│   └── jpyc_payment.py        # JPYC決済（Phase 2から移動）
│
├── crewai_orchestrator.py     # 新規: CrewAI Orchestrator
└── test_llm_agents.py          # 新規: LLMエージェントテスト
```

---

## 🚀 実装手順

### Step 1: Ollama環境構築（1-2時間）

1. docker-compose.ymlにOllamaサービスを追加
2. Ollamaコンテナを起動
3. 推奨モデルをダウンロード（mistral:7b）
4. 接続テストスクリプト作成

```yaml
# docker-compose.yml
ollama:
  image: ollama/ollama:latest
  container_name: a2a-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
  networks:
    - a2a-network
```

### Step 2: CrewAI + Ollama統合（2-3時間）

1. CrewAI, langchain-ollama をインストール
2. シンプルなエージェント1つで動作確認
3. Ollama接続設定
4. レスポンス品質テスト

### Step 3: LLMエージェント実装（4-6時間）

1. Demand Forecast Agent（LLM版）
2. Inventory Optimizer Agent（LLM版）
3. Report Generator Agent（LLM版）
4. エージェント間通信テスト

### Step 4: X402決済フロー実装（3-4時間）

1. X402プロトコルクラス実装
2. JPYC決済統合
3. ブロックチェーントランザクション記録
4. ERC8004フィードバック送信

### Step 5: CrewAI Orchestrator実装（2-3時間）

1. エージェントチーム編成
2. タスクフロー定義
3. 決済フロー統合
4. エラーハンドリング

### Step 6: 統合テスト（2-3時間）

1. エンドツーエンドテスト
2. 決済フローテスト
3. ブロックチェーン記録確認
4. パフォーマンステスト

---

## 📊 期待される成果物

### デモシナリオ

1. ユーザーがREST APIで最適化リクエスト送信
2. Demand Forecast Agentが需要予測を実行（LLM使用）
3. Inventory Optimizer Agentが在庫最適化を実行（LLM使用）
4. Report Generator Agentがレポート生成（LLM使用）
5. 各エージェントにX402でJPYC決済実行
6. ブロックチェーンにトランザクション記録
7. 総合レポートを返す

### 実行結果イメージ

```
============================================================
A2A Supply Chain Optimization - LLM Demo
============================================================

1. Demand Forecast Agent (LLM)
   予測需要量: 305個
   信頼区間: [285, 325]
   説明: 先週の販売データと天候予報を分析しました。
         週末に晴天が予想されるため、通常より5%増の需要を見込みます。
   コスト: 3.04 JPYC (X402 upto)
   決済Tx: 0xabcd1234...
   ブロックチェーン記録: ✓

2. Inventory Optimizer Agent (LLM)
   推奨発注量: 301個
   推奨サプライヤー: 静岡農協
   説明: 需要予測を基に、廃棄ロスを最小化する発注量を計算しました。
         静岡農協は品質が高く、リードタイムも短いため選定しました。
   コスト: 15 JPYC (X402 exact)
   決済Tx: 0xdef5678...
   ブロックチェーン記録: ✓

3. Report Generator Agent (LLM)
   レポート: optimization_report_20260128.md
   エグゼクティブサマリー:
     - 予測需要: 305個
     - 推奨発注: 301個
     - 期待コスト削減: ¥12,500/週
     - 廃棄ロス削減: 8個 → 0個
   コスト: 5 JPYC (X402 deferred)
   決済Tx: 0x9abc012...
   ブロックチェーン記録: ✓

============================================================
総コスト: 23.04 JPYC
実行時間: 45秒
ブロックチェーントランザクション: 3件
============================================================
```

---

## ⚠️ リスクとフォールバック

### リスク1: Ollamaのパフォーマンス不足

**症状**:
- レスポンスが遅い（> 30秒）
- 回答品質が低い
- メモリ不足エラー

**フォールバック**:
→ LangChain + Claude APIに切り替え

### リスク2: エージェント間通信の複雑性

**症状**:
- エージェント間でコンテキストが失われる
- タスク依存関係の管理が複雑

**フォールバック**:
→ シンプルな順次実行に変更

### リスク3: X402実装の複雑性

**症状**:
- プロトコル仕様の理解不足
- 決済フローのデバッグが困難

**フォールバック**:
→ 簡易版決済（単純なERC-20転送）に簡略化

---

## 🎯 Phase 3完了基準

- [ ] Ollamaが正常に動作（または Claude API統合）
- [ ] 3つのLLMエージェントが実装され動作
- [ ] エージェント間でメッセージをやり取り
- [ ] X402プロトコルで決済リクエスト/レスポンス
- [ ] JPYCで実際に決済実行
- [ ] ブロックチェーンにトランザクション記録
- [ ] ERC8004 Reputationにフィードバック送信
- [ ] デモシナリオの実行成功
- [ ] テストカバレッジ > 70%

---

## 📅 スケジュール（目安）

| フェーズ | 作業内容 | 所要時間 |
|---------|---------|---------|
| Step 1 | Ollama環境構築 | 1-2時間 |
| Step 2 | CrewAI + Ollama統合 | 2-3時間 |
| Step 3 | LLMエージェント実装 | 4-6時間 |
| Step 4 | X402決済フロー実装 | 3-4時間 |
| Step 5 | CrewAI Orchestrator実装 | 2-3時間 |
| Step 6 | 統合テスト | 2-3時間 |
| **合計** | | **14-21時間** |

---

## 📝 次回作業開始時のチェックリスト

- [ ] Phase 2の動作確認（Anvil, コントラクト）
- [ ] このドキュメントを再読
- [ ] Ollamaのインストール確認
- [ ] CrewAIのドキュメント確認
- [ ] X402 v2仕様の再確認

---

**作成者**: Claude Sonnet 4.5
**最終更新**: 2026-01-28
**次回更新予定**: Phase 3 Step 1完了後
