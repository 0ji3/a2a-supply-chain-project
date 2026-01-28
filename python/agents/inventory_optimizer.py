"""
在庫最適化エージェント

ニュースベンダーモデルで最適発注量を計算する。
"""
import time
import logging
from typing import Dict, Any
from scipy.stats import norm
from sqlalchemy import text

from .base import Agent, AgentResult, PaymentScheme, PaymentConfig

logger = logging.getLogger(__name__)


class InventoryOptimizerAgent(Agent):
    """在庫最適化エージェント"""

    def __init__(self, db_session):
        """
        Args:
            db_session: データベースセッション
        """
        super().__init__(
            name="inventory_optimizer",
            payment_config=PaymentConfig(
                scheme=PaymentScheme.EXACT,
                base_amount=15,  # 15 JPYC
            ),
        )
        self.db_session = db_session

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        在庫最適化の実行

        Args:
            input_data:
                - demand_forecast: 需要予測結果
                - product_sku: 商品SKU
                - store_id: 店舗ID

        Returns:
            AgentResult: 最適化結果
        """
        start_time = time.time()

        try:
            demand_forecast = input_data["demand_forecast"]
            product_sku = input_data.get("product_sku", "tomato-medium-domestic")

            logger.info(f"[{self.name}] Starting inventory optimization")

            # 需要予測値
            demand_mean = float(demand_forecast["data"]["predicted_demand"])
            demand_lower = float(demand_forecast["data"]["confidence_interval"]["lower"])
            demand_upper = float(demand_forecast["data"]["confidence_interval"]["upper"])

            # 標準偏差を推定（95%信頼区間から）
            demand_std = float((demand_upper - demand_lower) / (2 * 1.96))

            # サプライヤー情報取得
            supplier = self._get_best_supplier()

            # パラメータ
            selling_price = 198.0  # 円
            unit_cost = float(supplier["unit_price"])
            disposal_cost = 120.0  # 円（廃棄コスト）
            shortage_cost = selling_price - unit_cost  # 機会損失

            # ニュースベンダーモデル
            # Critical Ratio = (p - c) / (p - c + h)
            critical_ratio = float(shortage_cost / (shortage_cost + disposal_cost))

            # 最適発注量（正規分布を仮定）
            optimal_order = norm.ppf(critical_ratio, loc=demand_mean, scale=demand_std)

            # 現在在庫（仮）
            current_inventory = 80  # TODO: 実データ取得

            # 発注量
            order_quantity = max(0, int(optimal_order - current_inventory))

            # 安全在庫
            safety_stock = int(demand_mean * 0.15)

            # 期待廃棄量・欠品量
            expected_waste = max(0, int(optimal_order - demand_mean))
            expected_shortage = max(0, int(demand_mean - optimal_order))

            execution_time = time.time() - start_time
            cost = self.calculate_cost({})

            logger.info(
                f"[{self.name}] Order quantity: {order_quantity} (supplier: {supplier['name']})"
            )

            return AgentResult(
                success=True,
                data={
                    "order_quantity": order_quantity,
                    "supplier": {
                        "id": supplier["id"],
                        "name": supplier["name"],
                        "unit_price": float(unit_cost),
                        "lead_time_hours": supplier["lead_time_hours"],
                    },
                    "current_inventory": current_inventory,
                    "optimal_order_level": int(optimal_order),
                    "safety_stock": safety_stock,
                    "expected_waste": expected_waste,
                    "expected_shortage": expected_shortage,
                    "critical_ratio": round(critical_ratio, 3),
                },
                confidence=0.89,
                execution_time=execution_time,
                cost=cost,
            )

        except KeyError as e:
            logger.error(f"[{self.name}] Missing required input: {e}")
            return AgentResult(
                success=False,
                data={},
                confidence=0.0,
                execution_time=time.time() - start_time,
                cost=0,
                error_message=f"Missing required input: {e}",
            )
        except Exception as e:
            logger.error(f"[{self.name}] Execution failed: {e}")
            return AgentResult(
                success=False,
                data={},
                confidence=0.0,
                execution_time=time.time() - start_time,
                cost=0,
                error_message=str(e),
            )

    def _get_best_supplier(self) -> Dict[str, Any]:
        """
        最適サプライヤー取得

        品質スコアが最も高いサプライヤーを選択。

        Returns:
            Dict: サプライヤー情報
        """
        query = text(
            """
            SELECT
                supplier_id as id,
                supplier_name as name,
                unit_price,
                lead_time_hours,
                quality_score
            FROM suppliers
            ORDER BY quality_score DESC
            LIMIT 1
        """
        )

        result = self.db_session.execute(query)
        row = result.fetchone()

        if row is None:
            # デフォルト値
            return {
                "id": "SUP001",
                "name": "静岡農協",
                "unit_price": 120.0,
                "lead_time_hours": 8,
                "quality_score": 0.95,
            }

        return dict(row._mapping)
