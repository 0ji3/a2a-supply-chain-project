# テストと動作理解ガイド

**作成日**: 2026-01-29
**対象**: Phase 3実装の動作確認とシステム理解

---

## 🎯 このガイドの目的

Phase 3で実装した以下のコンポーネントの動作を理解し、テストを通じて挙動を確認する：

1. **X402 v2決済プロトコル** - Agent-to-Agentマイクロペイメント
2. **LLMエージェント** - CrewAI + Ollama統合
3. **SupplyChainOrchestrator** - エージェント協調と決済の統合

---

## 📁 実装済みコンポーネント一覧

### 1. X402 v2 決済プロトコル

**場所**: `python/protocols/x402/`

**主要ファイル**:
- `models.py`: データモデル定義
- `client.py`: X402Client実装

**テストファイル**:
- `python/test_x402.py`: プロトコル単体テスト
- `python/test_agents_with_x402.py`: エージェント統合テスト

### 2. LLMエージェント

**場所**: `python/agents/`

**主要ファイル**:
- `agents/tools/database_tool.py`: 販売履歴・サプライヤー情報取得
- `agents/tools/optimization_tool.py`: ニュースベンダーモデル
- `agents/tools/blockchain_tool.py`: 評価取得・フィードバック（モック）
- `agents/llm/demand_forecast_llm.py`: 需要予測エージェント
- `agents/llm/inventory_optimizer_llm.py`: 在庫最適化エージェント
- `agents/llm/report_generator_llm.py`: レポート生成エージェント

**テストファイル**:
- `python/test_llm_agents.py`: LLMエージェント統合テスト

### 3. Orchestrator

**場所**: `python/orchestrator_llm.py`

**テストファイル**:
- `python/test_orchestrator.py`: Orchestrator統合テスト

---

## 🧪 テスト実行ガイド

### テスト1: X402プロトコルテスト（推奨：最初に実行）

**目的**: X402決済プロトコルの3つのスキーム（EXACT, UPTO, DEFERRED）を理解する

**実行方法**:
```bash
cd python
python test_x402.py
```

**期待される出力**:
- 5つのテストケースがすべて成功
- 各決済スキームの動作が確認できる
- 総コスト: 23.04 JPYC

**理解ポイント**:
1. **EXACTスキーム**: 固定料金（15 JPYC）
   - 在庫最適化サービスで使用
   - `actual_amount = base_amount`

2. **UPTOスキーム**: 従量課金（3 JPYC + 0.02/1000レコード、上限10 JPYC）
   - 需要予測サービスで使用
   - `actual_amount = base_amount + usage_fee`
   - 上限チェック機能

3. **DEFERREDスキーム**: 後払い（5 JPYC）
   - レポート生成サービスで使用
   - サービス完了後に決済

**確認すべき出力**:
```
✅ ALL X402 TESTS PASSED!
  ✓ EXACT payment scheme (fixed fee)
  ✓ UPTO payment scheme (usage-based with cap)
  ✓ UPTO max amount validation
  ✓ DEFERRED payment scheme (post-payment)
  ✓ Transaction tracking and summary
```

---

### テスト2: エージェント + X402統合テスト

**目的**: エージェント実行と決済フローの統合を理解する

**実行方法**:
```bash
cd python
python test_agents_with_x402.py
```

**期待される出力**:
- 3フェーズ（需要予測 → 在庫最適化 → レポート生成）が順次実行
- 各フェーズで決済が実行される
- 総コスト: 23.04 JPYC

**理解ポイント**:
1. **AgentWithPaymentクラス**:
   - エージェント実行と決済を統合
   - `execute()`: タスク実行（Phase 3ではモック）
   - `calculate_actual_cost()`: 使用量に基づくコスト計算

2. **決済フロー**:
   ```
   X402Request作成
      ↓
   エージェント実行
      ↓
   コスト計算
      ↓
   X402Response作成
      ↓
   決済実行（X402Client.process_response）
      ↓
   トランザクション記録
   ```

**確認すべき出力**:
```
✅ 統合テスト成功！
🎯 Phase 3 Step 4完了:
   ✓ エージェント実行フロー
   ✓ X402決済統合
   ✓ 3つの決済スキーム（EXACT, UPTO, DEFERRED）
   ✓ トランザクション追跡
```

---

### テスト3: Orchestratorテスト（推奨：理解を深める）

**目的**: SupplyChainOrchestratorの協調フローを理解する

**実行方法**:
```bash
cd python
python test_orchestrator.py
```

**期待される出力**:
- 2つのテストケースが成功
- 1商品および複数商品の最適化フローが動作
- エージェント協調と決済の統合が確認できる

**理解ポイント**:
1. **SupplyChainOrchestratorクラス**:
   - エージェント設定管理（AgentConfig）
   - 3フェーズの協調実行
   - X402決済統合
   - 結果集計とサマリー表示

