# 実装ガイド

このドキュメントは、Phase 1の各コンポーネントを段階的に実装するための詳細な手順を提供します。

---

## 📋 目次

1. [レポート生成エージェントの実装](#1-レポート生成エージェントの実装)
2. [PostgreSQL統合](#2-postgresql統合)
3. [Redis統合](#3-redis統合)
4. [FastAPI実装](#4-fastapi実装)
5. [統合テスト](#5-統合テスト)

---

## 1. レポート生成エージェントの実装

### 1.1 ファイル作成

```bash
# ファイル作成
touch python/agents/report_generator.py
```

### 1.2 基本構造実装

```python
# python/agents/report_generator.py

from typing import Dict
from datetime import datetime
from .base import Agent, AgentResult, PaymentScheme, PaymentConfig


class ReportGeneratorAgent(Agent):
    """レポート生成エージェント"""
    
    def __init__(self):
        super().__init__(
            name="report_generator",
            payment_config=PaymentConfig(
                scheme=PaymentScheme.DEFERRED,
                base_amount=5  # 5 JPYC固定
            ),
            erc8004_id=None  # Phase 2で設定
        )
    
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        レポート生成の実行
        
        Input:
            - demand_result: 需要予測結果
            - inventory_result: 在庫最適化結果
            - product_sku: 商品SKU
            - store_id: 店舗ID
            
        Output:
            - report_text: テキストレポート
            - report_json: JSON形式のレポート
        """
        # TODO: 実装
        pass
```

### 1.3 レポート生成ロジック実装

```python
    async def execute(self, input_data: Dict) -> AgentResult:
        demand_result = input_data.get("demand_result")
        inventory_result = input_data.get("inventory_result")
        product_sku = input_data.get("product_sku")
        store_id = input_data.get("store_id")
        
        # バリデーション
        if not all([demand_result, inventory_result, product_sku, store_id]):
            return AgentResult(
                success=False,
                data={},
                confidence=0.0,
                execution_time=0.0,
                cost=0,
                error_message="Missing required input"
            )
        
        # レポート生成
        report_text = self._generate_text_report(
            demand_result, inventory_result, product_sku, store_id
        )
        
        report_json = self._generate_json_report(
            demand_result, inventory_result, product_sku, store_id
        )
        
        # コスト計算
        cost = self.calculate_cost()
        
        return AgentResult(
            success=True,
            data={
                "report_text": report_text,
                "report_json": report_json
            },
            confidence=1.0,  # レポート生成は確定的
            execution_time=0.0,
            cost=cost
        )
```

### 1.4 レポートフォーマット実装

```python
    def _generate_text_report(
        self, demand_result, inventory_result, product_sku, store_id
    ) -> str:
        """テキストレポート生成"""
        # 商品名取得（簡易版）
        product_names = {
            "tomato-medium-domestic": "トマト（中玉・国産）"
        }
        product_name = product_names.get(product_sku, product_sku)
        
        # 日付
        today = datetime.now().strftime("%Y年%m月%d日（%a）")
        
        # データ抽出
        predicted_demand = demand_result.get("predicted_demand")
        order_quantity = inventory_result.get("order_quantity")
        supplier = inventory_result.get("supplier", {})
        order_timing = inventory_result.get("order_timing")
        
        # レポート生成
        report = f"""
🍅 {product_name} 最適化レポート
実行日：{today}

📦 推奨発注量：{order_quantity}個
🏪 発注先：{supplier.get('name')}
⏰ 発注時刻：{order_timing}
💰 調達単価：{supplier.get('unit_price')}円/個

📊 予測結果：
  - 販売予測：{predicted_demand}個
  - 安全在庫：{inventory_result.get('safety_stock')}個
  - 予想廃棄：{inventory_result.get('expected_waste')}個

✅ 信頼度：高
"""
        return report.strip()
```

### 1.5 テスト作成

```python
# tests/test_report_generator.py

import pytest
from python.agents.report_generator import ReportGeneratorAgent


@pytest.mark.asyncio
async def test_report_generator():
    """レポート生成エージェントのテスト"""
    agent = ReportGeneratorAgent()
    
    # モックデータ
    input_data = {
        "demand_result": {
            "predicted_demand": 350,
            "confidence_interval": {"lower": 320, "upper": 380}
        },
        "inventory_result": {
            "order_quantity": 280,
            "supplier": {
                "id": "supplier_a",
                "name": "サプライヤーA",
                "unit_price": 95
            },
            "order_timing": "05:00",
            "safety_stock": 50,
            "expected_waste": 0
        },
        "product_sku": "tomato-medium-domestic",
        "store_id": "S001"
    }
    
    result = await agent._execute_with_timing(input_data)
    
    assert result.success == True
    assert "report_text" in result.data
    assert "report_json" in result.data
    assert result.cost == 5
```

### 1.6 Orchestratorへの統合

```python
# python/orchestrator.py の execute_optimization_task() に追加

# ... 既存のコード ...

# Phase 3: レポート生成
report_result = await self.report_generator_agent._execute_with_timing({
    "demand_result": demand_result.data,
    "inventory_result": inventory_result.data,
    "product_sku": product_sku,
    "store_id": store_id
})

# エージェント実行履歴を記録
await self._record_agent_execution(
    db_session,
    execution_id,
    "report_generator",
    {...},
    report_result
)

# レポートをタスクに保存
await self._update_task_status(
    db_session,
    execution_id,
    "completed",
    total_cost=total_cost,
    report_data=report_result.data
)
```

---

## 2. PostgreSQL統合

### 2.1 Docker環境確認

```bash
# PostgreSQL起動
docker-compose up -d postgres

# 接続確認
docker-compose exec postgres psql -U postgres -d a2a_supply_chain

# テーブル確認
\dt

# データ確認
SELECT COUNT(*) FROM pos_sales;
SELECT * FROM stores;
SELECT * FROM products;
```

### 2.2 接続テスト実装

```python
# tests/test_database.py

from python.database import get_db_session, engine


def test_database_connection():
    """データベース接続テスト"""
    # エンジン接続確認
    conn = engine.connect()
    result = conn.execute("SELECT 1")
    assert result.fetchone()[0] == 1
    conn.close()


def test_database_session():
    """データベースセッションテスト"""
    with get_db_session() as db:
        result = db.execute("SELECT COUNT(*) FROM stores")
        count = result.fetchone()[0]
        assert count > 0  # 最低1件のデータがあること
```

### 2.3 エージェントでの実際のDB使用

```python
# python/agents/demand_forecast.py の _fetch_pos_data を修正

async def _fetch_pos_data(
    self,
    db_session,
    product_sku: str,
    store_id: str,
    days: int = 30
) -> list:
    """POSデータ取得（実際のデータベース使用）"""
    from datetime import date, timedelta
    from sqlalchemy import text
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    query = text("""
        SELECT 
            date,
            sales_quantity,
            price,
            day_of_week,
            is_holiday
        FROM pos_sales
        WHERE product_sku = :product_sku
          AND store_id = :store_id
          AND date >= :start_date
          AND date < :end_date
        ORDER BY date DESC
    """)
    
    result = db_session.execute(
        query,
        {
            "product_sku": product_sku,
            "store_id": store_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    
    rows = result.fetchall()
    
    return [
        {
            "date": row[0],
            "sales_quantity": row[1],
            "price": float(row[2]),
            "day_of_week": row[3],
            "is_holiday": row[4]
        }
        for row in rows
    ]
```

### 2.4 統合テスト

```python
# tests/test_integration_db.py

import pytest
from python.orchestrator import AgentCoordinator
from python.database import get_db_session


@pytest.mark.asyncio
async def test_orchestrator_with_real_db():
    """OrchestratorとPostgreSQLの統合テスト"""
    coordinator = AgentCoordinator()
    
    result = await coordinator.execute_optimization_task(
        product_sku="tomato-medium-domestic",
        store_id="S001"
    )
    
    assert result.execution_id is not None
    assert result.total_cost > 0
    
    # データベースにレコードが記録されていることを確認
    with get_db_session() as db:
        query = """
            SELECT status, total_cost 
            FROM optimization_tasks 
            WHERE execution_id = :execution_id
        """
        row = db.execute(query, {"execution_id": result.execution_id}).fetchone()
        assert row[0] == "completed"
        assert row[1] == result.total_cost
```

---

## 3. Redis統合

### 3.1 キャッシュモジュール作成

```bash
touch python/utils/cache.py
```

```python
# python/utils/cache.py

import redis
import json
from typing import Optional, Any
from python.config import settings


class CacheManager:
    """Redisキャッシュマネージャー"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """キャッシュ取得"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = None
    ) -> bool:
        """キャッシュ設定"""
        ttl = ttl or settings.redis_cache_ttl
        return self.redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    def delete(self, key: str) -> bool:
        """キャッシュ削除"""
        return self.redis_client.delete(key) > 0
    
    def exists(self, key: str) -> bool:
        """キャッシュ存在確認"""
        return self.redis_client.exists(key) > 0


# グローバルインスタンス
cache = CacheManager()
```

### 3.2 エージェントでのキャッシュ使用

```python
# python/agents/demand_forecast.py に追加

from python.utils.cache import cache

async def execute(self, input_data: Dict) -> AgentResult:
    product_sku = input_data.get("product_sku")
    store_id = input_data.get("store_id")
    
    # キャッシュキー生成
    from datetime import date
    cache_key = f"df:{product_sku}:{store_id}:{date.today()}"
    
    # キャッシュ確認
    cached_result = cache.get(cache_key)
    if cached_result:
        return AgentResult(
            success=True,
            data=cached_result,
            confidence=0.85,
            execution_time=0.0,
            cost=0  # キャッシュヒットの場合はコスト0
        )
    
    # ... 既存の予測処理 ...
    
    # キャッシュに保存（TTL: 24時間）
    cache.set(cache_key, result.data, ttl=86400)
    
    return result
```

### 3.3 キャッシュテスト

```python
# tests/test_cache.py

import pytest
from python.utils.cache import cache


def test_cache_basic():
    """キャッシュ基本動作テスト"""
    key = "test_key"
    value = {"test": "data"}
    
    # 設定
    assert cache.set(key, value, ttl=60)
    
    # 取得
    assert cache.get(key) == value
    
    # 存在確認
    assert cache.exists(key)
    
    # 削除
    assert cache.delete(key)
    assert not cache.exists(key)


@pytest.mark.asyncio
async def test_demand_forecast_cache():
    """需要予測エージェントのキャッシュテスト"""
    from python.agents.demand_forecast import DemandForecastAgent
    
    agent = DemandForecastAgent()
    
    # 1回目: キャッシュミス
    result1 = await agent.execute({...})
    assert result1.cost > 0
    
    # 2回目: キャッシュヒット
    result2 = await agent.execute({...})
    assert result2.cost == 0  # キャッシュヒットなのでコスト0
```

---

## 4. FastAPI実装

### 4.1 APIメインファイル作成

```python
# python/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from python.config import settings

# ロギング設定
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPIアプリ作成
app = FastAPI(
    title="A2A Supply Chain Optimization API",
    description="生鮮品サプライチェーン最適化AI協調システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# ルーター登録
from python.api import routes
app.include_router(routes.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "python.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
```

### 4.2 ルーター実装

```python
# python/api/routes.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from python.orchestrator import AgentCoordinator
from python.database import get_db_session

router = APIRouter()


# リクエスト/レスポンスモデル
class OptimizationRequest(BaseModel):
    product_sku: str
    store_id: str
    scheduled_at: Optional[str] = None


class OptimizationResponse(BaseModel):
    execution_id: str
    status: str
    message: str


# グローバルコーディネーター
coordinator = AgentCoordinator()


@router.post("/optimize", response_model=OptimizationResponse)
async def create_optimization_task(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    最適化タスクの作成
    """
    # バックグラウンドタスク登録
    execution_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        execute_optimization,
        execution_id,
        request.product_sku,
        request.store_id
    )
    
    return OptimizationResponse(
        execution_id=execution_id,
        status="queued",
        message="Optimization task created successfully"
    )


async def execute_optimization(
    execution_id: str,
    product_sku: str,
    store_id: str
):
    """バックグラウンドで実行される最適化処理"""
    try:
        result = await coordinator.execute_optimization_task(
            product_sku=product_sku,
            store_id=store_id
        )
    except Exception as e:
        # エラーログ記録
        logger.error(f"Optimization failed: {e}")


@router.get("/optimize/{execution_id}")
async def get_optimization_result(execution_id: str):
    """
    最適化結果の取得
    """
    with get_db_session() as db:
        query = """
            SELECT 
                execution_id,
                product_sku,
                store_id,
                status,
                total_cost,
                report_data,
                created_at,
                completed_at
            FROM optimization_tasks
            WHERE execution_id = :execution_id
        """
        
        result = db.execute(query, {"execution_id": execution_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "execution_id": str(row[0]),
            "product_sku": row[1],
            "store_id": row[2],
            "status": row[3],
            "total_cost": row[4],
            "report": row[5],
            "created_at": row[6].isoformat(),
            "completed_at": row[7].isoformat() if row[7] else None
        }
```

### 4.3 API起動とテスト

```bash
# API起動
cd python
python -m uvicorn api.main:app --reload --port 8000

# 別ターミナルでテスト
curl http://localhost:8000/health

# 最適化タスク作成
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{"product_sku": "tomato-medium-domestic", "store_id": "S001"}'

# 結果取得（execution_idは上記のレスポンスから）
curl http://localhost:8000/api/v1/optimize/{execution_id}
```

---

## 5. 統合テスト

### 5.1 エンドツーエンドテスト

```python
# tests/test_e2e.py

import pytest
import httpx
from time import sleep


@pytest.mark.asyncio
async def test_full_optimization_flow():
    """フルフロー統合テスト"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. ヘルスチェック
        response = await client.get(f"{base_url}/health")
        assert response.status_code == 200
        
        # 2. タスク作成
        response = await client.post(
            f"{base_url}/api/v1/optimize",
            json={
                "product_sku": "tomato-medium-domestic",
                "store_id": "S001"
            }
        )
        assert response.status_code == 200
        data = response.json()
        execution_id = data["execution_id"]
        
        # 3. タスク完了を待つ（最大30秒）
        for _ in range(30):
            response = await client.get(
                f"{base_url}/api/v1/optimize/{execution_id}"
            )
            data = response.json()
            
            if data["status"] == "completed":
                break
            
            sleep(1)
        
        # 4. 結果検証
        assert data["status"] == "completed"
        assert data["total_cost"] > 0
        assert data["report"] is not None
```

### 5.2 パフォーマンステスト

```python
# tests/test_performance.py

import pytest
import time


@pytest.mark.asyncio
async def test_response_time():
    """レスポンスタイムテスト"""
    from python.orchestrator import AgentCoordinator
    
    coordinator = AgentCoordinator()
    
    start_time = time.time()
    
    result = await coordinator.execute_optimization_task(
        product_sku="tomato-medium-domestic",
        store_id="S001"
    )
    
    elapsed_time = time.time() - start_time
    
    # 60秒以内に完了すること
    assert elapsed_time < 60
    
    # 結果が正常であること
    assert result.total_cost > 0
```

---

## 📝 実装チェックリスト

各実装後にチェック:

### レポート生成
- [ ] ReportGeneratorAgent実装
- [ ] テキストレポート生成
- [ ] JSONレポート生成
- [ ] Orchestrator統合
- [ ] テスト成功

### PostgreSQL統合
- [ ] Docker起動確認
- [ ] 接続テスト
- [ ] エージェントDB統合
- [ ] トランザクション確認
- [ ] 統合テスト成功

### Redis統合
- [ ] CacheManager実装
- [ ] エージェントキャッシュ統合
- [ ] TTL動作確認
- [ ] キャッシュテスト成功

### FastAPI実装
- [ ] main.py作成
- [ ] routes.py作成
- [ ] POST /optimize実装
- [ ] GET /optimize/{id}実装
- [ ] API動作確認

### 統合テスト
- [ ] E2Eテスト実装
- [ ] パフォーマンステスト
- [ ] すべてのテスト成功

---

**次のステップ**: `docs/phase1-implementation-plan.md` のチェックリストを更新

**最終更新**: 2025-01-23