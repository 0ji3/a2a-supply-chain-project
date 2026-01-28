"""
需要予測エージェント

過去POSデータから翌日の販売数量を予測する。
MVP版: 7日移動平均ベースの簡易予測
"""
import time
import logging
from typing import Dict, Any
import pandas as pd
from sqlalchemy import text

from .base import Agent, AgentResult, PaymentScheme, PaymentConfig

logger = logging.getLogger(__name__)


class DemandForecastAgent(Agent):
    """需要予測エージェント（簡易版）"""

    def __init__(self, db_session):
        """
        Args:
            db_session: データベースセッション
        """
        super().__init__(
            name="demand_forecast",
            payment_config=PaymentConfig(
                scheme=PaymentScheme.UPTO,
                base_amount=3,  # 3 JPYC
                variable_rate=0.02,  # 0.02 JPYC/1000レコード
            ),
        )
        self.db_session = db_session

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        需要予測の実行

        Args:
            input_data:
                - product_sku: 商品SKU
                - store_id: 店舗ID

        Returns:
            AgentResult: 予測結果
        """
        start_time = time.time()

        try:
            product_sku = input_data["product_sku"]
            store_id = input_data["store_id"]

            logger.info(
                f"[{self.name}] Starting prediction for {product_sku} at {store_id}"
            )

            # 1. 過去POSデータ取得（過去30日分）
            pos_data = self._fetch_pos_data(product_sku, store_id, days=30)

            if len(pos_data) == 0:
                return AgentResult(
                    success=False,
                    data={},
                    confidence=0.0,
                    execution_time=time.time() - start_time,
                    cost=0,
                    error_message="No historical data found",
                )

            # 2. 7日移動平均で予測
            recent_sales = pos_data.tail(7)["sales_quantity"].values
            predicted_demand = int(recent_sales.mean())

            # 3. 信頼区間算出（±9%）
            lower_bound = int(predicted_demand * 0.91)
            upper_bound = int(predicted_demand * 1.09)

            execution_time = time.time() - start_time

            # コスト計算
            cost = self.calculate_cost({"data_rows": len(pos_data)})

            logger.info(
                f"[{self.name}] Prediction: {predicted_demand} (range: {lower_bound}-{upper_bound})"
            )

            return AgentResult(
                success=True,
                data={
                    "predicted_demand": predicted_demand,
                    "confidence_interval": {"lower": lower_bound, "upper": upper_bound},
                    "historical_data_points": len(pos_data),
                    "method": "7-day moving average",
                },
                confidence=0.85,  # 簡易版なので85%
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

    def _fetch_pos_data(
        self, product_sku: str, store_id: str, days: int = 30
    ) -> pd.DataFrame:
        """
        POSデータ取得

        Args:
            product_sku: 商品SKU
            store_id: 店舗ID
            days: 取得日数

        Returns:
            pd.DataFrame: POSデータ
        """
        query = text(
            """
            SELECT
                date,
                sales_quantity,
                price,
                day_of_week,
                is_holiday
            FROM pos_sales
            WHERE product_sku = :product_sku
              AND store_id = :store_id
              AND date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY date
        """
        )

        result = self.db_session.execute(
            query, {"product_sku": product_sku, "store_id": store_id}
        )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        logger.debug(f"Fetched {len(df)} records from POS data")
        return df