2. **実行モード**:
   - `use_real_llm=False`: モックモード（デフォルト、高速）
   - `use_real_llm=True`: 実LLMモード（CrewAI + Ollama必要）

3. **フェーズ実行順序**:
   ```
   Phase 1: 需要予測
      ↓（予測需要を渡す）
   Phase 2: 在庫最適化
      ↓（最適化結果を渡す）
   Phase 3: レポート生成
   ```

**確認すべき出力**:
```
🎉 すべてのテストに合格しました！

📊 テスト結果サマリー
Total: 2
Passed: 2
Failed: 0

🎯 Phase 3 Step 5完了:
   ✓ SupplyChainOrchestrator実装
   ✓ エージェント協調フロー
   ✓ X402決済統合
   ✓ モック実行テスト
```

---

### テスト4: 実LLMテスト（オプショナル、時間がかかる）

**目的**: 実際のLLM（CrewAI + Ollama）でエージェントを動作させる

**前提条件**:
- Dockerコンテナが起動している
- Ollamaサービスが利用可能
- mistral:7bモデルがダウンロード済み

**実行方法**:
```bash
# Docker環境で実行
docker compose run app python test_llm_agents.py
```

**⚠️ 注意**:
- 実行に10分以上かかる可能性がある
- タイムアウト（600秒）する可能性がある
- 現在、既知の問題としてタイムアウトが発生

**既知の問題**:
```
litellm.APIConnectionError: OllamaException - litellm.Timeout:
Connection timed out after 600.0 seconds.
```

**対策案**:
1. より軽量なモデルを試す（後日）
2. タスクプロンプトを簡素化（後日）
3. タイムアウト時間を延長（後日）

**このテストは後回しで問題ありません。**

---

## 🔍 コード理解のポイント

### 1. X402決済スキームの使い分け

```python
# EXACT: 固定料金（在庫最適化）
PaymentScheme.EXACT
base_amount_jpyc = 15.0
# → 常に15 JPYCの請求

# UPTO: 従量課金（需要予測）
PaymentScheme.UPTO
base_amount_jpyc = 3.0
max_amount_jpyc = 10.0
# → 3 JPYC + 使用量課金、上限10 JPYC

# DEFERRED: 後払い（レポート生成）
PaymentScheme.DEFERRED
base_amount_jpyc = 5.0
# → サービス完了後に5 JPYC請求
```

### 2. Wei/JPYC変換

```python
from protocols.x402.models import jpyc_to_wei, wei_to_jpyc

# JPYC → wei（ブロックチェーン単位）
jpyc_to_wei(3.04)  # → 3040000000000000000

# wei → JPYC（人間が読める単位）
wei_to_jpyc(3040000000000000000)  # → 3.04

# 1 JPYC = 10^18 wei (ERC-20標準)
```

### 3. エージェント協調フロー

```python
# 1. Orchestrator初期化
orchestrator = SupplyChainOrchestrator(client_agent_id=0)

# 2. 最適化実行
results = orchestrator.execute_optimization(
    product_sku="TOMATO-001",
    product_name="トマト",
    store_name="渋谷店",
    weather="晴れ",
    day_type="週末",
    selling_price=200.0,
    use_real_llm=False  # モックモード
)

# 3. 結果取得
results["demand_forecast"]         # 需要予測結果
results["inventory_optimization"]  # 在庫最適化結果
results["report"]                  # レポート
results["total_cost_jpyc"]         # 総コスト
results["transactions"]            # トランザクション一覧
```

### 4. X402トランザクション追跡

```python
# X402Client経由で決済を実行
client = X402Client(client_agent_id=0)

# リクエスト作成
request = client.create_request(...)

# レスポンス処理（決済実行）
transaction = client.process_response(request, response)

# トランザクション情報
transaction.transaction_id  # トランザクションID
transaction.amount         # 支払額（wei）
transaction.status         # 決済ステータス
transaction.tx_hash        # トランザクションハッシュ（Phase 3ではモック）

# サマリー取得
summary = client.get_transaction_summary()
summary["total_transactions"]  # 総トランザクション数
summary["total_spent_jpyc"]   # 総支払額
summary["by_scheme"]          # スキーム別集計
```

---

## 📊 動作確認チェックリスト

明日のテスト・理解活動で確認すべき項目：

### X402プロトコル理解
- [ ] EXACTスキーム（固定料金）の動作を理解
- [ ] UPTOスキーム（従量課金）の動作を理解
- [ ] UPTOの上限チェック機能を確認
- [ ] DEFERREDスキーム（後払い）の動作を理解
- [ ] Wei/JPYC変換の仕組みを理解
- [ ] トランザクション追跡機能を確認

### エージェント統合理解
- [ ] AgentWithPaymentクラスの役割を理解
- [ ] エージェント実行フローを確認
- [ ] コスト計算ロジックを理解（使用量ベース）
- [ ] 3フェーズの協調フローを確認

