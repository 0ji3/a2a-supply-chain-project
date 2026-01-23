# シーケンス図 - 生鮮品サプライチェーン最適化AI協調システム

## ドキュメント情報

- **プロジェクト名**: 生鮮品サプライチェーン最適化AI協調システム
- **ドキュメントタイプ**: シーケンス図
- **バージョン**: 1.0.0
- **最終更新**: 2025-01-22

---

## 目次

1. [全体フロー（6エージェント協調）](#1-全体フロー6エージェント協調)
2. [X402決済フロー](#2-x402決済フロー)
3. [DID/VC検証フロー](#3-didvc検証フロー)
4. [ERC-8004記録フロー](#4-erc-8004記録フロー)
5. [エージェント実行詳細フロー](#5-エージェント実行詳細フロー)

---

## 1. 全体フロー（6エージェント協調）

### 1.1 概要

毎日深夜2時に実行される最適化タスクの全体フロー。6つのエージェントが協調して需要予測・在庫最適化・価格設定・品質検証を行い、最終的な意思決定サマリーを生成する。

### 1.2 シーケンス図

```mermaid
sequenceDiagram
    autonumber
    participant User as バイヤー
    participant Orch as Orchestrator
    participant DF as 需要予測エージェント
    participant SQ as 品質検証エージェント
    participant PO as 価格設定エージェント
    participant IO as 在庫最適化エージェント
    participant VA as 総合検証エージェント
    participant RG as レポート生成エージェント
    participant X402 as X402 Facilitator
    participant BC as Blockchain (ERC-8004)

    Note over Orch: 深夜2:00 タスク開始
    User->>Orch: トマト最適化リクエスト<br/>(product_sku, store_id)
    
    Note over Orch,PO: Phase 1: 並列実行可能なエージェント
    
    par 需要予測
        Orch->>DF: execute(product_sku, store_id)
        activate DF
        DF->>DF: POSデータ取得（過去3年）
        DF->>DF: 気象データ取得
        DF->>DF: LightGBM予測実行
        DF->>Orch: 予測結果（350個±30個）
        deactivate DF
        Orch->>X402: 決済（10 JPYC, upto）
        X402->>BC: JPYC Transfer
    and 品質検証
        Orch->>SQ: execute(product_sku)
        activate SQ
        SQ->>SQ: サプライヤー候補取得
        SQ->>SQ: DID/VC検証
        SQ->>SQ: 過去実績評価
        SQ->>Orch: 推奨サプライヤー（信頼度95点）
        deactivate SQ
        Orch->>X402: 決済（8 JPYC, exact）
        X402->>BC: JPYC Transfer
    and 価格設定
        Orch->>PO: execute(product_sku, store_id)
        activate PO
        PO->>PO: 需要弾力性分析
        PO->>PO: 競合価格取得
        PO->>PO: 時間帯別最適価格算出
        PO->>Orch: 価格カーブ（9-12時:218円...）
        deactivate PO
        Orch->>X402: 決済（12 JPYC, upto）
        X402->>BC: JPYC Transfer
    end
    
    Note over Orch,IO: Phase 2: 在庫最適化（需要予測に依存）
    
    Orch->>IO: execute(demand, supplier_quality)
    activate IO
    IO->>IO: ニュースベンダーモデル適用
    IO->>IO: 発注量最適化
    IO->>Orch: 推奨発注（280個、5時発注）
    deactivate IO
    Orch->>X402: 決済（15 JPYC, exact）
    X402->>BC: JPYC Transfer
    
    Note over Orch,VA: Phase 3: 総合検証
    
    Orch->>VA: execute(all_results)
    activate VA
    VA->>VA: 需要予測 vs 発注+在庫 整合性チェック
    VA->>VA: 粗利率目標達成チェック
    VA->>VA: サプライヤー品質チェック
    VA->>VA: 賞味期限 vs 販売期間チェック
    VA->>Orch: 検証結果（信頼度92/100）
    deactivate VA
    Orch->>X402: 決済（5 JPYC, exact）
    X402->>BC: JPYC Transfer
    Orch->>BC: ERC-8004 Validation記録
    BC-->>Orch: TxHash: 0x7a3f...
    
    Note over Orch,RG: Phase 4: 最終レポート生成
    
    Orch->>RG: execute(all_results + validation)
    activate RG
    RG->>RG: サマリーレポート生成
    RG->>Orch: 実行可能なアクションプラン
    deactivate RG
    Orch->>X402: 決済（5 JPYC, deferred）
    X402->>BC: JPYC Transfer
    
    Note over Orch: 深夜2:00:45 完了（45秒）
    
    Orch->>User: 最適化レポート提示<br/>（発注280個、5時発注、粗利¥18,200）<br/>TxHash: 0x7a3f...
    
    Note over User: バイヤーが最終承認
```

### 1.3 タイミング詳細

| フェーズ | 処理内容 | 所要時間 | コスト |
|---------|---------|---------|--------|
| Phase 1（並列） | 需要予測 + 品質検証 + 価格設定 | 8-10秒 | 30 JPYC |
| Phase 2 | 在庫最適化 | 5秒 | 15 JPYC |
| Phase 3 | 総合検証 + オンチェーン記録 | 3秒 | 5 JPYC |
| Phase 4 | レポート生成 | 2秒 | 5 JPYC |
| **合計** | | **約45秒** | **55 JPYC** |

---

## 2. X402決済フロー

### 2.1 概要

X402 v2プロトコルによるマイクロペイメントフロー。HTTP 402ステータスコードを活用し、署名ベースの認証で約2秒の即時決済を実現。

### 2.2 シーケンス図（exact方式の例）

```mermaid
sequenceDiagram
    autonumber
    participant Client as Orchestrator
    participant Agent as 在庫最適化エージェント
    participant Fac as X402 Facilitator
    participant JPYC as JPYCコントラクト
    participant BC as Blockchain

    Note over Client,Agent: Step 1: 初回リクエスト
    Client->>Agent: POST /api/execute<br/>{"demand": 350, "store_id": "S001"}
    
    Note over Agent: 決済が必要と判断
    Agent->>Client: 402 Payment Required<br/>PAYMENT-REQUIRED: {<br/>  "facilitator": "https://x402.example.com",<br/>  "token": "0x431D...BDB",<br/>  "amount": "15",<br/>  "scheme": "exact",<br/>  "nonce": "0xabc...",<br/>  "deadline": 1706000000<br/>}
    
    Note over Client: Step 2: PaymentPayload作成
    Client->>Client: PaymentPayload = {<br/>  facilitator, token, amount,<br/>  scheme, nonce, deadline<br/>}
    
    Note over Client: Step 3: 署名生成（EIP-191）
    Client->>Client: signature = sign(PaymentPayload)
    
    Note over Client,Agent: Step 4: 署名付きリトライ
    Client->>Agent: POST /api/execute<br/>PAYMENT-SIGNATURE: 0x1234...
    
    Note over Agent: Step 5: 署名検証
    Agent->>Agent: verify_signature(PaymentPayload, signature)
    
    Note over Agent,Fac: Step 6: Facilitatorに決済要求
    Agent->>Fac: POST /payment<br/>{PaymentPayload, signature}
    
    Fac->>Fac: 署名検証
    Fac->>Fac: amount検証（15 JPYC）
    Fac->>Fac: deadline検証
    
    Note over Fac,BC: Step 7: オンチェーン決済実行
    Fac->>JPYC: transfer(from: Client, to: Agent, amount: 15)
    JPYC->>BC: トランザクション送信
    BC-->>JPYC: TxHash: 0xdef...
    JPYC-->>Fac: Success
    
    Fac-->>Agent: Payment Confirmed<br/>TxHash: 0xdef...
    
    Note over Agent: Step 8: エージェント処理実行
    Agent->>Agent: execute_optimization()
    
    Note over Agent,Client: Step 9: 結果返却
    Agent->>Client: 200 OK<br/>{<br/>  "order_quantity": 280,<br/>  "supplier": "A",<br/>  "payment_tx": "0xdef..."<br/>}
```

### 2.3 支払いスキーム別の違い

#### exact方式（固定料金）

```json
// PAYMENT-REQUIRED ヘッダー
{
  "amount": "15",
  "scheme": "exact"
}
// クライアントは正確に15 JPYCを支払う
```

#### upto方式（従量課金）

```json
// PAYMENT-REQUIRED ヘッダー
{
  "amount": "20",     // 最大20 JPYC
  "scheme": "upto"
}
// エージェント実行後、実際のコストが計算される
// 例: データ処理量が少なければ12 JPYCで済む
// 差額8 JPYCは返金される
```

#### deferred方式（後払い）

```json
// PAYMENT-REQUIRED ヘッダー
{
  "amount": "5",
  "scheme": "deferred"
}
// セッション終了時に一括決済
// 複数のエージェント呼び出しをまとめて支払い
```

---

## 3. DID/VC検証フロー

### 3.1 概要

DID/VCコンソーシアム基盤と連携したサプライヤー認証フロー。Verifiable Credentialの検証により、産地証明・品質認証を確認する。

### 3.2 シーケンス図

```mermaid
sequenceDiagram
    autonumber
    participant Supplier as サプライヤーA
    participant DID as DID/VCコンソーシアム基盤
    participant SQA as 品質検証エージェント
    participant X402 as X402 Facilitator
    participant BC as Blockchain (ERC-8004)

    Note over Supplier,DID: 事前準備: サプライヤーのVC取得
    
    Supplier->>DID: VC発行リクエスト<br/>did:web:supplier-a.example.com
    DID->>DID: KYC/審査
    DID->>Supplier: VC発行<br/>{<br/>  "type": "OrganicCertificate",<br/>  "product": "トマト",<br/>  "certification": "有機JAS",<br/>  "origin": "熊本県"<br/>}
    
    Note over SQA: 発注時の品質検証開始
    
    SQA->>SQA: サプライヤー候補取得<br/>(A, B, C)
    
    loop 各サプライヤーに対して
        SQA->>DID: VC検証リクエスト<br/>did:web:supplier-a.example.com
        
        DID->>DID: DID解決（公開鍵取得）
        DID->>DID: VC署名検証
        DID->>DID: 有効期限チェック
        DID->>DID: 発行者信頼度チェック
        
        alt VCが有効
            DID->>SQA: 検証成功<br/>{<br/>  "valid": true,<br/>  "issuer": "did:web:organic-jas.go.jp",<br/>  "expiresAt": "2026-03-31"<br/>}
            SQA->>SQA: VCスコア算出: 0.95
        else VCが無効
            DID->>SQA: 検証失敗<br/>{"valid": false}
            SQA->>SQA: VCスコア算出: 0.0
        end
        
        SQA->>SQA: 過去実績スコア算出: 0.88
        SQA->>SQA: 配送リスクスコア算出: 0.92
        SQA->>SQA: 価格競争力スコア算出: 0.75
        
        SQA->>SQA: 総合スコア = <br/>0.95*0.4 + 0.88*0.3 + 0.92*0.2 + 0.75*0.1<br/>= 0.90
    end
    
    SQA->>SQA: 最高スコアのサプライヤー選定<br/>→ サプライヤーA（0.95）
    
    Note over SQA,BC: X402決済 + ERC-8004記録
    
    SQA->>X402: 決済（8 JPYC, exact）
    X402->>BC: JPYC Transfer
    
    SQA->>BC: ERC-8004 Validation記録<br/>recordValidation(<br/>  taskHash: keccak256("tomato-opt-20250124"),<br/>  validatorAgentId: 1004,<br/>  result: true,<br/>  confidenceScore: 95,<br/>  proofURI: "ipfs://Qm..."<br/>)
    BC-->>SQA: TxHash: 0x3f9a...
    
    SQA-->>SQA: 検証完了<br/>推奨: サプライヤーA（信頼度95点）
```

### 3.3 VCデータ構造例

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://www.w3.org/2018/credentials/examples/v1"
  ],
  "id": "http://example.org/credentials/3732",
  "type": ["VerifiableCredential", "OrganicCertificate"],
  "issuer": {
    "id": "did:web:organic-jas.go.jp",
    "name": "有機JAS認証機関"
  },
  "issuanceDate": "2025-01-01T00:00:00Z",
  "expirationDate": "2026-03-31T23:59:59Z",
  "credentialSubject": {
    "id": "did:web:supplier-a.example.com",
    "product": "トマト",
    "productCode": "tomato-medium-domestic",
    "certification": "有機JAS",
    "certificationNumber": "JAS-2025-001234",
    "origin": "熊本県",
    "farm": "阿蘇農園",
    "harvestDate": "2025-01-23"
  },
  "proof": {
    "type": "EcdsaSecp256k1Signature2019",
    "created": "2025-01-01T00:00:00Z",
    "proofPurpose": "assertionMethod",
    "verificationMethod": "did:web:organic-jas.go.jp#keys-1",
    "jws": "eyJhbGciOiJFUzI1NksiLCJiNjQiOmZhbHNlLCJjcml0IjpbImI2NCJdfQ..."
  }
}
```

---

## 4. ERC-8004記録フロー

### 4.1 概要

エージェントの登録・評判記録・検証結果記録をオンチェーンで管理するフロー。3つのRegistryを活用。

### 4.2 シーケンス図

```mermaid
sequenceDiagram
    autonumber
    participant Admin as システム管理者
    participant Agent as エージェント（需要予測）
    participant IdReg as ERC-8004 Identity Registry
    participant RepReg as ERC-8004 Reputation Registry
    participant ValReg as ERC-8004 Validation Registry
    participant BC as Blockchain

    Note over Admin,IdReg: フェーズ1: エージェント登録
    
    Admin->>IdReg: register(<br/>  name: "需要予測エージェントv2.3",<br/>  category: "demand-forecasting",<br/>  metadataURI: "ipfs://QmXYZ..."<br/>)
    activate IdReg
    IdReg->>IdReg: agentId = _nextAgentId++<br/>→ agentId = 1001
    IdReg->>BC: mint NFT (tokenId: 1001)
    BC-->>IdReg: Success
    IdReg->>IdReg: agents[1001] = AgentMetadata{...}
    IdReg-->>Admin: agentId: 1001
    deactivate IdReg
    
    Note over Admin: グローバル識別子:<br/>retail-ai:137:0x123...#{1001}
    
    Note over Agent: エージェント実行（30日間）
    
    loop 毎日の実行
        Agent->>Agent: 需要予測実行
        Agent->>Agent: 予測精度記録（MAPE）
    end
    
    Note over Admin,RepReg: フェーズ2: Reputation記録
    
    Admin->>RepReg: submitFeedback(<br/>  agentId: 1001,<br/>  score: 87,<br/>  tags: ["accurate", "fast"],<br/>  reportURI: "ipfs://QmABC..."<br/>)
    activate RepReg
    RepReg->>RepReg: feedbacks[1001].push({...})
    RepReg->>RepReg: stats[1001].totalFeedbacks++
    RepReg->>RepReg: stats[1001].totalScore += 87
    RepReg->>RepReg: stats[1001].averageScore = <br/>totalScore / totalFeedbacks<br/>= 87.3
    RepReg->>BC: emit FeedbackSubmitted(1001, 87)
    BC-->>RepReg: Success
    RepReg-->>Admin: Feedback recorded
    deactivate RepReg
    
    Note over Agent: 総合検証エージェントによる検証
    
    Agent->>ValReg: recordValidation(<br/>  taskHash: keccak256("tomato-opt-20250124"),<br/>  validatorAgentId: 2001,<br/>  result: true,<br/>  confidenceScore: 92,<br/>  proofURI: "ipfs://QmDEF..."<br/>)
    activate ValReg
    ValReg->>ValReg: validations[taskHash].push({<br/>  validatorAgentId: 2001,<br/>  result: true,<br/>  confidenceScore: 92,<br/>  timestamp: block.timestamp<br/>})
    ValReg->>BC: emit ValidationRecorded(taskHash, 2001, true, 92)
    BC-->>ValReg: TxHash: 0x7a3f...
    ValReg-->>Agent: Validation recorded
    deactivate ValReg
    
    Note over Admin: 後日の監査
    
    Admin->>IdReg: getAgentMetadata(1001)
    IdReg-->>Admin: {<br/>  name: "需要予測エージェントv2.3",<br/>  category: "demand-forecasting",<br/>  registeredAt: 1706000000<br/>}
    
    Admin->>RepReg: getAverageScore(1001)
    RepReg-->>Admin: 87
    
    Admin->>RepReg: getFeedbackCount(1001)
    RepReg-->>Admin: 892
    
    Admin->>ValReg: getValidations(taskHash)
    ValReg-->>Admin: [{<br/>  validatorAgentId: 2001,<br/>  result: true,<br/>  confidenceScore: 92,<br/>  proofURI: "ipfs://QmDEF..."<br/>}]
```

### 4.3 オンチェーンデータの関連性

```
Identity Registry (ERC-721 NFT)
├─ agentId: 1001 (需要予測エージェント)
│  └─ メタデータ: 名前、カテゴリ、ベンダー、モデル種類
├─ agentId: 1002 (在庫最適化エージェント)
├─ agentId: 1003 (価格設定エージェント)
└─ agentId: 2001 (総合検証エージェント)

Reputation Registry
├─ agentId: 1001
│  ├─ 評価件数: 892件
│  ├─ 平均スコア: 87.3/100
│  └─ タグ: ["accurate", "fast", "stable"]
└─ agentId: 1002
   └─ ...

Validation Registry
├─ taskHash: keccak256("tomato-opt-20250124")
│  └─ 検証者: agentId 2001
│     ├─ 結果: true
│     ├─ 信頼度: 92/100
│     └─ 証明: ipfs://QmDEF...
└─ taskHash: keccak256("tomato-opt-20250125")
   └─ ...
```

---

## 5. エージェント実行詳細フロー

### 5.1 需要予測エージェントの詳細

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant IO as 在庫最適化エージェント
    participant DB as PostgreSQL

    Orch->>IO: execute demand and supplier data
    activate IO
    
    Note over IO: インプット確認
    IO->>IO: demand mean = 350demand lower = 320demand upper = 380
    
    Note over IO: 現在在庫取得
    IO->>DB: SELECT inventory quantityFROM inventory table
    DB-->>IO: 80個
    
    Note over IO: ニュースベンダーモデル適用
    IO->>IO: パラメータ設定selling price 198円unit cost 95円
    
    IO->>IO: Critical Ratio計算result = 0.462
    
    IO->>IO: 需要分布推定standard deviation = 15.3
    
    IO->>IO: 最適発注量計算optimal order = 349個
    
    IO->>IO: 在庫調整269個 to 280個
    
    Note over IO: 発注計画確定
    IO->>IO: order time = 05:00safety stock = 50個
    
    IO-->>Orch: order quantity 280cost 15 JPYC
    deactivate IO
```

### 5.2 在庫最適化エージェントの詳細

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant IO as 在庫最適化エージェント
    participant DB as PostgreSQL
    participant Opt as 最適化エンジン

    Orch->>IO: execute demand_forecast and supplier_quality
    activate IO
    
    Note over IO: インプット確認
    IO->>IO: demand_mean = 350demand_lower = 320demand_upper = 380supplier = A, unit_price: 95円
    
    Note over IO: 現在在庫取得
    IO->>DB: SELECT inventory_quantityFROM inventoryWHERE product_sku = tomato-mediumAND store_id = S001
    DB-->>IO: 80個
    
    Note over IO: ニュースベンダーモデルパラメータ設定
    IO->>IO: selling_price = 198円unit_cost = 95円disposal_cost = 120円shortage_cost = 103円
    
    Note over IO: Critical Ratio計算
    IO->>IO: critical_ratio = shortage_cost divided by total= 103 divided by 223= 0.462
    
    Note over IO: 需要分布推定
    IO->>IO: demand_std = range divided by 3.92= 60 divided by 3.92= 15.3
    
    Note over IO: 最適発注量計算
    IO->>Opt: 正規分布パーセント点関数q=0.462, mean=350, std=15.3
    Opt-->>IO: optimal_order = 349.4
    
    IO->>IO: 現在在庫を考慮order = max value of 0 or 269結果: 269個調整後: 280個
    
    Note over IO: 発注タイミング計算
    IO->>IO: lead_time = 6時間order_time = 05:00
    
    Note over IO: 安全在庫計算
    IO->>IO: safety_stock = 350 × 0.15= 52.5 → 50個
    
    IO-->>Orch: AgentResultorder_quantity: 280confidence: 0.89cost: 15 JPYC
    deactivate IO
```

---

## 6. まとめ

### 6.1 主要フローの特徴

| フロー | 所要時間 | 主要技術 | 重要ポイント |
|--------|---------|---------|-------------|
| **全体フロー** | 約45秒 | エージェント協調 | 並列実行で高速化 |
| **X402決済** | 約2秒 | HTTP 402, 署名 | ガスレス、即時決済 |
| **DID/VC検証** | 約3秒 | 分散ID, VC | 信頼性の可視化 |
| **ERC-8004記録** | 約5秒 | NFT, オンチェーン | 監査証跡の永続化 |

### 6.2 システムの信頼性を支える仕組み

1. **並列実行**: Phase 1で3つのエージェントを同時実行し、全体処理時間を短縮
2. **段階的検証**: Phase 3で全エージェント結果の整合性を確認
3. **オンチェーン記録**: ERC-8004で検証結果を改ざん不可能な形で保存
4. **DID/VC統合**: サプライヤーの信頼性を外部認証基盤で担保

---

**作成日**: 2025-01-22  
**次回更新予定**: Phase 1実装完了時
