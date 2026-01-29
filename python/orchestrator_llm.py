"""
LLMエージェントオーケストレータ

CrewAIエージェントとX402決済を統合したサプライチェーン最適化オーケストレータ
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from protocols.x402 import (
    PaymentScheme,
    X402Client,
    X402Request,
    X402Response,
    X402Transaction,
)
from protocols.x402.models import jpyc_to_wei, wei_to_jpyc

# CrewAI imports - optional, only needed for real LLM execution
try:
    from crewai import Crew
    from agents.llm import (
        create_demand_forecast_agent,
        create_inventory_optimizer_agent,
        create_report_generator_agent,
    )
    from agents.llm.demand_forecast_llm import create_demand_forecast_task
    from agents.llm.inventory_optimizer_llm import create_inventory_optimization_task
    from agents.llm.report_generator_llm import create_report_generation_task
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


logger = logging.getLogger(__name__)


class AgentConfig:
    """エージェント設定"""

    def __init__(
        self,
        agent_id: int,
        agent_name: str,
        payment_scheme: PaymentScheme,
        base_cost_jpyc: float,
        max_cost_jpyc: Optional[float] = None,
        payment_address: str = None,
        cost_per_1000_records: float = 0.0
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.payment_scheme = payment_scheme
        self.base_cost_jpyc = base_cost_jpyc
        self.max_cost_jpyc = max_cost_jpyc
        self.payment_address = payment_address or f"0xAgent{agent_id:040x}"
        self.cost_per_1000_records = cost_per_1000_records


class SupplyChainOrchestrator:
    """
    サプライチェーン最適化オーケストレータ

    LLMエージェント（CrewAI）とX402決済を統合し、
    需要予測 → 在庫最適化 → レポート生成の協調フローを管理
    """

    def __init__(self, client_agent_id: int = 0):
        """
        初期化

        Args:
            client_agent_id: クライアント（店舗）エージェントID
        """
        self.client_agent_id = client_agent_id
        self.x402_client = X402Client(client_agent_id=client_agent_id)

        # エージェント設定
        self.agent_configs = {
            "demand_forecast": AgentConfig(
                agent_id=1,
                agent_name="需要予測エージェント",
                payment_scheme=PaymentScheme.UPTO,
                base_cost_jpyc=3.0,
                max_cost_jpyc=10.0,
                payment_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                cost_per_1000_records=0.02
            ),
            "inventory_optimizer": AgentConfig(
                agent_id=2,
                agent_name="在庫最適化エージェント",
                payment_scheme=PaymentScheme.EXACT,
                base_cost_jpyc=15.0,
                payment_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
            ),
            "report_generator": AgentConfig(
                agent_id=3,
                agent_name="レポート生成エージェント",
                payment_scheme=PaymentScheme.DEFERRED,
                base_cost_jpyc=5.0,
                payment_address="0x90F79bf6EB2c4f870365E785982E1f101E93b906"
            )
        }

        logger.info(f"SupplyChainOrchestrator initialized for client agent {client_agent_id}")

    def execute_optimization(
        self,
        product_sku: str,
        product_name: str,
        product_category: str,
        store_name: str,
        weather: str,
        day_type: str,
        selling_price: float,
        disposal_cost: float = 120.0,
        shortage_cost: float = 80.0,
        use_real_llm: bool = False
    ) -> Dict[str, Any]:
        """
        サプライチェーン最適化を実行

        Args:
            product_sku: 商品SKU
            product_name: 商品名
            product_category: 商品カテゴリ
            store_name: 店舗名
            weather: 明日の天気
            day_type: 明日のタイプ（平日/週末）
            selling_price: 販売単価
            disposal_cost: 廃棄コスト
            shortage_cost: 機会損失コスト
            use_real_llm: 実際のLLMを使用するか（Falseならモック）

        Returns:
            最適化結果と決済情報
        """
        logger.info(f"Starting optimization for {product_name} at {store_name}")
        print("\n" + "=" * 70)
        print(f"🏪 サプライチェーン最適化実行: {store_name} - {product_name}")
        print("=" * 70)

        results = {
            "store_name": store_name,
            "product_name": product_name,
            "product_sku": product_sku,
            "weather": weather,
            "day_type": day_type,
            "transactions": [],
            "total_cost_jpyc": 0.0,
            "execution_time_ms": 0,
            "timestamp": datetime.now().isoformat()
        }

        start_time = datetime.now()

        # 実LLM使用時にCrewAI利用可能性をチェック
        if use_real_llm and not CREWAI_AVAILABLE:
            raise RuntimeError(
                "CrewAI is not available. Install required packages: "
                "pip install crewai langchain langchain-ollama"
            )

        try:
            # Phase 1: 需要予測
            demand_result, demand_tx = self._execute_demand_forecast(
                product_sku=product_sku,
                product_name=product_name,
                weather=weather,
                day_type=day_type,
                use_real_llm=use_real_llm
            )
            results["demand_forecast"] = demand_result
            results["transactions"].append(demand_tx)

            # Phase 2: 在庫最適化
            inventory_result, inventory_tx = self._execute_inventory_optimization(
                product_category=product_category,
                product_name=product_name,
                demand_forecast=demand_result,
                selling_price=selling_price,
                disposal_cost=disposal_cost,
                shortage_cost=shortage_cost,
                use_real_llm=use_real_llm
            )
            results["inventory_optimization"] = inventory_result
            results["transactions"].append(inventory_tx)

            # Phase 3: レポート生成
            report_result, report_tx = self._execute_report_generation(
                store_name=store_name,
                product_name=product_name,
                demand_result=demand_result,
                inventory_result=inventory_result,
                use_real_llm=use_real_llm
            )
            results["report"] = report_result
            results["transactions"].append(report_tx)

            # 総コスト計算
            total_cost = sum(wei_to_jpyc(tx.amount) for tx in results["transactions"])
            results["total_cost_jpyc"] = total_cost

            # 実行時間計算
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            results["execution_time_ms"] = execution_time

            # サマリー表示
            self._print_summary(results)

            logger.info(f"Optimization completed successfully in {execution_time:.0f}ms")
            return results

        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            results["error"] = str(e)
            raise

    def _execute_demand_forecast(
        self,
        product_sku: str,
        product_name: str,
        weather: str,
        day_type: str,
        use_real_llm: bool
    ) -> tuple[Dict[str, Any], X402Transaction]:
        """需要予測フェーズを実行"""
        print("\n" + "-" * 70)
        print("📈 Phase 1: 需要予測")
        print("-" * 70)

        config = self.agent_configs["demand_forecast"]

        # X402リクエスト作成
        request = self.x402_client.create_request(
            service_agent_id=config.agent_id,
            service_description=f"{product_name}の需要予測",
            payment_scheme=config.payment_scheme,
            base_amount_jpyc=config.base_cost_jpyc,
            max_amount_jpyc=config.max_cost_jpyc,
            metadata={
                "product_sku": product_sku,
                "weather": weather,
                "day_type": day_type
            }
        )

        print(f"✓ X402リクエスト作成: {request.request_id}")

        # エージェント実行
        if use_real_llm:
            # 実際のLLMエージェントを使用
            result, usage_metrics = self._run_demand_forecast_llm(
                product_sku, weather, day_type
            )
        else:
            # モック実行（Phase 3デフォルト）
            result, usage_metrics = self._mock_demand_forecast(
                product_sku, weather, day_type
            )

        print(f"✓ エージェント実行完了")
        print(f"  予測需要: {result['predicted_demand']}個")
        print(f"  信頼区間: [{result['confidence_interval'][0]}, {result['confidence_interval'][1]}]")

        # 実際のコスト計算（従量課金）
        records_processed = usage_metrics.get("records_processed", 2000)
        actual_cost = config.base_cost_jpyc + (records_processed / 1000) * config.cost_per_1000_records

        # X402レスポンス作成
        response = X402Response(
            request_id=request.request_id,
            response_id=f"res-demand-{request.request_id[4:12]}",
            status="success",
            result=result,
            actual_amount=jpyc_to_wei(actual_cost),
            payment_address=config.payment_address,
            execution_time_ms=usage_metrics.get("execution_time_ms", 1200),
            usage_metrics=usage_metrics
        )

        # 決済実行
        transaction = self.x402_client.process_response(request, response)

        print(f"✓ 決済完了: {wei_to_jpyc(transaction.amount):.2f} JPYC (TX: {transaction.tx_hash})")

        return result, transaction

    def _execute_inventory_optimization(
        self,
        product_category: str,
        product_name: str,
        demand_forecast: Dict[str, Any],
        selling_price: float,
        disposal_cost: float,
        shortage_cost: float,
        use_real_llm: bool
    ) -> tuple[Dict[str, Any], X402Transaction]:
        """在庫最適化フェーズを実行"""
        print("\n" + "-" * 70)
        print("📦 Phase 2: 在庫最適化")
        print("-" * 70)

        config = self.agent_configs["inventory_optimizer"]

        # X402リクエスト作成
        request = self.x402_client.create_request(
            service_agent_id=config.agent_id,
            service_description=f"{product_name}の在庫最適化",
            payment_scheme=config.payment_scheme,
            base_amount_jpyc=config.base_cost_jpyc,
            metadata={
                "product_category": product_category,
                "demand_forecast": demand_forecast,
                "selling_price": selling_price
            }
        )

        print(f"✓ X402リクエスト作成: {request.request_id}")

        # エージェント実行
        if use_real_llm:
            # 実際のLLMエージェントを使用
            result, usage_metrics = self._run_inventory_optimizer_llm(
                product_category, selling_price, disposal_cost, shortage_cost, demand_forecast
            )
        else:
            # モック実行
            result, usage_metrics = self._mock_inventory_optimization(
                demand_forecast, selling_price
            )

        print(f"✓ エージェント実行完了")
        print(f"  最適発注量: {result['optimal_order_quantity']}個")
        print(f"  期待利益: {result['expected_profit']:,}円")

        # 実際のコスト（EXACT: 固定料金）
        actual_cost = config.base_cost_jpyc

        # X402レスポンス作成
        response = X402Response(
            request_id=request.request_id,
            response_id=f"res-inventory-{request.request_id[4:12]}",
            status="success",
            result=result,
            actual_amount=jpyc_to_wei(actual_cost),
            payment_address=config.payment_address,
            execution_time_ms=usage_metrics.get("execution_time_ms", 500)
        )

        # 決済実行
        transaction = self.x402_client.process_response(request, response)

        print(f"✓ 決済完了: {wei_to_jpyc(transaction.amount):.2f} JPYC (TX: {transaction.tx_hash})")

        return result, transaction

    def _execute_report_generation(
        self,
        store_name: str,
        product_name: str,
        demand_result: Dict[str, Any],
        inventory_result: Dict[str, Any],
        use_real_llm: bool
    ) -> tuple[Dict[str, Any], X402Transaction]:
        """レポート生成フェーズを実行"""
        print("\n" + "-" * 70)
        print("📄 Phase 3: レポート生成")
        print("-" * 70)

        config = self.agent_configs["report_generator"]

        # X402リクエスト作成
        request = self.x402_client.create_request(
            service_agent_id=config.agent_id,
            service_description=f"{store_name} {product_name}最適化レポート",
            payment_scheme=config.payment_scheme,
            base_amount_jpyc=config.base_cost_jpyc,
            metadata={
                "store_name": store_name,
                "product_name": product_name
            }
        )

        print(f"✓ X402リクエスト作成: {request.request_id}")

        # エージェント実行
        if use_real_llm:
            # 実際のLLMエージェントを使用
            result, usage_metrics = self._run_report_generator_llm(
                store_name, product_name, demand_result, inventory_result
            )
        else:
            # モック実行
            result, usage_metrics = self._mock_report_generation(
                store_name, product_name, demand_result, inventory_result
            )

        print(f"✓ エージェント実行完了")
        print(f"  レポート: {result['report_summary']}")

        # 実際のコスト（DEFERRED: 後払い固定）
        actual_cost = config.base_cost_jpyc

        # X402レスポンス作成
        response = X402Response(
            request_id=request.request_id,
            response_id=f"res-report-{request.request_id[4:12]}",
            status="success",
            result=result,
            actual_amount=jpyc_to_wei(actual_cost),
            payment_address=config.payment_address,
            execution_time_ms=usage_metrics.get("execution_time_ms", 800)
        )

        # 決済実行
        transaction = self.x402_client.process_response(request, response)

        print(f"✓ 決済完了: {wei_to_jpyc(transaction.amount):.2f} JPYC (TX: {transaction.tx_hash})")

        return result, transaction

    # モック実装（Phase 3デフォルト）
    def _mock_demand_forecast(self, product_sku: str, weather: str, day_type: str):
        """需要予測モック"""
        return {
            "predicted_demand": 340,
            "confidence_interval": [325, 355],
            "std_dev": 15,
            "trend": "stable",
            "weather_factor": weather,
            "day_type_factor": day_type
        }, {"records_processed": 2000, "execution_time_ms": 1200}

    def _mock_inventory_optimization(self, demand_forecast: Dict, selling_price: float):
        """在庫最適化モック"""
        return {
            "optimal_order_quantity": demand_forecast["predicted_demand"],
            "expected_profit": 12500,
            "selected_supplier": "サプライヤーA",
            "supplier_quality_score": 95,
            "unit_cost": selling_price * 0.6
        }, {"execution_time_ms": 500}

    def _mock_report_generation(
        self, store_name: str, product_name: str, demand_result: Dict, inventory_result: Dict
    ):
        """レポート生成モック"""
        return {
            "report_summary": f"{store_name} {product_name}最適化レポート",
            "sections": {
                "demand_forecast": f"予測需要: {demand_result['predicted_demand']}個",
                "inventory_optimization": f"最適発注量: {inventory_result['optimal_order_quantity']}個",
                "expected_profit": f"期待利益: {inventory_result['expected_profit']:,}円"
            }
        }, {"execution_time_ms": 800}

    # 実LLM実装（Phase 3では動作確認のみ、Phase 4で本格利用）
    def _run_demand_forecast_llm(self, product_sku: str, weather: str, day_type: str):
        """実際のLLM需要予測エージェント実行"""
        raise NotImplementedError("Real LLM execution will be implemented in integration test")

    def _run_inventory_optimizer_llm(
        self, product_category: str, selling_price: float,
        disposal_cost: float, shortage_cost: float, demand_forecast: Dict
    ):
        """実際のLLM在庫最適化エージェント実行"""
        raise NotImplementedError("Real LLM execution will be implemented in integration test")

    def _run_report_generator_llm(
        self, store_name: str, product_name: str, demand_result: Dict, inventory_result: Dict
    ):
        """実際のLLMレポート生成エージェント実行"""
        raise NotImplementedError("Real LLM execution will be implemented in integration test")

    def _print_summary(self, results: Dict[str, Any]):
        """結果サマリーを表示"""
        print("\n" + "=" * 70)
        print("📊 最適化結果サマリー")
        print("=" * 70)

        print(f"\n🏪 店舗: {results['store_name']}")
        print(f"🍅 商品: {results['product_name']} ({results['product_sku']})")
        print(f"🌤️  天気: {results['weather']} ({results['day_type']})")

        print(f"\n📈 需要予測:")
        df = results["demand_forecast"]
        print(f"   予測需要: {df['predicted_demand']}個")
        print(f"   信頼区間: [{df['confidence_interval'][0]}, {df['confidence_interval'][1]}]")
        print(f"   標準偏差: {df['std_dev']}個")

        print(f"\n📦 在庫最適化:")
        io = results["inventory_optimization"]
        print(f"   最適発注量: {io['optimal_order_quantity']}個")
        print(f"   期待利益: {io['expected_profit']:,}円")
        print(f"   選定サプライヤー: {io['selected_supplier']}")

        print(f"\n💰 決済サマリー:")
        for i, tx in enumerate(results["transactions"], 1):
            print(f"   {i}. {wei_to_jpyc(tx.amount):.2f} JPYC ({tx.payment_scheme.value})")

        print(f"\n   総コスト: {results['total_cost_jpyc']:.2f} JPYC")
        print(f"   実行時間: {results['execution_time_ms']:.0f}ms")

    def get_payment_summary(self) -> Dict[str, Any]:
        """決済サマリーを取得"""
        return self.x402_client.get_transaction_summary()