### Orchestrator理解
- [ ] AgentConfigの設定内容を確認
- [ ] execute_optimization()の処理フローを理解
- [ ] 各フェーズの実行順序を確認
- [ ] X402決済統合の仕組みを理解
- [ ] モックモードと実LLMモードの違いを理解
- [ ] 結果集計とサマリー表示を確認

### コード探索
- [ ] protocols/x402/models.py を読む
- [ ] protocols/x402/client.py を読む
- [ ] orchestrator_llm.py を読む
- [ ] test_orchestrator.py を読む

### 疑問点のリストアップ
- [ ] 理解できなかった部分をメモ
- [ ] 改善したい部分をメモ
- [ ] 次に実装すべき機能を検討

---

## 🛠️ トラブルシューティング

### テスト実行でエラーが出る

**症状**: `ModuleNotFoundError`
```
ModuleNotFoundError: No module named 'protocols'
```

**解決策**:
```bash
# 必ずpythonディレクトリから実行
cd /Users/ogawaranaoki/Sample/a2a-supply-chain-project/python
python test_x402.py
```

---

### Docker環境でテストしたい

**基本的なDockerコマンド**:
```bash
# コンテナ起動
docker compose up -d

# コンテナ状態確認
docker compose ps

# アプリコンテナでコマンド実行
docker compose run app python test_x402.py

# ログ確認
docker compose logs app

# コンテナ停止
docker compose down
```

---

### Ollamaの状態確認

**Ollamaサービス確認**:
```bash
# Ollamaコンテナの状態確認
docker compose ps a2a-ollama

# Ollamaログ確認
docker compose logs a2a-ollama

# Ollamaに直接アクセス
curl http://localhost:11434/api/tags
```

---

## 📝 理解を深めるための質問リスト

### X402プロトコル
1. なぜ3つの決済スキームが必要なのか？
2. UPTOスキームで上限が必要な理由は？
3. Wei/JPYC変換で10^18を使う理由は？
4. Phase 3（モック）とPhase 4（実決済）の違いは？

### エージェント協調
1. なぜ需要予測 → 在庫最適化 → レポート生成の順序なのか？
2. 各エージェントが使用するツールの役割は？
3. ニュースベンダーモデルとは何か？
4. 従量課金のコスト計算方法は？

### システム設計
1. なぜOrchestratorパターンを使うのか？
2. モックモードと実LLMモードを分けた理由は？
3. エージェント設定（AgentConfig）の役割は？
4. トランザクション追跡が重要な理由は？

### 実装の詳細
1. X402Requestにはどんな情報が含まれるか？
2. X402Responseで返される情報は？
3. X402Transactionで記録される情報は？
4. エージェント実行結果はどのように次のフェーズに渡されるか？

---

## 🎯 明日の推奨スケジュール

### 午前（2-3時間）: テスト実行と基本理解
1. テスト1: X402プロトコルテスト（30分）
   - test_x402.pyを実行
   - 出力を見ながら各スキームの動作を理解

2. テスト2: エージェント + X402統合テスト（30分）
   - test_agents_with_x402.pyを実行
   - 3フェーズの協調フローを確認

3. テスト3: Orchestratorテスト（30分）
   - test_orchestrator.pyを実行
   - 複数商品の最適化フローを確認

4. 休憩（15分）

5. コード探索（1時間）
   - protocols/x402/models.py を読む
   - protocols/x402/client.py を読む
   - わからない部分をメモ

### 午後（2-3時間）: 詳細理解と実験
1. orchestrator_llm.py の詳細理解（1時間）
   - AgentConfigの設定を確認
   - execute_optimization()の処理フローを追跡
   - 各フェーズのメソッドを確認

2. 実験: パラメータを変えてテスト（1時間）
   - 商品を変えて実行（レタス、キャベツ等）
   - 天気・曜日タイプを変えて実行
   - 価格を変えて実行
   - 結果の違いを観察（現在はモックなので同じ結果が返る）

3. 疑問点の整理とメモ（30分）
   - 理解できなかった部分をリストアップ
   - 改善案を検討
   - 次に実装したい機能を考える

---

## 📚 参考リソース

### プロジェクトドキュメント
- `docs/phase3-progress.md`: Phase 3実装進捗
- `docs/README.md`: プロジェクト概要
- `docs/system-specification.md`: システム仕様

### 外部ドキュメント
- [X402 v2 Specification](https://github.com/a2a-protocol/x402)
- [ERC-8004: Autonomous Agent Registry](https://eips.ethereum.org/EIPS/eip-8004)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### ツール・フレームワーク
- [Ollama Models](https://ollama.ai/library)
- [LiteLLM](https://docs.litellm.ai/)

---

**このガイドを使って、明日は実装の動作を理解し、システム全体の挙動を把握しましょう！**

**最終更新**: 2026-01-29
