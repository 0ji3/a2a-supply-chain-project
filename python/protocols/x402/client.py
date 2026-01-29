"""
X402 v2 クライアント

Agent-to-Agent決済を実行するクライアント実装
"""
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .models import (
    PaymentScheme,
    X402Request,
    X402Response,
    X402Transaction,
    PaymentStatus,
    jpyc_to_wei,
    wei_to_jpyc,
)

logger = logging.getLogger(__name__)


class X402Client:
    """
    X402決済クライアント

    エージェント間のマイクロペイメントを処理
    """

    def __init__(
        self,
        blockchain_service=None,
        client_agent_id: int = 0
    ):
        """
        初期化

        Args:
            blockchain_service: ブロックチェーンサービス（Phase 3ではNone）
            client_agent_id: クライアントエージェントID
        """
        self.blockchain_service = blockchain_service
        self.client_agent_id = client_agent_id
        self.transactions: Dict[str, X402Transaction] = {}

        logger.info(f"X402Client initialized for agent {client_agent_id}")

    def create_request(
        self,
        service_agent_id: int,
        service_description: str,
        payment_scheme: PaymentScheme,
        base_amount_jpyc: float,
        max_amount_jpyc: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> X402Request:
        """
        X402リクエストを作成

        Args:
            service_agent_id: サービス提供エージェントID
            service_description: サービス内容
            payment_scheme: 決済スキーム
            base_amount_jpyc: 基本料金（JPYC）
            max_amount_jpyc: 最大料金（JPYC、uptoスキームの場合）
            metadata: 追加情報

        Returns:
            X402Request
        """
        request_id = f"req-{uuid.uuid4()}"

        request = X402Request(
            request_id=request_id,
            client_agent_id=self.client_agent_id,
            service_agent_id=service_agent_id,
            service_description=service_description,
            payment_scheme=payment_scheme,
            base_amount=jpyc_to_wei(base_amount_jpyc),
            max_amount=jpyc_to_wei(max_amount_jpyc) if max_amount_jpyc else None,
            metadata=metadata or {}
        )

        logger.info(
            f"Created X402 request {request_id} for agent {service_agent_id}: "
            f"{service_description} ({payment_scheme.value}, {base_amount_jpyc} JPYC)"
        )

        return request

    def process_response(
        self,
        request: X402Request,
        response: X402Response
    ) -> X402Transaction:
        """
        X402レスポンスを処理し、決済を実行

        Args:
            request: 元のリクエスト
            response: エージェントからのレスポンス

        Returns:
            X402Transaction
        """
        # トランザクションIDを生成
        transaction_id = f"tx-{uuid.uuid4()}"

        # 決済額を検証
        actual_amount_jpyc = wei_to_jpyc(response.actual_amount)
        base_amount_jpyc = wei_to_jpyc(request.base_amount)

        if request.payment_scheme == PaymentScheme.EXACT:
            # EXACTスキーム: 固定料金
            if response.actual_amount != request.base_amount:
                logger.warning(
                    f"EXACT scheme amount mismatch: expected {base_amount_jpyc} JPYC, "
                    f"got {actual_amount_jpyc} JPYC"
                )

        elif request.payment_scheme == PaymentScheme.UPTO:
            # UPTOスキーム: 従量課金、上限チェック
            if request.max_amount and response.actual_amount > request.max_amount:
                max_amount_jpyc = wei_to_jpyc(request.max_amount)
                raise ValueError(
                    f"Amount exceeds maximum: {actual_amount_jpyc} JPYC > {max_amount_jpyc} JPYC"
                )

        # トランザクション作成
        transaction = X402Transaction(
            transaction_id=transaction_id,
            request_id=request.request_id,
            response_id=response.response_id,
            client_agent_id=request.client_agent_id,
            service_agent_id=request.service_agent_id,
            payment_scheme=request.payment_scheme,
            amount=response.actual_amount,
            status=PaymentStatus.PENDING
        )

        # 決済実行（Phase 3ではモック、Phase 4でブロックチェーン統合）
        if self.blockchain_service:
            # 実際のブロックチェーン決済
            tx_hash = self._execute_blockchain_payment(
                to_address=response.payment_address,
                amount=response.actual_amount
            )
            transaction.tx_hash = tx_hash
            transaction.status = PaymentStatus.COMPLETED
            transaction.completed_at = datetime.now()

        else:
            # Phase 3: モック決済
            transaction.tx_hash = f"0xmock_{transaction_id[:8]}"
            transaction.status = PaymentStatus.COMPLETED
            transaction.completed_at = datetime.now()

            logger.info(
                f"[MOCK] Payment completed: {actual_amount_jpyc} JPYC "
                f"from agent {request.client_agent_id} to agent {request.service_agent_id} "
                f"(scheme: {request.payment_scheme.value})"
            )

        # トランザクションを記録
        self.transactions[transaction_id] = transaction

        return transaction

    def _execute_blockchain_payment(
        self,
        to_address: str,
        amount: int
    ) -> str:
        """
        ブロックチェーン決済を実行

        Args:
            to_address: 支払先アドレス
            amount: 支払額（wei）

        Returns:
            トランザクションハッシュ
        """
        # Phase 4で実装
        if not self.blockchain_service:
            raise RuntimeError("Blockchain service not initialized")

        # JPYC transferを実行
        tx_hash = self.blockchain_service.transfer_jpyc(
            to_address=to_address,
            amount=amount
        )

        return tx_hash

    def get_transaction(self, transaction_id: str) -> Optional[X402Transaction]:
        """
        トランザクションを取得

        Args:
            transaction_id: トランザクションID

        Returns:
            X402Transaction or None
        """
        return self.transactions.get(transaction_id)

    def get_total_spent(self) -> float:
        """
        総支払額を取得（JPYC）

        Returns:
            総支払額
        """
        total_wei = sum(
            tx.amount for tx in self.transactions.values()
            if tx.status == PaymentStatus.COMPLETED
        )
        return wei_to_jpyc(total_wei)

    def get_transaction_summary(self) -> Dict[str, Any]:
        """
        トランザクションサマリーを取得

        Returns:
            サマリー情報
        """
        completed = [tx for tx in self.transactions.values() if tx.status == PaymentStatus.COMPLETED]
        failed = [tx for tx in self.transactions.values() if tx.status == PaymentStatus.FAILED]

        return {
            "total_transactions": len(self.transactions),
            "completed": len(completed),
            "failed": len(failed),
            "total_spent_jpyc": self.get_total_spent(),
            "by_scheme": {
                PaymentScheme.EXACT.value: len([tx for tx in completed if tx.payment_scheme == PaymentScheme.EXACT]),
                PaymentScheme.UPTO.value: len([tx for tx in completed if tx.payment_scheme == PaymentScheme.UPTO]),
                PaymentScheme.DEFERRED.value: len([tx for tx in completed if tx.payment_scheme == PaymentScheme.DEFERRED]),
            }
        }
