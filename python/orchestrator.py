"""
Orchestrator - エージェント協調制御

複数のエージェントを協調させてタスクを実行する。
"""
import logging
import time
from typing import Dict, Any
from dataclasses import dataclass

from agents.demand_forecast import DemandForecastAgent
from agents.inventory_optimizer import InventoryOptimizerAgent

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """最適化タスク結果"""

    success: bool
    product_sku: str
    store_id: str
    demand_forecast: Dict[str, Any]
    inventory_optimization: Dict[str, Any]
    total_cost: int  # JPYC
    total_execution_time: float  # 秒
    summary: Dict[str, Any]
    error_message: str = ""


class AgentCoordinator:
    """エージェント協調制御"""

    def __init__(self, db_session):
        """
        Args:
            db_session: データベースセッション
        """
        self.db_session = db_session
        self.demand_forecast_agent = DemandForecastAgent(db_session)
        self.inventory_optimizer_agent = InventoryOptimizerAgent(db_session)
        logger.info("AgentCoordinator initialized")

    async def execute_optimization_task(
        self, product_sku: str, store_id: str
    ) -> OptimizationResult:
        """
        最適化タスクの実行

        Args:
            product_sku: 商品SKU
            store_id: 店舗ID

        Returns:
            OptimizationResult: 最適化結果
        """
        start_time = time.time()
        logger.info(f"=== Starting optimization task: {product_sku} @ {store_id} ===")

        try:
            # Phase 1: 需要予測
            logger.info("Phase 1: Demand Forecasting")
            demand_result = await self.demand_forecast_agent.execute(
                {"product_sku": product_sku, "store_id": store_id}
            )

            if not demand_result.success:
                logger.error(f"Demand forecast failed: {demand_result.error_message}")
                return OptimizationResult(
                    success=False,
                    product_sku=product_sku,
                    store_id=store_id,
                    demand_forecast={},
                    inventory_optimization={},
                    total_cost=0,
                    total_execution_time=time.time() - start_time,
                    summary={},
                    error_message=f"Demand forecast failed: {demand_result.error_message}",
                )

            # Phase 2: 在庫最適化
            logger.info("Phase 2: Inventory Optimization")
            inventory_result = await self.inventory_optimizer_agent.execute(
                {
                    "demand_forecast": demand_result.__dict__,
                    "product_sku": product_sku,
                    "store_id": store_id,
                }
            )

            if not inventory_result.success:
                logger.error(
                    f"Inventory optimization failed: {inventory_result.error_message}"
                )
                return OptimizationResult(
                    success=False,
                    product_sku=product_sku,
                    store_id=store_id,
                    demand_forecast=demand_result.__dict__,
                    inventory_optimization={},
                    total_cost=demand_result.cost,
                    total_execution_time=time.time() - start_time,
                    summary={},
                    error_message=f"Inventory optimization failed: {inventory_result.error_message}",
                )

            # 合計コスト・実行時間
            total_cost = demand_result.cost + inventory_result.cost
            total_execution_time = time.time() - start_time

            # サマリー生成
            summary = self._generate_summary(demand_result, inventory_result)

            logger.info(f"=== Optimization completed: {total_cost} JPYC ===")

            return OptimizationResult(
                success=True,
                product_sku=product_sku,
                store_id=store_id,
                demand_forecast=demand_result.__dict__,
                inventory_optimization=inventory_result.__dict__,
                total_cost=total_cost,
                total_execution_time=total_execution_time,
                summary=summary,
            )

        except Exception as e:
            logger.error(f"Optimization task failed: {e}")
            return OptimizationResult(
                success=False,
                product_sku=product_sku,
                store_id=store_id,
                demand_forecast={},
                inventory_optimization={},
                total_cost=0,
                total_execution_time=time.time() - start_time,
                summary={},
                error_message=str(e),
            )

    def _generate_summary(
        self, demand_result, inventory_result
    ) -> Dict[str, Any]:
        """
        サマリー生成

        Args:
            demand_result: 需要予測結果
            inventory_result: 在庫最適化結果

        Returns:
            Dict: サマリー
        """
        return {
            "predicted_demand": demand_result.data["predicted_demand"],
            "recommended_order": inventory_result.data["order_quantity"],
            "supplier": inventory_result.data["supplier"]["name"],
            "unit_cost": inventory_result.data["supplier"]["unit_price"],
            "total_cost_jpyc": demand_result.cost + inventory_result.cost,
            "confidence": {
                "demand": demand_result.confidence,
                "inventory": inventory_result.confidence,
                "overall": (demand_result.confidence + inventory_result.confidence)
                / 2,
            },
            "expected_waste": inventory_result.data["expected_waste"],
            "expected_shortage": inventory_result.data["expected_shortage"],
        }
