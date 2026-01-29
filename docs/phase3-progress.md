# Phase 3 実装進捗 - CrewAI + Ollama LLMエージェント

## 📅 実装日
2026-01-29

## 🎯 Phase 3 目標
LLMベースのエージェントシステムと、Agent-to-Agent (A2A) マイクロペイメントプロトコル（X402 v2）の実装

---

## ✅ 完了したステップ

### Step 1: Ollama環境セットアップ ✅
**完了日**: 2026-01-29

**実装内容**:
- Docker ComposeへOllamaサービス追加
- `mistral:7b` モデル（4.4GB）のダウンロード
- Ollama接続テスト実装（`test_ollama.py`）

**成果物**:
- `docker-compose.yml`: ollama サービス定義
- `python/test_ollama.py`: 接続テスト
- Ollamaコンテナ: `a2a-ollama` (port 11434)

**検証**:
```bash
✓ Ollama接続成功
✓ mistral:7bモデル動作確認
✓ レイテンシー: < 1秒（短いプロンプト）
```

---

### Step 2: CrewAI + Ollama統合 ✅
**完了日**: 2026-01-29

**実装内容**:
- CrewAI依存関係追加（crewai, langchain, langchain-ollama）
- LiteLLM統合（`ollama/mistral:7b`フォーマット）
- 2エージェント統合テスト実装

**成果物**:
- `requirements.txt`: CrewAI関連パッケージ追加
- `python/test_crewai.py`: CrewAI統合テスト

**トラブルシューティング**:
- ❌ 問題: aiohttp バージョン競合
  - ✅ 解決: `aiohttp>=3.11.0` へアップデート
- ❌ 問題: LiteLLM provider エラー
  - ✅ 解決: `model="ollama/mistral:7b"` フォーマット使用

**検証**:
```bash
✓ CrewAI + Ollama接続成功
✓ 2エージェント協調動作確認
✓ LLM推論正常動作
```

---

### Step 3: LLMエージェント実装 ✅
**完了日**: 2026-01-29

**実装内容**:
- エージェントツール実装（database, optimization, blockchain）
- 3つのLLMエージェント実装（需要予測、在庫最適化、レポート生成）
- 統合テスト実装（`test_llm_agents.py`）

**成果物**:
- `python/agents/tools/database_tool.py`
  - `get_sales_history`: 販売履歴取得
  - `get_supplier_info`: サプライヤー情報取得

- `python/agents/tools/optimization_tool.py`
  - `calculate_optimal_order_quantity`: ニュースベンダーモデル
  - カスタム逆正規分布CDF実装（scipy不要）

- `python/agents/tools/blockchain_tool.py`
  - `get_agent_reputation`: エージェント評価取得（モック）
  - `submit_agent_feedback`: フィードバック送信（モック）

- `python/agents/llm/demand_forecast_llm.py`
  - 需要予測エージェント
  - Tools: get_sales_history

- `python/agents/llm/inventory_optimizer_llm.py`
  - 在庫最適化エージェント
  - Tools: get_supplier_info, calculate_optimal_order_quantity

- `python/agents/llm/report_generator_llm.py`
  - レポート生成エージェント
  - Tools: なし（前エージェントの出力を統合）

- `python/test_llm_agents.py`: 3エージェント統合テスト

**既知の問題**:
- ⚠️ タイムアウト: LLM推論が600秒でタイムアウト
  - 原因: mistral:7bモデルの推論が遅い、またはタスクが複雑
  - 今後の対応: より軽量なモデル（qwen:7b等）の検討

---

### Step 4: X402 v2 決済プロトコル実装 ✅
**完了日**: 2026-01-29

**実装内容**:
- X402 v2プロトコルの完全実装
- 3つの決済スキーム（EXACT, UPTO, DEFERRED）
- エージェント実行と決済フローの統合

**成果物**:
- `python/protocols/x402/__init__.py`: モジュールエクスポート
- `python/protocols/x402/models.py`: データモデル
  - `PaymentScheme`: 決済スキーム列挙型
  - `X402Request`: リクエストモデル
  - `X402Response`: レスポンスモデル
  - `X402Transaction`: トランザクションモデル
  - `jpyc_to_wei()`, `wei_to_jpyc()`: 変換関数

- `python/protocols/x402/client.py`: X402クライアント
  - `X402Client`: 決済処理クラス
  - `create_request()`: リクエスト作成
  - `process_response()`: 決済実行（Phase 3はモック）
  - `get_transaction_summary()`: トランザクション集計

