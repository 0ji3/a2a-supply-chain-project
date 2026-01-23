# API仕様書 - 生鮮品サプライチェーン最適化AI協調システム

## ドキュメント情報

- **プロジェクト名**: 生鮮品サプライチェーン最適化AI協調システム
- **ドキュメントタイプ**: REST API仕様書
- **バージョン**: 1.0.0
- **最終更新**: 2025-01-22
- **ベースURL**: `https://api.a2a-supply-chain.example.com/v1`

---

## 目次

1. [認証](#1-認証)
2. [最適化API](#2-最適化api)
3. [エージェントAPI](#3-エージェントapi)
4. [レポートAPI](#4-レポートapi)
5. [エラーレスポンス](#5-エラーレスポンス)
6. [Webhook](#6-webhook)

---

## 1. 認証

### 1.1 認証方式

**Bearer Token（JWT）**

```http
Authorization: Bearer <JWT_TOKEN>
```

**APIキー（外部パートナー用）**

```http
X-API-Key: <API_KEY>
```

### 1.2 JWT構造

```json
{
  "sub": "user_12345",
  "role": "buyer",
  "store_id": "S001",
  "exp": 1706000000
}
```

---

## 2. 最適化API

### 2.1 最適化タスクの作成

**エンドポイント**: `POST /optimize`

**説明**: 商品の需要予測・在庫最適化・価格設定を実行するタスクを作成します。

**リクエスト**

```http
POST /v1/optimize
Content-Type: application/json
Authorization: Bearer <TOKEN>
```

```json
{
  "product_sku": "tomato-medium-domestic",
  "store_id": "S001",
  "scheduled_at": "2025-01-24T02:00:00Z"
}
```

**リクエストパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|----------|---|------|------|
| `product_sku` | string | ✓ | 商品SKU（例: `tomato-medium-domestic`） |
| `store_id` | string | ✓ | 店舗ID（例: `S001`） |
| `scheduled_at` | string | | 実行予定時刻（ISO 8601形式）。省略時は即時実行 |

**レスポンス**

```http
HTTP/1.1 201 Created
Content-Type: application/json
```

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "product_sku": "tomato-medium-domestic",
  "store_id": "S001",
  "scheduled_at": "2025-01-24T02:00:00Z",
  "created_at": "2025-01-23T10:30:00Z",
  "estimated_completion": "2025-01-24T02:00:45Z"
}
```

**ステータスコード**

| コード | 説明 |
|-------|------|
| `201` | タスク作成成功 |
| `400` | リクエストパラメータ不正 |
| `401` | 認証失敗 |
| `429` | レート制限超過 |

---

### 2.2 最適化結果の取得

**エンドポイント**: `GET /optimize/{execution_id}`

**説明**: 実行中または完了した最適化タスクの結果を取得します。

**リクエスト**

```http
GET /v1/optimize/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <TOKEN>
```

**レスポンス（実行中）**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "current_phase": "validation",
    "completed_agents": ["demand_forecast", "supplier_quality", "price_optimizer", "inventory_optimizer"],
    "total_agents": 6
  },
  "started_at": "2025-01-24T02:00:00Z"
}
```

**レスポンス（完了）**

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "product_sku": "tomato-medium-domestic",
  "store_id": "S001",
  "result": {
    "demand_forecast": {
      "predicted_demand": 350,
      "confidence_interval": {
        "lower": 320,
        "upper": 380
      },
      "confidence": 0.92
    },
    "inventory_optimization": {
      "order_quantity": 280,
      "supplier": {
        "id": "supplier_a",
        "name": "サプライヤーA",
        "unit_price": 95
      },
      "order_timing": "05:00",
      "safety_stock": 50
    },
    "price_optimization": {
      "price_curve": [
        {"time_range": "09:00-12:00", "price": 218},
        {"time_range": "12:00-18:00", "price": 198},
        {"time_range": "18:00-21:00", "price": 168}
      ],
      "expected_profit": 18200
    },
    "validation": {
      "overall_confidence": 0.92,
      "all_checks_passed": true,
      "warnings": []
    }
  },
  "costs": {
    "demand_forecast": 10,
    "supplier_quality": 8,
    "price_optimizer": 12,
    "inventory_optimizer": 15,
    "validation": 5,
    "report_generator": 5,
    "total": 55
  },
  "blockchain_tx": "0x7a3f9c2b1e8d4f6a5c3e9b7d1f4a8c6e2b5d9f3a7c1e8b4d6f2a9c5e3b7d1f4a",
  "started_at": "2025-01-24T02:00:00Z",
  "completed_at": "2025-01-24T02:00:45Z",
  "execution_time": 45.2
}
```

**ステータス値**

| ステータス | 説明 |
|----------|------|
| `queued` | 実行待機中 |
| `running` | 実行中 |
| `completed` | 完了 |
| `failed` | 失敗 |

---

### 2.3 最適化タスク一覧の取得

**エンドポイント**: `GET /optimize`

**説明**: 最適化タスクの一覧を取得します。

**リクエスト**

```http
GET /v1/optimize?status=completed&limit=20&offset=0
Authorization: Bearer <TOKEN>
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|----------|---|------|------|
| `status` | string | | フィルタ: `queued`, `running`, `completed`, `failed` |
| `product_sku` | string | | 商品SKUでフィルタ |
| `store_id` | string | | 店舗IDでフィルタ |
| `limit` | integer | | 取得件数（デフォルト: 20、最大: 100） |
| `offset` | integer | | オフセット（デフォルト: 0） |

**レスポンス**

```json
{
  "tasks": [
    {
      "execution_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "product_sku": "tomato-medium-domestic",
      "store_id": "S001",
      "scheduled_at": "2025-01-24T02:00:00Z",
      "completed_at": "2025-01-24T02:00:45Z",
      "total_cost": 55
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

## 3. エージェントAPI

### 3.1 エージェント情報取得

**エンドポイント**: `GET /agents/{agent_id}`

**説明**: ERC-8004に登録されたエージェントの情報を取得します。

**リクエスト**

```http
GET /v1/agents/1001
Authorization: Bearer <TOKEN>
```

**レスポンス**

```json
{
  "agent_id": 1001,
  "name": "需要予測エージェントv2.3",
  "category": "demand-forecasting",
  "vendor": "AI Solutions Corp",
  "model_type": "LightGBM",
  "metadata_uri": "ipfs://QmXYZ...",
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "registered_at": "2024-12-01T00:00:00Z",
  "reputation": {
    "average_score": 87.3,
    "total_feedbacks": 892,
    "top_tags": ["accurate", "fast", "stable"]
  },
  "performance_metrics": {
    "mape": 8.2,
    "cost_savings": 2840000,
    "uptime": 99.5
  }
}
```

---

### 3.2 エージェント評価の取得

**エンドポイント**: `GET /agents/{agent_id}/reputation`

**説明**: エージェントの評価履歴を取得します。

**リクエスト**

```http
GET /v1/agents/1001/reputation?limit=10&offset=0
Authorization: Bearer <TOKEN>
```

**レスポンス**

```json
{
  "agent_id": 1001,
  "average_score": 87.3,
  "total_feedbacks": 892,
  "feedbacks": [
    {
      "client": "0xabcdef...",
      "score": 90,
      "tags": ["accurate", "fast"],
      "report_uri": "ipfs://QmABC...",
      "timestamp": "2025-01-23T00:00:00Z"
    }
  ],
  "limit": 10,
  "offset": 0
}
```

---

### 3.3 エージェント評価の投稿

**エンドポイント**: `POST /agents/{agent_id}/feedback`

**説明**: エージェントの実行結果に対する評価を投稿します。

**リクエスト**

```http
POST /v1/agents/1001/feedback
Content-Type: application/json
Authorization: Bearer <TOKEN>
```

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": 90,
  "tags": ["accurate", "fast"],
  "comment": "予測精度が高く、実行時間も短かった。"
}
```

**レスポンス**

```json
{
  "feedback_id": "fb_12345",
  "agent_id": 1001,
  "score": 90,
  "blockchain_tx": "0xabc...",
  "created_at": "2025-01-24T03:00:00Z"
}
```

---

## 4. レポートAPI

### 4.1 最適化レポートの取得

**エンドポイント**: `GET /reports/{execution_id}`

**説明**: 最適化タスクの詳細レポートを取得します。

**リクエスト**

```http
GET /v1/reports/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <TOKEN>
```

**レスポンス**

```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "report": {
    "title": "トマト（中玉・国産）最適化レポート",
    "execution_date": "2025-01-24",
    "summary": {
      "order_quantity": 280,
      "supplier": "サプライヤーA",
      "order_time": "05:00",
      "unit_price": 95
    },
    "pricing": {
      "morning": {"time": "09:00-12:00", "price": 218},
      "afternoon": {"time": "12:00-18:00", "price": 198},
      "evening": {"time": "18:00-21:00", "price": 168}
    },
    "forecast": {
      "predicted_sales": 350,
      "predicted_waste": 8,
      "waste_rate": 2.3,
      "expected_profit": 18200
    },
    "validation": {
      "confidence": 92,
      "status": "all_checks_passed"
    },
    "blockchain_proof": "0x7a3f9c2b1e8d4f6a5c3e9b7d1f4a8c6e2b5d9f3a7c1e8b4d6f2a9c5e3b7d1f4a"
  },
  "format": "json"
}
```

---

### 4.2 レポートのダウンロード

**エンドポイント**: `GET /reports/{execution_id}/download`

**説明**: レポートをPDFまたはCSV形式でダウンロードします。

**リクエスト**

```http
GET /v1/reports/550e8400-e29b-41d4-a716-446655440000/download?format=pdf
Authorization: Bearer <TOKEN>
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|----------|---|------|------|
| `format` | string | | `pdf`, `csv`, `json`（デフォルト: `pdf`） |

**レスポンス**

```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="optimization-report-2025-01-24.pdf"

[PDF バイナリデータ]
```

---

## 5. エラーレスポンス

### 5.1 エラーフォーマット

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "product_sku is required",
    "details": {
      "field": "product_sku",
      "reason": "missing_field"
    },
    "request_id": "req_abc123"
  }
}
```

### 5.2 エラーコード一覧

| コード | HTTPステータス | 説明 |
|-------|--------------|------|
| `INVALID_REQUEST` | 400 | リクエストパラメータ不正 |
| `UNAUTHORIZED` | 401 | 認証失敗 |
| `FORBIDDEN` | 403 | アクセス権限なし |
| `NOT_FOUND` | 404 | リソースが見つからない |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `INTERNAL_ERROR` | 500 | サーバー内部エラー |
| `SERVICE_UNAVAILABLE` | 503 | サービス一時停止中 |

---

## 6. Webhook

### 6.1 Webhook設定

**エンドポイント**: `POST /webhooks`

**説明**: タスク完了時のWebhook通知を設定します。

**リクエスト**

```json
{
  "url": "https://your-app.example.com/webhook",
  "events": ["task.completed", "task.failed"],
  "secret": "your_webhook_secret"
}
```

**レスポンス**

```json
{
  "webhook_id": "wh_12345",
  "url": "https://your-app.example.com/webhook",
  "events": ["task.completed", "task.failed"],
  "created_at": "2025-01-24T00:00:00Z"
}
```

---

### 6.2 Webhook ペイロード

**タスク完了時**

```http
POST https://your-app.example.com/webhook
Content-Type: application/json
X-Webhook-Signature: sha256=...
```

```json
{
  "event": "task.completed",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_sku": "tomato-medium-domestic",
  "store_id": "S001",
  "completed_at": "2025-01-24T02:00:45Z",
  "result_url": "https://api.a2a-supply-chain.example.com/v1/optimize/550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 7. レート制限

| エンドポイント | レート制限 | 備考 |
|--------------|----------|------|
| `POST /optimize` | 100リクエスト/時間 | 店舗単位 |
| `GET /optimize` | 1000リクエスト/時間 | 全体 |
| `GET /agents` | 500リクエスト/時間 | 全体 |

**レート制限超過時のレスポンスヘッダー**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706004000
Retry-After: 3600
```

---

## 8. ページネーション

一覧取得APIは以下の形式でページネーションをサポートします。

**リクエスト**

```http
GET /v1/optimize?limit=20&offset=40
```

**レスポンス**

```json
{
  "tasks": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 40,
    "has_more": true
  }
}
```

---

## 9. バージョニング

APIバージョンはURLパスに含まれます。

- **現在**: `/v1/...`
- **次期**: `/v2/...`（Phase 4で導入予定）

旧バージョンは最低6ヶ月間サポートされます。

---

**作成日**: 2025-01-22  
**次回更新予定**: Phase 1実装完了時