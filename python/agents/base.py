"""
エージェント基底クラス

すべてのエージェントの基底クラス。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PaymentScheme(Enum):
    """X402決済スキーム"""

    EXACT = "exact"  # 固定料金
    UPTO = "upto"  # 従量課金
    DEFERRED = "deferred"  # 後払い


@dataclass
class PaymentConfig:
    """決済設定"""

    scheme: PaymentScheme
    base_amount: int  # JPYC単位
    variable_rate: Optional[float] = None  # upto方式用（JPYC/1000レコード）


@dataclass
class AgentResult:
    """エージェント実行結果"""

    success: bool
    data: Dict[str, Any]
    confidence: float  # 0.0 ~ 1.0
    execution_time: float  # 秒
    cost: int  # JPYC
    error_message: Optional[str] = None
    tx_hash: Optional[str] = None  # Phase 2で使用


class Agent(ABC):
    """エージェント基底クラス"""

    def __init__(
        self,
        name: str,
        payment_config: PaymentConfig,
        erc8004_id: Optional[int] = None,
        should_record_onchain: bool = False,
    ):
        """
        Args:
            name: エージェント名
            payment_config: 決済設定
            erc8004_id: ERC-8004エージェントID（Phase 2）
            should_record_onchain: オンチェーン記録の有無（Phase 2）
        """
        self.name = name
        self.payment_config = payment_config
        self.erc8004_id = erc8004_id
        self.should_record_onchain = should_record_onchain
        logger.info(f"Agent initialized: {self.name}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        エージェントのメイン処理

        Args:
            input_data: 入力データ

        Returns:
            AgentResult: 実行結果
        """
        pass

    def calculate_cost(self, usage_metrics: Dict[str, Any]) -> int:
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
            data_rows = usage_metrics.get("data_rows", 0)
            variable_cost = (data_rows / 1000.0) * (
                self.payment_config.variable_rate or 0
            )
            return int(self.payment_config.base_amount + variable_cost)

        elif self.payment_config.scheme == PaymentScheme.DEFERRED:
            # セッション終了時に計算（Phase 2）
            return self.payment_config.base_amount

        return 0
