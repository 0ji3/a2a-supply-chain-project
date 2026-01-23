# システム仕様書 - 生鮮品サプライチェーン最適化AI協調システム

## ドキュメント情報

- **プロジェクト名**: 生鮮品サプライチェーン最適化AI協調システム
- **ドキュメントタイプ**: 技術仕様書
- **バージョン**: 1.0.0
- **最終更新**: 2025-01-22
- **ステータス**: Draft

---

## 目次

1. [システムアーキテクチャ](#1-システムアーキテクチャ)
2. [コンポーネント仕様](#2-コンポーネント仕様)
3. [データモデル](#3-データモデル)
4. [プロトコル統合](#4-プロトコル統合)
5. [API設計](#5-api設計)
6. [セキュリティ](#6-セキュリティ)
7. [パフォーマンス要件](#7-パフォーマンス要件)
8. [開発環境](#8-開発環境)
9. [デプロイメント](#9-デプロイメント)
10. [監視・運用](#10-監視運用)

---

## 1. システムアーキテクチャ

### 1.1 全体アーキテクチャ（C4モデル Level 1: Context）

```
┌────────────────────────────────────────────────────────────┐
│                    外部システム・ユーザー                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  バイヤー │  │サプライヤー│  │ DID/VC  │   │ 気象庁API  │    │
│  │  (店舗)  │  │  (メーカー)│  │  基盤   │    │           │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
│        │             │             │             │        │
└────────┼─────────────┼─────────────┼─────────────┼────────┘
         │             │             │             │
         ▼             ▼             ▼             ▼
┌────────────────────────────────────────────────────────────┐
│              A2A Supply Chain Optimization System          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         AI Agent Orchestration Layer                 │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │  │
│  │  │需要予測 │ │在庫最適. │ │価格設定 │ │品質検証  │        │   │
│  │  │agent.  │ │agent   │ │agent.  │ │agent.  │         │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘         │  │
│  │  ┌────────┐ ┌────────────────────┐                   │  │
│  │  │総合検証 │ │最終サマリー生成       │                   │  │
│  │  │agent.  │ │agent.              │                   │  │
│  │  └────────┘ └────────────────────┘                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Payment & Trust Layer                        │  │
│  │  ┌─────────────────┐  ┌────────────────────┐         │  │
│  │  │ X402 Facilitator│  │ ERC-8004 Registry  │         │  │
│  │  │ (Micropayment)  │  │ (Identity/Rep/Val) │         │  │
│  │  └─────────────────┘  └────────────────────┘         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Data Layer                                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ Postgre  │  │  Redis   │  │  IPFS    │            │  │
│  │  │ (POS等)  │  │ (Cache)  │  │(OffChain)│            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Blockchain Layer     │
         │  (Anvil/Sepolia/      │
         │   Polygon)            │
         │  - JPYC Token         │
         │  - ERC-8004 Contracts │
         └───────────────────────┘
```

### 1.2 コンテナアーキテクチャ（C4モデル Level 2: Container）

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌────────────────┐                                         │
│  │ Web Dashboard  │  (Optional: Phase 4)                    │
│  │   (React)      │                                         │
│  └────────┬───────┘                                         │
│           │ HTTPS/REST                                      │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Orchestrator Service (Python)                      │   │
│  │   - Agent coordination                               │   │
│  │   - Task scheduling (APScheduler)                    │   │
│  │   - Result aggregation                               │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                           │
│  ┌──────────────┼───────────────────────────────────────┐   │
│  │              ▼                                       │   │
│  │   ┌──────────────────┐  ┌──────────────────┐         │   │
│  │   │ Demand Forecast  │  │ Inventory Opt    │         │   │
│  │   │ Agent (Python)   │  │ Agent (Python)   │         │   │
│  │   │ - LightGBM       │  │ - Newsvendor     │         │   │
│  │   │ - Weather API    │  │ - Optimization   │         │   │
│  │   └──────────────────┘  └──────────────────┘         │   │
│  │                                                      │   │
│  │   ┌──────────────────┐  ┌──────────────────┐         │   │
│  │   │ Price Optimizer  │  │ Supplier Quality │         │   │
│  │   │ Agent (Python)   │  │ Agent (Python)   │         │   │
│  │   │ - Price elasticity│ │ - DID/VC verify  │         │   │
│  │   └──────────────────┘  └──────────────────┘         │   │
│  │                                                      │   │
│  │   ┌──────────────────┐  ┌──────────────────┐         │   │
│  │   │ Validation Agent │  │ Report Generator │         │   │
│  │   │ (Python)         │  │ Agent (Python)   │         │   │
│  │   │ - Consistency    │  │ - Summary output │         │   │
│  │   └──────────────────┘  └──────────────────┘         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Payment Service (Python)                           │   │
│  │   - X402 client integration                          │   │
│  │   - JPYC payment execution                           │   │
│  │   - Payment state management                         │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                           │
│  ┌──────────────┼───────────────────────────────────────┐   │
│  │              ▼                                       │   │
│  │   Blockchain Service (Python)                        │   │
│  │   - web3.py integration                              │   │
│  │   - ERC-8004 contract interaction                    │   │
│  │   - Transaction management                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PostgreSQL  │  │    Redis     │  │  RabbitMQ    │       │
│  │  - POS data  │  │  - Cache     │  │  - Message   │       │
│  │  - History   │  │  - Session   │  │    queue     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   IPFS Node  │  │   Prometheus │                         │
│  │  - Off-chain │  │  - Metrics   │                         │
│  │    storage   │  │  - Monitoring│                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Blockchain Layer                         │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │   Ethereum-compatible Chain                        │     │
│  │   (Anvil / Sepolia / Polygon)                      │     │
│  │                                                    │     │
│  │   Smart Contracts:                                 │     │
│  │   - JPYC Token (ERC-20)                            │     │
│  │   - ERC-8004 Identity Registry                     │     │
│  │   - ERC-8004 Reputation Registry                   │     │
│  │   - ERC-8004 Validation Registry                   │     │
│  │   - Payment Escrow (optional)                      │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 技術スタック詳細

| レイヤー | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **Frontend** | React | 18.x | ダッシュボード（Phase 4） |
| **Backend** | Python | 3.11+ | エージェント実装 |
| | FastAPI | 0.104+ | REST API |
| | web3.py | 6.x | ブロックチェーン連携 |
| | LangChain | 0.1.x | エージェントフレームワーク |
| **ML** | scikit-learn | 1.3+ | 機械学習モデル |
| | LightGBM | 4.1+ | 需要予測モデル |
| | pandas | 2.1+ | データ処理 |
| | numpy | 1.26+ | 数値計算 |
| **Blockchain** | Foundry | Latest | スマートコントラクト開発 |
| | Solidity | 0.8.20+ | コントラクト言語 |
| | Anvil | Latest | ローカルチェーン |
| **Database** | PostgreSQL | 15+ | トランザクショナルデータ |
| | Redis | 7+ | キャッシュ・セッション |
| **Message Queue** | RabbitMQ | 3.12+ | 非同期処理 |
| **Storage** | IPFS | Latest | オフチェーンストレージ |
| **Monitoring** | Prometheus | 2.x | メトリクス収集 |
| | Grafana | 10.x | メトリクス可視化 |
| **Testing** | pytest | 7.x | Pythonテスト |
| | forge test | - | Solidityテスト |

---

## 2. コンポーネント仕様

### 2.1 Orchestrator Service

**責務**:
- エージェントのライフサイクル管理
- タスクスケジューリング（毎日深夜2時実行）
- エージェント間の依存関係解決
- 結果の集約・永続化

**主要クラス**:

```python
# orchestrator/coordinator.py
class AgentCoordinator:
    """エージェント協調制御"""
    
    def __init__(
        self,
        payment_service: PaymentService,
        blockchain_service: BlockchainService
    ):
        self.payment_service = payment_service
        self.blockchain_service = blockchain_service
        self.agents: Dict[str, Agent] = {}
        
    async def execute_optimization_task(
        self,
        product_sku: str,
        store_id: str
    ) -> OptimizationResult:
        """
        最適化タスクの実行
        
        Args:
            product_sku: 商品SKU（例: "tomato-medium-domestic"）
            store_id: 店舗ID
            
        Returns:
            OptimizationResult: 最適化結果
        """
        # Phase 1: 並列実行可能なエージェント
        demand_task = self._execute_agent(
            "demand_forecast", 
            {"product_sku": product_sku, "store_id": store_id}
        )
        quality_task = self._execute_agent(
            "supplier_quality",
            {"product_sku": product_sku}
        )
        price_task = self._execute_agent(
            "price_optimizer",
            {"product_sku": product_sku, "store_id": store_id}
        )
        
        # 並列実行
        demand_result, quality_result, price_result = await asyncio.gather(
            demand_task, quality_task, price_task
        )
        
        # Phase 2: 在庫最適化（需要予測に依存）
        inventory_result = await self._execute_agent(
            "inventory_optimizer",
            {
                "demand_forecast": demand_result,
                "supplier_quality": quality_result
            }
        )
        
        # Phase 3: 総合検証
        validation_result = await self._execute_agent(
            "validation",
            {
                "demand": demand_result,
                "inventory": inventory_result,
                "price": price_result,
                "quality": quality_result
            }
        )
        
        # Phase 4: 最終レポート生成
        report_result = await self._execute_agent(
            "report_generator",
            {
                "all_results": {
                    "demand": demand_result,
                    "inventory": inventory_result,
                    "price": price_result,
                    "quality": quality_result,
                    "validation": validation_result
                }
            }
        )
        
        return OptimizationResult(
            product_sku=product_sku,
            store_id=store_id,
            report=report_result,
            total_cost=self._calculate_total_cost(),
            blockchain_tx=validation_result.tx_hash
        )
    
    async def _execute_agent(
        self,
        agent_name: str,
        input_data: Dict
    ) -> AgentResult:
        """
        個別エージェントの実行
        
        1. エージェントに処理を委譲
        2. X402決済を実行
        3. ERC-8004に実行記録を保存
        """
        agent = self.agents[agent_name]
        
        # エージェント実行
        result = await agent.execute(input_data)
        
        # X402決済
        payment_result = await self.payment_service.pay_agent(
            agent_id=agent.erc8004_id,
            amount=agent.payment_config.amount,
            scheme=agent.payment_config.scheme
        )
        
        # ERC-8004記録（必要に応じて）
        if agent.should_record_onchain:
            tx_hash = await self.blockchain_service.record_execution(
                agent_id=agent.erc8004_id,
                result_hash=hash_result(result),
                confidence_score=result.confidence
            )
            result.tx_hash = tx_hash
        
        return result
```

### 2.2 エージェント基底クラス

```python
# agents/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class PaymentScheme(Enum):
    EXACT = "exact"
    UPTO = "upto"
    DEFERRED = "deferred"

@dataclass
class PaymentConfig:
    scheme: PaymentScheme
    base_amount: int  # JPYC単位
    variable_rate: Optional[float] = None  # upto方式用

@dataclass
class AgentResult:
    success: bool
    data: Dict
    confidence: float  # 0.0 ~ 1.0
    execution_time: float  # 秒
    cost: int  # JPYC
    tx_hash: Optional[str] = None

class Agent(ABC):
    """エージェント基底クラス"""
    
    def __init__(
        self,
        name: str,
        erc8004_id: int,
        payment_config: PaymentConfig,
        should_record_onchain: bool = False
    ):
        self.name = name
        self.erc8004_id = erc8004_id
        self.payment_config = payment_config
        self.should_record_onchain = should_record_onchain
    
    @abstractmethod
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        エージェントのメイン処理
        
        Args:
            input_data: 入力データ
            
        Returns:
            AgentResult: 実行結果
        """
        pass
    
    def calculate_cost(self, usage_metrics: Dict) -> int:
        """
        実行コストの計算
        
        Args:
            usage_metrics: 使用量メトリクス
                - data_rows: 処理したデータ行数（upto方式）
                - computation_time: 計算時間（upto方式）
                
        Returns:
            int: コスト（JPYC単位）
        """
        if self.payment_config.scheme == PaymentScheme.EXACT:
            return self.payment_config.base_amount
        
        elif self.payment_config.scheme == PaymentScheme.UPTO:
            variable_cost = (
                usage_metrics.get("data_rows", 0) * 
                self.payment_config.variable_rate
            )
            return int(self.payment_config.base_amount + variable_cost)
        
        elif self.payment_config.scheme == PaymentScheme.DEFERRED:
            # セッション終了時に計算
            return self.payment_config.base_amount
```

### 2.3 需要予測エージェント

```python
# agents/demand_forecast.py
import lightgbm as lgb
import pandas as pd
from typing import Dict
import aiohttp

class DemandForecastAgent(Agent):
    """需要予測エージェント"""
    
    def __init__(self):
        super().__init__(
            name="demand_forecast",
            erc8004_id=1001,
            payment_config=PaymentConfig(
                scheme=PaymentScheme.UPTO,
                base_amount=3,  # 3 JPYC
                variable_rate=0.02  # 0.02 JPYC/1000レコード
            ),
            should_record_onchain=False
        )
        self.model = self._load_model()
    
    def _load_model(self) -> lgb.Booster:
        """学習済みLightGBMモデルのロード"""
        return lgb.Booster(model_file='models/demand_forecast_v2.3.txt')
    
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        需要予測の実行
        
        Input:
            - product_sku: 商品SKU
            - store_id: 店舗ID
            
        Output:
            - predicted_demand: 予測販売数量
            - confidence_interval: 信頼区間 (lower, upper)
            - confidence: 信頼度スコア
        """
        start_time = time.time()
        
        # 1. 過去POSデータ取得
        pos_data = await self._fetch_pos_data(
            input_data["product_sku"],
            input_data["store_id"]
        )
        
        # 2. 気象データ取得
        weather_data = await self._fetch_weather_data(
            input_data["store_id"]
        )
        
        # 3. イベントカレンダー
        calendar_data = self._get_calendar_features()
        
        # 4. 特徴量エンジニアリング
        features = self._build_features(
            pos_data, weather_data, calendar_data
        )
        
        # 5. 予測実行
        prediction = self.model.predict(features)[0]
        
        # 6. 信頼区間算出（Quantile Regression）
        lower_bound = prediction * 0.91  # -9%
        upper_bound = prediction * 1.09  # +9%
        
        execution_time = time.time() - start_time
        
        # コスト計算
        cost = self.calculate_cost({
            "data_rows": len(pos_data)
        })
        
        return AgentResult(
            success=True,
            data={
                "predicted_demand": round(prediction),
                "confidence_interval": {
                    "lower": round(lower_bound),
                    "upper": round(upper_bound)
                },
                "features_used": features.columns.tolist()
            },
            confidence=0.92,  # MAPE 8.2% → 信頼度92%
            execution_time=execution_time,
            cost=cost
        )
    
    async def _fetch_pos_data(
        self, 
        product_sku: str, 
        store_id: str
    ) -> pd.DataFrame:
        """POSデータ取得（過去3年分）"""
        # PostgreSQLから取得
        query = """
            SELECT 
                date, 
                sales_quantity,
                price,
                day_of_week,
                is_holiday
            FROM pos_sales
            WHERE product_sku = %s
              AND store_id = %s
              AND date >= CURRENT_DATE - INTERVAL '3 years'
            ORDER BY date
        """
        # 実装省略
        pass
    
    async def _fetch_weather_data(self, store_id: str) -> Dict:
        """気象庁APIから天気予報取得"""
        # 店舗の緯度経度取得
        location = await self._get_store_location(store_id)
        
        # 気象庁API呼び出し
        async with aiohttp.ClientSession() as session:
            url = f"https://api.jma.go.jp/forecast?lat={location.lat}&lon={location.lon}"
            async with session.get(url) as response:
                data = await response.json()
                
        return {
            "temperature": data["temperature"],
            "precipitation_probability": data["precipitation"],
            "weather_code": data["weather_code"]
        }
```

### 2.4 在庫最適化エージェント

```python
# agents/inventory_optimizer.py
from scipy.optimize import minimize
import numpy as np

class InventoryOptimizerAgent(Agent):
    """在庫最適化エージェント（ニュースベンダーモデル）"""
    
    def __init__(self):
        super().__init__(
            name="inventory_optimizer",
            erc8004_id=1002,
            payment_config=PaymentConfig(
                scheme=PaymentScheme.EXACT,
                base_amount=15
            ),
            should_record_onchain=False
        )
    
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        在庫最適化の実行
        
        Input:
            - demand_forecast: 需要予測結果
            - supplier_quality: サプライヤー品質情報
            
        Output:
            - order_quantity: 推奨発注量
            - supplier: 推奨サプライヤー
            - order_timing: 発注タイミング
            - safety_stock: 安全在庫
        """
        start_time = time.time()
        
        # 需要予測値
        demand_mean = input_data["demand_forecast"]["data"]["predicted_demand"]
        demand_lower = input_data["demand_forecast"]["data"]["confidence_interval"]["lower"]
        demand_upper = input_data["demand_forecast"]["data"]["confidence_interval"]["upper"]
        
        # 現在在庫
        current_inventory = await self._get_current_inventory()
        
        # サプライヤー情報
        supplier = input_data["supplier_quality"]["data"]["recommended_supplier"]
        unit_cost = supplier["unit_price"]
        lead_time_hours = supplier["lead_time_hours"]
        
        # パラメータ
        selling_price = 198  # 円（価格エージェントから取得予定）
        disposal_cost = 120  # 円
        shortage_cost = selling_price - unit_cost  # 機会損失
        
        # ニュースベンダーモデル
        # Critical Ratio = (p - c) / (p - c + h)
        # p: 販売価格, c: 調達コスト, h: 廃棄コスト
        critical_ratio = shortage_cost / (shortage_cost + disposal_cost)
        
        # 正規分布を仮定してQuantileを計算
        from scipy.stats import norm
        demand_std = (demand_upper - demand_lower) / (2 * 1.96)  # 95%信頼区間
        optimal_order = norm.ppf(critical_ratio, loc=demand_mean, scale=demand_std)
        
        # 現在在庫を考慮
        order_quantity = max(0, int(optimal_order - current_inventory))
        
        # 発注タイミング（開店9時に間に合わせる）
        store_open_time = "09:00"
        order_time = self._calculate_order_time(store_open_time, lead_time_hours)
        
        # 安全在庫（1日分）
        safety_stock = int(demand_mean * 0.15)
        
        execution_time = time.time() - start_time
        
        return AgentResult(
            success=True,
            data={
                "order_quantity": order_quantity,
                "supplier": {
                    "id": supplier["id"],
                    "name": supplier["name"],
                    "unit_price": unit_cost
                },
                "order_timing": order_time,
                "safety_stock": safety_stock,
                "expected_waste": max(0, optimal_order - demand_mean),
                "expected_shortage": max(0, demand_mean - optimal_order)
            },
            confidence=0.89,
            execution_time=execution_time,
            cost=15
        )
```

### 2.5 サプライヤー品質検証エージェント（DID/VC統合）

```python
# agents/supplier_quality.py
import aiohttp
from typing import List

class SupplierQualityAgent(Agent):
    """サプライヤー品質検証エージェント"""
    
    def __init__(self, did_vc_client):
        super().__init__(
            name="supplier_quality",
            erc8004_id=1004,
            payment_config=PaymentConfig(
                scheme=PaymentScheme.EXACT,
                base_amount=8
            ),
            should_record_onchain=True  # 検証結果をオンチェーン記録
        )
        self.did_vc_client = did_vc_client
    
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        サプライヤー品質検証
        
        Input:
            - product_sku: 商品SKU
            
        Output:
            - suppliers: サプライヤーリスト（信頼度スコア付き）
            - recommended_supplier: 推奨サプライヤー
        """
        start_time = time.time()
        
        # サプライヤー候補取得
        suppliers = await self._get_suppliers(input_data["product_sku"])
        
        scored_suppliers = []
        for supplier in suppliers:
            # DID/VC検証
            vc_score = await self._verify_supplier_credentials(
                supplier["did"]
            )
            
            # 過去実績
            history_score = await self._evaluate_history(
                supplier["id"]
            )
            
            # 配送リスク
            delivery_score = await self._evaluate_delivery_risk(
                supplier["id"]
            )
            
            # 価格競争力
            price_score = self._evaluate_price_competitiveness(
                supplier["unit_price"]
            )
            
            # 総合スコア（重み付け平均）
            total_score = (
                vc_score * 0.4 +
                history_score * 0.3 +
                delivery_score * 0.2 +
                price_score * 0.1
            )
            
            scored_suppliers.append({
                **supplier,
                "trust_score": round(total_score, 2),
                "vc_verified": vc_score > 0.8,
                "scores": {
                    "credential": vc_score,
                    "history": history_score,
                    "delivery": delivery_score,
                    "price": price_score
                }
            })
        
        # スコア順にソート
        scored_suppliers.sort(key=lambda x: x["trust_score"], reverse=True)
        
        execution_time = time.time() - start_time
        
        return AgentResult(
            success=True,
            data={
                "suppliers": scored_suppliers,
                "recommended_supplier": scored_suppliers[0]
            },
            confidence=0.95,
            execution_time=execution_time,
            cost=8
        )
    
    async def _verify_supplier_credentials(self, supplier_did: str) -> float:
        """
        DID/VC基盤でサプライヤーの認証情報を検証
        
        Returns:
            float: 認証スコア（0.0〜1.0）
        """
        try:
            # DID/VCコンソーシアム基盤に問い合わせ
            verification_result = await self.did_vc_client.verify_credential(
                did=supplier_did,
                credential_types=["OrganicCertificate", "SupplierLicense"]
            )
            
            if not verification_result.valid:
                return 0.0
            
            # 証明書の有効期限チェック
            if verification_result.is_expired:
                return 0.5
            
            # 発行者の信頼度
            issuer_trust = self._get_issuer_trust_score(
                verification_result.issuer
            )
            
            return issuer_trust
            
        except Exception as e:
            logger.error(f"VC verification failed: {e}")
            return 0.0
```

### 2.6 総合検証エージェント

```python
# agents/validation.py
class ValidationAgent(Agent):
    """総合検証エージェント（A2A経済圏の要）"""
    
    def __init__(self):
        super().__init__(
            name="validation",
            erc8004_id=2001,
            payment_config=PaymentConfig(
                scheme=PaymentScheme.EXACT,
                base_amount=5
            ),
            should_record_onchain=True
        )
    
    async def execute(self, input_data: Dict) -> AgentResult:
        """
        全エージェント結果の整合性検証
        
        Input:
            - demand: 需要予測結果
            - inventory: 在庫最適化結果
            - price: 価格設定結果
            - quality: 品質検証結果
            
        Output:
            - validation_results: 検証項目ごとの結果
            - overall_confidence: 総合信頼度
            - warnings: 警告リスト
        """
        start_time = time.time()
        
        validations = []
        warnings = []
        
        # 検証1: 需要予測 vs 発注量 + 在庫
        demand_predicted = input_data["demand"]["data"]["predicted_demand"]
        order_qty = input_data["inventory"]["data"]["order_quantity"]
        current_inventory = 80  # TODO: 実データ取得
        
        total_available = order_qty + current_inventory
        demand_diff_pct = abs(total_available - demand_predicted) / demand_predicted
        
        validations.append({
            "check": "demand_inventory_consistency",
            "passed": demand_diff_pct <= 0.03,  # ±3%以内
            "details": {
                "demand": demand_predicted,
                "total_available": total_available,
                "diff_pct": round(demand_diff_pct * 100, 2)
            }
        })
        
        # 検証2: 価格設定 vs 粗利率目標
        price = input_data["price"]["data"]["base_price"]
        cost = input_data["inventory"]["data"]["supplier"]["unit_price"]
        gross_margin_pct = (price - cost) / price
        target_margin = 0.45  # 45%
        
        margin_check = gross_margin_pct >= target_margin * 0.95  # 目標の95%以上
        validations.append({
            "check": "gross_margin_target",
            "passed": margin_check,
            "details": {
                "price": price,
                "cost": cost,
                "margin_pct": round(gross_margin_pct * 100, 2),
                "target_pct": round(target_margin * 100, 2)
            }
        })
        
        if not margin_check:
            warnings.append("粗利率が目標未達。価格再設定を推奨")
        
        # 検証3: サプライヤー選定 vs 品質スコア
        supplier_score = input_data["quality"]["data"]["recommended_supplier"]["trust_score"]
        quality_threshold = 0.85
        
        validations.append({
            "check": "supplier_quality_threshold",
            "passed": supplier_score >= quality_threshold,
            "details": {
                "supplier_score": supplier_score,
                "threshold": quality_threshold
            }
        })
        
        # 検証4: 賞味期限 vs 販売期間
        shelf_life_days = 3
        predicted_sales_days = demand_predicted / (demand_predicted / 1.2)  # 簡易計算
        
        validations.append({
            "check": "shelf_life_adequacy",
            "passed": predicted_sales_days <= shelf_life_days * 0.8,
            "details": {
                "shelf_life_days": shelf_life_days,
                "predicted_sales_days": round(predicted_sales_days, 2)
            }
        })
        
        # 検証5: 天候リスク
        weather_risk = input_data["demand"]["data"].get("weather_risk", {})
        if weather_risk.get("precipitation_prob", 0) > 0.7:
            warnings.append("高降水確率による需要減退リスクあり")
        
        # 総合信頼度スコア
        passed_count = sum(1 for v in validations if v["passed"])
        overall_confidence = passed_count / len(validations)
        
        execution_time = time.time() - start_time
        
        return AgentResult(
            success=True,
            data={
                "validation_results": validations,
                "overall_confidence": round(overall_confidence, 2),
                "warnings": warnings,
                "all_checks_passed": all(v["passed"] for v in validations)
            },
            confidence=overall_confidence,
            execution_time=execution_time,
            cost=5
        )
```

---

## 3. データモデル

### 3.1 オンチェーンデータ（ERC-8004）

#### Identity Registry

```solidity
// contracts/src/ERC8004Identity.sol
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract ERC8004Identity is ERC721 {
    struct AgentMetadata {
        string name;
        string category;
        string vendor;
        string modelType;
        string metadataURI;  // IPFS URI
        uint256 registeredAt;
        address wallet;
    }
    
    mapping(uint256 => AgentMetadata) public agents;
    uint256 private _nextAgentId;
    
    event AgentRegistered(
        uint256 indexed agentId,
        string name,
        string category,
        address indexed wallet
    );
    
    event MetadataUpdated(
        uint256 indexed agentId,
        string key,
        string value
    );
    
    function register(
        string memory _name,
        string memory _category,
        string memory _metadataURI
    ) external returns (uint256) {
        uint256 agentId = _nextAgentId++;
        
        _safeMint(msg.sender, agentId);
        
        agents[agentId] = AgentMetadata({
            name: _name,
            category: _category,
            vendor: "",  // 後で設定可能
            modelType: "",
            metadataURI: _metadataURI,
            registeredAt: block.timestamp,
            wallet: msg.sender
        });
        
        emit AgentRegistered(agentId, _name, _category, msg.sender);
        
        return agentId;
    }
    
    function setAgentWallet(
        uint256 agentId,
        address newWallet,
        uint256 deadline,
        bytes memory signature
    ) external {
        require(ownerOf(agentId) == msg.sender, "Not owner");
        require(block.timestamp <= deadline, "Signature expired");
        
        // EIP-712署名検証（省略）
        
        agents[agentId].wallet = newWallet;
    }
    
    function getAgentMetadata(uint256 agentId) 
        external 
        view 
        returns (AgentMetadata memory) 
    {
        return agents[agentId];
    }
}
```

#### Reputation Registry

```solidity
// contracts/src/ERC8004Reputation.sol
pragma solidity ^0.8.20;

contract ERC8004Reputation {
    struct Feedback {
        address client;
        uint8 score;  // 0-100
        string[] tags;
        string reportURI;
        uint256 timestamp;
    }
    
    struct ReputationStats {
        uint256 totalFeedbacks;
        uint256 totalScore;
        uint8 averageScore;
        mapping(string => uint256) tagCounts;
    }
    
    mapping(uint256 => Feedback[]) public feedbacks;
    mapping(uint256 => ReputationStats) private stats;
    
    event FeedbackSubmitted(
        uint256 indexed agentId,
        address indexed client,
        uint8 score,
        string reportURI
    );
    
    function submitFeedback(
        uint256 agentId,
        uint8 score,
        string[] memory tags,
        string memory reportURI
    ) external {
        require(score <= 100, "Invalid score");
        
        feedbacks[agentId].push(Feedback({
            client: msg.sender,
            score: score,
            tags: tags,
            reportURI: reportURI,
            timestamp: block.timestamp
        }));
        
        ReputationStats storage agentStats = stats[agentId];
        agentStats.totalFeedbacks++;
        agentStats.totalScore += score;
        agentStats.averageScore = uint8(
            agentStats.totalScore / agentStats.totalFeedbacks
        );
        
        for (uint i = 0; i < tags.length; i++) {
            agentStats.tagCounts[tags[i]]++;
        }
        
        emit FeedbackSubmitted(agentId, msg.sender, score, reportURI);
    }
    
    function getAverageScore(uint256 agentId) 
        external 
        view 
        returns (uint8) 
    {
        return stats[agentId].averageScore;
    }
    
    function getFeedbackCount(uint256 agentId) 
        external 
        view 
        returns (uint256) 
    {
        return stats[agentId].totalFeedbacks;
    }
}
```

#### Validation Registry

```solidity
// contracts/src/ERC8004Validation.sol
pragma solidity ^0.8.20;

contract ERC8004Validation {
    struct ValidationRecord {
        uint256 validatorAgentId;
        bytes32 taskHash;
        bool result;
        uint8 confidenceScore;  // 0-100
        string proofURI;  // IPFS URI
        uint256 timestamp;
    }
    
    mapping(bytes32 => ValidationRecord[]) public validations;
    
    event ValidationRecorded(
        bytes32 indexed taskHash,
        uint256 indexed validatorAgentId,
        bool result,
        uint8 confidenceScore
    );
    
    function recordValidation(
        bytes32 taskHash,
        uint256 validatorAgentId,
        bool result,
        uint8 confidenceScore,
        string memory proofURI
    ) external {
        require(confidenceScore <= 100, "Invalid confidence score");
        
        validations[taskHash].push(ValidationRecord({
            validatorAgentId: validatorAgentId,
            taskHash: taskHash,
            result: result,
            confidenceScore: confidenceScore,
            proofURI: proofURI,
            timestamp: block.timestamp
        }));
        
        emit ValidationRecorded(
            taskHash,
            validatorAgentId,
            result,
            confidenceScore
        );
    }
    
    function getValidations(bytes32 taskHash) 
        external 
        view 
        returns (ValidationRecord[] memory) 
    {
        return validations[taskHash];
    }
    
    function getLatestValidation(bytes32 taskHash)
        external
        view
        returns (ValidationRecord memory)
    {
        ValidationRecord[] storage records = validations[taskHash];
        require(records.length > 0, "No validation found");
        return records[records.length - 1];
    }
}
```

### 3.2 オフチェーンデータ（PostgreSQL）

#### POSデータテーブル

```sql
-- POS販売データ
CREATE TABLE pos_sales (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    sales_quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    day_of_week INTEGER NOT NULL,  -- 0=月曜, 6=日曜
    is_holiday BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_product_store_date (product_sku, store_id, date),
    INDEX idx_date (date)
);

-- 店舗マスタ
CREATE TABLE stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(200) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    store_type VARCHAR(50),  -- 'flagship', 'standard', 'compact'
    chain VARCHAR(50),  -- 'existing', 'seiyu'
    opened_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品マスタ
CREATE TABLE products (
    product_sku VARCHAR(100) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,  -- '生鮮', '日配', '一般食品'
    subcategory VARCHAR(100),
    shelf_life_days INTEGER,  -- 賞味期限（日数）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- サプライヤーマスタ
CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    did VARCHAR(200) UNIQUE,  -- DID識別子
    unit_price DECIMAL(10, 2) NOT NULL,
    lead_time_hours INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- エージェント実行履歴
CREATE TABLE agent_executions (
    id BIGSERIAL PRIMARY KEY,
    execution_id UUID NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    agent_erc8004_id INTEGER,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    confidence DECIMAL(3, 2),
    execution_time DECIMAL(10, 3),  -- 秒
    cost INTEGER,  -- JPYC
    tx_hash VARCHAR(66),  -- ブロックチェーントランザクションハッシュ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_execution_id (execution_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_created_at (created_at)
);

-- 最適化タスク実行履歴
CREATE TABLE optimization_tasks (
    id BIGSERIAL PRIMARY KEY,
    execution_id UUID NOT NULL UNIQUE,
    product_sku VARCHAR(100) NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- 'pending', 'running', 'completed', 'failed'
    total_cost INTEGER,  -- 合計コスト（JPYC）
    validation_tx_hash VARCHAR(66),  -- 検証結果のTxハッシュ
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_scheduled_at (scheduled_at)
);
```

### 3.3 キャッシュデータ（Redis）

```python
# キャッシュキー設計
CACHE_KEYS = {
    # 需要予測結果（24時間キャッシュ）
    "demand_forecast": "df:{product_sku}:{store_id}:{date}",
    
    # サプライヤー品質スコア（1週間キャッシュ）
    "supplier_quality": "sq:{supplier_id}",
    
    # 気象データ（6時間キャッシュ）
    "weather": "weather:{store_id}:{date}",
    
    # エージェント実行セッション（1時間）
    "session": "session:{execution_id}",
}
```

---

## 4. プロトコル統合

### 4.1 X402決済フロー

```python
# protocols/x402_client.py
import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
import json

class X402Client:
    """X402 v2プロトコルクライアント"""
    
    def __init__(
        self,
        facilitator_url: str,
        payer_account: Account
    ):
        self.facilitator_url = facilitator_url
        self.payer_account = payer_account
        self.client = httpx.AsyncClient()
    
    async def pay_agent(
        self,
        agent_endpoint: str,
        payment_scheme: PaymentScheme,
        amount: int,
        input_data: Dict
    ) -> Dict:
        """
        エージェントへの支払いと実行
        
        Args:
            agent_endpoint: エージェントのエンドポイント
            payment_scheme: exact/upto/deferred
            amount: 支払額（JPYC単位）
            input_data: エージェントへの入力データ
            
        Returns:
            Dict: エージェントの実行結果
        """
        # Step 1: エージェントにリクエスト送信
        response = await self.client.post(
            agent_endpoint,
            json=input_data
        )
        
        # Step 2: 402 Payment Required を受信
        if response.status_code != 402:
            raise Exception(f"Expected 402, got {response.status_code}")
        
        payment_required_header = response.headers.get("PAYMENT-REQUIRED")
        payment_info = json.loads(payment_required_header)
        
        # Step 3: PaymentPayloadを作成
        payment_payload = {
            "facilitator": self.facilitator_url,
            "token": payment_info["token"],  # JPYCコントラクトアドレス
            "amount": str(amount),
            "scheme": payment_scheme.value,
            "nonce": payment_info["nonce"],
            "deadline": payment_info["deadline"]
        }
        
        # Step 4: PaymentPayloadに署名
        message = encode_defunct(text=json.dumps(payment_payload))
        signed_message = self.payer_account.sign_message(message)
        
        # Step 5: 署名付きでリトライ
        response = await self.client.post(
            agent_endpoint,
            json=input_data,
            headers={
                "PAYMENT-SIGNATURE": signed_message.signature.hex()
            }
        )
        
        # Step 6: 200 OK を受信し結果を取得
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Payment failed: {response.status_code}")
```

### 4.2 JPYC決済実装（EIP-3009）

```python
# protocols/jpyc_payment.py
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_structured_data

class JPYCPayment:
    """JPYCガスレス決済（EIP-3009）"""
    
    def __init__(
        self,
        web3: Web3,
        jpyc_address: str,
        relayer_account: Account
    ):
        self.web3 = web3
        self.jpyc_address = jpyc_address
        self.relayer_account = relayer_account
        
        # JPYCコントラクトABI（EIP-3009対応）
        with open("abis/JPYC.json") as f:
            self.jpyc_contract = web3.eth.contract(
                address=jpyc_address,
                abi=json.load(f)
            )
    
    def create_transfer_authorization(
        self,
        from_account: Account,
        to_address: str,
        value: int,
        valid_after: int = 0,
        valid_before: int = None
    ) -> Dict:
        """
        transferWithAuthorization用の署名を作成
        
        Args:
            from_account: 送信者アカウント
            to_address: 受信者アドレス
            value: 送金額（wei単位）
            valid_after: 有効開始時刻（Unix timestamp）
            valid_before: 有効終了時刻（Unix timestamp）
            
        Returns:
            Dict: v, r, s 署名
        """
        if valid_before is None:
            valid_before = int(time.time()) + 3600  # 1時間後
        
        # ノンス生成
        nonce = Web3.keccak(text=f"{from_account.address}{to_address}{value}{time.time()}")
        
        # EIP-712構造化データ
        domain = {
            "name": "JPY Coin",
            "version": "1",
            "chainId": self.web3.eth.chain_id,
            "verifyingContract": self.jpyc_address
        }
        
        types = {
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"}
            ]
        }
        
        message = {
            "from": from_account.address,
            "to": to_address,
            "value": value,
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce.hex()
        }
        
        # EIP-712署名
        signable_message = encode_structured_data(
            domain_data=domain,
            message_types=types,
            message_data=message
        )
        signed = from_account.sign_message(signable_message)
        
        return {
            "from": from_account.address,
            "to": to_address,
            "value": value,
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce.hex(),
            "v": signed.v,
            "r": signed.r.to_bytes(32, 'big').hex(),
            "s": signed.s.to_bytes(32, 'big').hex()
        }
    
    async def execute_transfer(self, authorization: Dict) -> str:
        """
        リレイヤーがtransferWithAuthorizationを実行
        
        Args:
            authorization: create_transfer_authorization()の戻り値
            
        Returns:
            str: トランザクションハッシュ
        """
        tx = self.jpyc_contract.functions.transferWithAuthorization(
            authorization["from"],
            authorization["to"],
            authorization["value"],
            authorization["validAfter"],
            authorization["validBefore"],
            bytes.fromhex(authorization["nonce"][2:]),  # 0xを除去
            int(authorization["v"]),
            bytes.fromhex(authorization["r"]),
            bytes.fromhex(authorization["s"])
        ).build_transaction({
            "from": self.relayer_account.address,
            "nonce": self.web3.eth.get_transaction_count(
                self.relayer_account.address
            ),
            "gas": 200000,
            "gasPrice": self.web3.eth.gas_price
        })
        
        # リレイヤーが署名・送信
        signed_tx = self.web3.eth.account.sign_transaction(
            tx,
            self.relayer_account.key
        )
        
        tx_hash = self.web3.eth.send_raw_transaction(
            signed_tx.rawTransaction
        )
        
        # トランザクション確認待機
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_hash.hex()
```

---

## 5. API設計

### 5.1 REST API エンドポイント

```python
# api/routes.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="A2A Supply Chain Optimization API")

# リクエストモデル
class OptimizationRequest(BaseModel):
    product_sku: str
    store_id: str
    scheduled_at: Optional[str] = None  # ISO 8601形式

class OptimizationResponse(BaseModel):
    execution_id: str
    status: str
    message: str

# エンドポイント定義
@app.post("/api/v1/optimize", response_model=OptimizationResponse)
async def create_optimization_task(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    最適化タスクの作成
    
    - **product_sku**: 商品SKU
    - **store_id**: 店舗ID
    - **scheduled_at**: 実行予定時刻（省略時は即時実行）
    """
    execution_id = str(uuid.uuid4())
    
    # 非同期タスクをキューに追加
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

@app.get("/api/v1/optimize/{execution_id}")
async def get_optimization_result(execution_id: str):
    """
    最適化結果の取得
    
    - **execution_id**: 実行ID
    """
    # PostgreSQLから取得
    result = await db.get_optimization_task(execution_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "execution_id": execution_id,
        "status": result.status,
        "product_sku": result.product_sku,
        "store_id": result.store_id,
        "total_cost": result.total_cost,
        "report": result.report_data,
        "validation_tx": result.validation_tx_hash,
        "created_at": result.created_at.isoformat(),
        "completed_at": result.completed_at.isoformat() if result.completed_at else None
    }

@app.get("/api/v1/agents/{agent_id}/reputation")
async def get_agent_reputation(agent_id: int):
    """
    エージェントのReputation取得
    
    - **agent_id**: ERC-8004エージェントID
    """
    # ERC-8004 Reputation Registryから取得
    reputation = await blockchain_service.get_agent_reputation(agent_id)
    
    return {
        "agent_id": agent_id,
        "average_score": reputation.average_score,
        "feedback_count": reputation.feedback_count,
        "top_tags": reputation.top_tags
    }
```

### 5.2 エージェント間通信（Internal API）

```python
# エージェント間のメッセージフォーマット（JSON）
{
    "message_id": "uuid",
    "from_agent": "demand_forecast",
    "to_agent": "inventory_optimizer",
    "timestamp": "2025-01-24T02:00:15Z",
    "payload": {
        "predicted_demand": 350,
        "confidence_interval": {
            "lower": 320,
            "upper": 380
        },
        "confidence": 0.92
    },
    "metadata": {
        "execution_id": "uuid",
        "cost_jpyc": 10
    }
}
```

---

## 6. セキュリティ

### 6.1 認証・認可

**API認証**:
- Bearer Token（JWT）
- API Key（外部パートナー用）

**エージェント認証**:
- ERC-8004 Identity Registryによる一意性保証
- ウォレット署名による所有権証明

**DID/VC検証**:
- 既存コンソーシアム基盤との連携
- VCの署名検証（Issuerの公開鍵）
- 有効期限チェック

### 6.2 データ保護

**PII（個人情報）**:
- PostgreSQLの暗号化カラム（pgcrypto）
- アクセスログの記録

**秘密鍵管理**:
- AWS Secrets Manager / HashiCorp Vault
- ローカル開発時は.envファイル（.gitignore必須）

**通信暗号化**:
- HTTPS/TLS 1.3
- WebSocket over TLS

### 6.3 スマートコントラクトセキュリティ

**監査**:
- Slither静的解析
- Mythril脆弱性スキャン
- 外部監査（Phase 4）

**アクセス制御**:
```solidity
// Ownable/AccessControlの活用
import "@openzeppelin/contracts/access/Ownable.sol";

contract ERC8004Identity is ERC721, Ownable {
    function adminFunction() external onlyOwner {
        // 管理者のみ実行可能
    }
}
```

---

## 7. パフォーマンス要件

### 7.1 レスポンスタイム

| エンドポイント | 目標レスポンスタイム | 最大許容時間 |
|--------------|-------------------|-------------|
| POST /api/v1/optimize | 200ms（非同期キュー登録） | 500ms |
| GET /api/v1/optimize/{id} | 100ms | 300ms |
| エージェント実行全体 | 45秒 | 60秒 |
| 需要予測エージェント | 8秒 | 15秒 |
| 在庫最適化エージェント | 5秒 | 10秒 |
| 価格設定エージェント | 6秒 | 12秒 |

### 7.2 スループット

- 同時実行タスク数: 100タスク/分
- ピーク時（深夜2-3時）: 300タスク/分
- データベースコネクションプール: 50接続

### 7.3 スケーラビリティ

**水平スケーリング**:
- Kubernetes Pod Auto-scaling
- エージェントサービスのステートレス設計
- RabbitMQによるタスク分散

**垂直スケーリング**:
- ML推論サーバーのGPU対応（Phase 4）

---

## 8. 開発環境

### 8.1 ローカル開発セットアップ

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd a2a-supply-chain-project

# 2. Python仮想環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Foundryインストール
curl -L https://foundry.paradigm.xyz | bash
foundryup

# 4. 環境変数設定
cp .env.example .env
# .envを編集（データベース接続情報、秘密鍵等）

# 5. ローカルチェーン起動
anvil

# 6. スマートコントラクトデプロイ（別ターミナル）
cd contracts
forge build
forge script script/Deploy.s.sol --rpc-url http://127.0.0.1:8545 --broadcast

# 7. データベース初期化
psql -U postgres -f db/schema.sql
python scripts/seed_data.py

# 8. アプリケーション起動
cd python
uvicorn api.main:app --reload --port 8000
```

### 8.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: a2a_supply_chain
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/schema.sql:/docker-entrypoint-initdb.d/schema.sql
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"  # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
  
  anvil:
    image: ghcr.io/foundry-rs/foundry:latest
    command: anvil --host 0.0.0.0
    ports:
      - "8545:8545"
  
  app:
    build: ./python
    depends_on:
      - postgres
      - redis
      - rabbitmq
      - anvil
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/a2a_supply_chain
      REDIS_URL: redis://redis:6379
      RABBITMQ_URL: amqp://admin:password@rabbitmq:5672
      ANVIL_RPC_URL: http://anvil:8545
    volumes:
      - ./python:/app

volumes:
  postgres_data:
```

### 8.3 開発ツール

**コードフォーマット**:
```bash
# Python
black python/
isort python/
flake8 python/

# Solidity
forge fmt
```

**テスト実行**:
```bash
# Pythonテスト
pytest python/tests/ -v --cov

# Solidityテスト
forge test -vv
```

**静的解析**:
```bash
# Python
mypy python/
bandit -r python/

# Solidity
slither contracts/src/
```

---

## 9. デプロイメント

### 9.1 環境構成

| 環境 | ブロックチェーン | 用途 |
|------|----------------|------|
| **Local** | Anvil | 開発・単体テスト |
| **Staging** | Sepolia testnet | 統合テスト・検証 |
| **Production** | Polygon Mainnet | 本番運用 |

### 9.2 CI/CDパイプライン

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Foundry
        uses: foundry-rs/foundry-toolchain@v1
      - name: Run tests
        run: forge test -vv
      - name: Static analysis
        run: slither contracts/src/
  
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest python/tests/ --cov
  
  deploy-staging:
    needs: [test-contracts, test-python]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Sepolia
        run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.SEPOLIA_RPC_URL }} \
            --private-key ${{ secrets.DEPLOYER_PRIVATE_KEY }} \
            --broadcast --verify
```

---

## 10. 監視・運用

### 10.1 メトリクス収集

**Prometheus設定**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'a2a-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**主要メトリクス**:
- `optimization_task_duration_seconds`: タスク実行時間
- `agent_execution_count`: エージェント実行回数
- `agent_cost_jpyc_total`: エージェントコスト累計
- `blockchain_tx_count`: トランザクション数
- `database_query_duration_seconds`: DB クエリ時間

### 10.2 ログ管理

```python
# utils/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = 'a2a-supply-chain'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

# ロガー設定
logger = logging.getLogger('a2a')
handler = logging.StreamHandler()
handler.setFormatter(CustomJsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 10.3 アラート設定

**Grafana Alert Rules**:
- エージェント実行失敗率 > 5%
- API レスポンスタイム > 1秒（P95）
- ブロックチェーントランザクション失敗
- データベース接続プールの枯渇

---

## 11. 今後の拡張

### 11.1 Phase 4以降の計画

- **マルチチェーン対応**: Ethereum、Avalanche等
- **高度なML**: Transformer モデルによる需要予測
- **リアルタイム分析**: Apache Kafkaによるストリーム処理
- **モバイルアプリ**: バイヤー向けネイティブアプリ

### 11.2 機能追加候補

- **A/Bテスト機能**: 複数のエージェント戦略を比較
- **異常検知**: 需要急変・サプライチェーン混乱の早期検知
- **自動再発注**: 検証結果に基づく自動発注実行

---

## 12. 付録

### 12.1 技術用語集

- **Facilitator**: X402プロトコルで決済仲介を行うサービス
- **Newsvendor Model**: 需要不確実性下の在庫最適化モデル
- **EIP-3009**: イーサリアム改善提案、transferWithAuthorizationによるガスレス決済
- **MAPE**: Mean Absolute Percentage Error、予測精度の指標

### 12.2 参考資料

- [X402 Specification](https://x402.org)
- [ERC-8004 Draft](https://eips.ethereum.org/EIPS/eip-8004)
- [JPYC Developer Docs](https://jpyc.gitbook.io)
- [Foundry Book](https://book.getfoundry.sh)

---

**最終更新**: 2025-01-22  
**次回レビュー予定**: Phase 1完了時