- `python/test_x402.py`: X402プロトコルテスト
  - Test 1: EXACT決済（固定料金）
  - Test 2: UPTO決済（従量課金）
  - Test 3: UPTO上限超過検証
  - Test 4: DEFERRED決済（後払い）
  - Test 5: トランザクション集計

- `python/test_agents_with_x402.py`: エージェント + X402統合テスト
  - `AgentWithPayment`: 決済統合エージェントラッパー
  - 3フェーズフロー実装（需要予測 → 在庫最適化 → レポート生成）
  - 各フェーズでX402決済実行

**決済スキーム詳細**:
| スキーム | 用途 | 料金体系 | 例 |
|---------|------|----------|-----|
| EXACT | 固定料金 | 基本料金のみ | 在庫最適化: 15 JPYC |
| UPTO | 従量課金 | 基本 + 使用量（上限あり） | 需要予測: 3 + 0.02/1000レコード（上限10 JPYC） |
| DEFERRED | 後払い | 事後確定 | レポート生成: 5 JPYC |

**検証結果**:
```bash
✅ ALL X402 TESTS PASSED!

📊 Summary:
  ✓ EXACT payment scheme (fixed fee)
  ✓ UPTO payment scheme (usage-based with cap)
  ✓ UPTO max amount validation
  ✓ DEFERRED payment scheme (post-payment)
  ✓ Transaction tracking and summary

統合テスト結果:
  Total Transactions: 3
  Total Spent: 23.04 JPYC
  内訳:
    - 需要予測 (UPTO): 3.04 JPYC
    - 在庫最適化 (EXACT): 15.00 JPYC
    - レポート生成 (DEFERRED): 5.00 JPYC
```

**Phase 3とPhase 4の違い**:
- **Phase 3（現在）**: モック決済実装
  - `tx_hash = f"0xmock_{transaction_id[:8]}"`
  - ブロックチェーンへのトランザクションなし
  - テストとプロトタイピング用

- **Phase 4（今後）**: 実際のブロックチェーン決済
  - JPYCトークンコントラクト連携
  - EIP-3009 `transferWithAuthorization`使用
  - Anvilローカルチェーンへの実トランザクション

---

### Step 5: Orchestrator実装 ✅
**完了日**: 2026-01-29

**実装内容**:
- SupplyChainOrchestratorクラスの実装
- LLMエージェントとX402決済の統合
- モック実行モードと実LLMモードのサポート
- エージェント設定管理とコスト計算

**成果物**:
- `python/orchestrator_llm.py`: SupplyChainOrchestrator
  - `AgentConfig`: エージェント設定（ID、決済スキーム、コスト）
  - `execute_optimization()`: 最適化フロー実行
    - Phase 1: 需要予測（UPTO: 3 + 0.02/1000レコード）
    - Phase 2: 在庫最適化（EXACT: 15 JPYC）
    - Phase 3: レポート生成（DEFERRED: 5 JPYC）
  - X402Client統合
  - モック実装（use_real_llm=False）
  - 実LLM対応（use_real_llm=True、CrewAI必須）
  - エラーハンドリングとログ出力
  - 結果集計とサマリー表示

- `python/test_orchestrator.py`: 統合テスト
  - test_orchestrator_mock(): 基本動作テスト
  - test_multiple_products(): 複数商品最適化テスト

**アーキテクチャ**:
```
1. X402Request作成（各エージェント用）
2. エージェントタスク実行（モックまたは実LLM）
3. 使用量メトリクスに基づくコスト計算
4. X402Response作成
5. X402Clientで決済処理
6. 結果集計とサマリー表示
```

**検証結果**:
```bash
✅ すべてのテストに合格 (2/2)

テスト1: 基本動作
  総コスト: 23.04 JPYC
  実行時間: < 1ms

テスト2: 複数商品（トマト + レタス）
  総トランザクション: 6
  総支払額: 46.08 JPYC
  スキーム別: EXACT 2件, UPTO 2件, DEFERRED 2件
```

**特徴**:
- CrewAI依存はオプショナル（モックモードでは不要）
- use_real_llm=Falseでテスト可能
- 実LLM使用時のみCrewAI必須
- 柔軟なエージェント設定
- 詳細な結果サマリー表示

---

## 🔄 次のステップ（Phase 3 残り）

### Step 6: 統合テスト（未着手）
**目標**: 実LLMを使ったEnd-to-Endテスト

**テスト項目**:
- [ ] 実LLM（CrewAI + Ollama）でのOrchestrator実行
- [ ] 3エージェント協調動作の検証
- [ ] X402決済フローの完全検証
- [ ] タイムアウト処理の確認
- [ ] エラーハンドリングの検証
- [ ] パフォーマンス測定（実行時間）

**アプローチ候補**:
1. **簡易版テスト（推奨）**:
   - より簡単なプロンプトで試す
   - タイムアウトを延長（1200秒）
   - 1エージェントずつテスト

2. **Docker環境で完全テスト**:
   - `docker compose run app python test_llm_agents.py`
   - 必要に応じてモデル変更（qwen:7b等）

3. **Orchestrator + 実LLM**:
   - test_orchestrator.pyに実LLMオプション追加
   - Docker環境で実行

---

## 📊 Phase 3 進捗サマリー

| ステップ | タスク | ステータス | 完了日 |
|---------|--------|----------|--------|
| 1 | Ollama環境セットアップ | ✅ 完了 | 2026-01-29 |
| 2 | CrewAI + Ollama統合 | ✅ 完了 | 2026-01-29 |
| 3 | LLMエージェント実装 | ✅ 完了 | 2026-01-29 |
| 4 | X402決済プロトコル実装 | ✅ 完了 | 2026-01-29 |
| 5 | Orchestrator実装 | ✅ 完了 | 2026-01-29 |
| 6 | 統合テスト（実LLM） | ⏳ 未着手 | - |

**進捗率**: 83% (5/6 ステップ完了)

---

## 🐛 既知の問題と対策

### 1. LLM推論タイムアウト（優先度: 高）
**症状**:
```
litellm.APIConnectionError: OllamaException - litellm.Timeout:
Connection timed out after 600.0 seconds.
```

**原因**:
- mistral:7bモデルの推論速度が遅い
- タスクプロンプトが複雑すぎる可能性

**対策案**:
1. より軽量なモデルを試す（qwen:7b, phi3:mini等）
2. タスクプロンプトを簡素化
3. タイムアウト時間を延長（1200秒等）
4. GPU対応Ollamaコンテナ使用（nvidia-docker）

### 2. Dependency競合（解決済み）
**症状**: aiohttp, pydantic バージョン競合

**解決策**:
- `aiohttp>=3.11.0`
- `pydantic>=2.7.4,<3.0.0`

---

## 🎯 Phase 4 準備状況

### Phase 4で必要な実装

#### 4.1 ブロックチェーン統合
- [ ] JPYC トークンコントラクト連携
- [ ] EIP-3009 `transferWithAuthorization` 実装
- [ ] Web3.py統合
- [ ] Anvil testnet接続確認

#### 4.2 ERC-8004統合
- [ ] Identity Registry連携
- [ ] Reputation Registry連携
- [ ] Validation Registry連携

#### 4.3 X402実決済
- [ ] `X402Client._execute_blockchain_payment()` 実装
- [ ] ガス代見積もり
- [ ] トランザクション確認待機
- [ ] エラーリトライロジック

---

## 📝 技術的メモ

### X402決済フロー
```
1. クライアント: create_request()
   → X402Request生成

2. サービス: エージェント実行
   → タスク実行 + 使用量メトリクス取得

3. サービス: X402Response作成
   → actual_amount計算（使用量ベース）

4. クライアント: process_response()
   → 決済額検証（UPTOの場合、max_amount超過チェック）
   → 決済実行（Phase 3: モック / Phase 4: 実決済）
   → X402Transaction生成
```

### Wei/JPYC変換
```python
1 JPYC = 10^18 wei (ERC-20標準)

jpyc_to_wei(3.04) = 3040000000000000000
wei_to_jpyc(3040000000000000000) = 3.04
```

### ニュースベンダーモデル（在庫最適化）
```python
critical_ratio = (selling_price - unit_cost) /
                 (selling_price - unit_cost + shortage_cost + disposal_cost)

z_score = inverse_normal_cdf(critical_ratio)
optimal_quantity = demand_mean + z_score * demand_std
```

---

## 🔗 関連ドキュメント

- [X402 v2 Specification](https://github.com/a2a-protocol/x402)
- [ERC-8004: Autonomous Agent Registry](https://eips.ethereum.org/EIPS/eip-8004)
- [JPYC Documentation](https://docs.jpyc.jp/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Ollama Model Library](https://ollama.ai/library)

---

**最終更新**: 2026-01-29 (Step 5完了)
**次回更新予定**: Step 6 統合テスト実施後
