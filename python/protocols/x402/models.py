"""
X402 v2 データモデル

Agent-to-Agent決済プロトコルのデータ構造定義
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PaymentScheme(str, Enum):
    """
    X402決済スキーム

    - EXACT: 固定料金（例：在庫最適化 15 JPYC）
    - UPTO: 従量課金上限付き（例：需要予測 3 + 0.02/1000レコード）
    - DEFERRED: 後払い（例：レポート生成 5 JPYC）
    """
    EXACT = "exact"
    UPTO = "upto"
    DEFERRED = "deferred"


class PaymentStatus(str, Enum):
    """決済ステータス"""
    PENDING = "pending"          # 保留中
    AUTHORIZED = "authorized"    # 承認済み
    COMPLETED = "completed"      # 完了
    FAILED = "failed"            # 失敗
    REFUNDED = "refunded"        # 返金済み


class X402Request(BaseModel):
    """
    X402リクエスト

    クライアントがエージェントにサービスを依頼する際のリクエスト
    """
    request_id: str = Field(..., description="リクエストID（UUID）")
    client_agent_id: int = Field(..., description="クライアントエージェントID（ERC-8004）")
    service_agent_id: int = Field(..., description="サービス提供エージェントID（ERC-8004）")
    service_description: str = Field(..., description="サービス内容")
    payment_scheme: PaymentScheme = Field(..., description="決済スキーム")

    # 決済情報
    base_amount: int = Field(..., description="基本料金（JPYC wei単位）", ge=0)
    max_amount: Optional[int] = Field(None, description="最大料金（uptoスキームの場合）", ge=0)

    # メタデータ
    metadata: Dict[str, Any] = Field(default_factory=dict, description="追加情報")
    timestamp: datetime = Field(default_factory=datetime.now, description="リクエスト時刻")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "client_agent_id": 0,
                "service_agent_id": 1,
                "service_description": "トマトの需要予測",
                "payment_scheme": "upto",
                "base_amount": 3000000000000000000,  # 3 JPYC
                "max_amount": 10000000000000000000,  # 10 JPYC
                "metadata": {
                    "product_sku": "TOMATO-001",
                    "days": 7
                }
            }
        }


class X402Response(BaseModel):
    """
    X402レスポンス

    エージェントがサービス提供後に返すレスポンス
    """
    request_id: str = Field(..., description="対応するリクエストID")
    response_id: str = Field(..., description="レスポンスID（UUID）")

    # サービス結果
    status: str = Field(..., description="サービス実行ステータス")
    result: Dict[str, Any] = Field(default_factory=dict, description="サービス実行結果")

    # 決済情報
    actual_amount: int = Field(..., description="実際の請求額（JPYC wei単位）", ge=0)
    payment_address: str = Field(..., description="支払先ウォレットアドレス")

    # メタデータ
    execution_time_ms: Optional[int] = Field(None, description="実行時間（ミリ秒）")
    usage_metrics: Dict[str, Any] = Field(default_factory=dict, description="使用量メトリクス")
    timestamp: datetime = Field(default_factory=datetime.now, description="レスポンス時刻")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "response_id": "res-123e4567-e89b-12d3-a456-426614174001",
                "status": "success",
                "result": {
                    "predicted_demand": 340,
                    "confidence_interval": [325, 355],
                    "std_dev": 15
                },
                "actual_amount": 3040000000000000000,  # 3.04 JPYC
                "payment_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
                "execution_time_ms": 1200,
                "usage_metrics": {
                    "records_processed": 2000
                }
            }
        }


class X402Transaction(BaseModel):
    """
    X402トランザクション

    決済実行の記録
    """
    transaction_id: str = Field(..., description="トランザクションID（UUID）")
    request_id: str = Field(..., description="対応するリクエストID")
    response_id: str = Field(..., description="対応するレスポンスID")

    # エージェント情報
    client_agent_id: int = Field(..., description="クライアントエージェントID")
    service_agent_id: int = Field(..., description="サービスエージェントID")

    # 決済情報
    payment_scheme: PaymentScheme = Field(..., description="決済スキーム")
    amount: int = Field(..., description="支払額（JPYC wei単位）", ge=0)

    # ブロックチェーン情報
    tx_hash: Optional[str] = Field(None, description="ブロックチェーントランザクションハッシュ")
    block_number: Optional[int] = Field(None, description="ブロック番号")

    # ステータス
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="決済ステータス")

    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.now, description="作成時刻")
    completed_at: Optional[datetime] = Field(None, description="完了時刻")

    # エラー情報
    error_message: Optional[str] = Field(None, description="エラーメッセージ")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "tx-123e4567-e89b-12d3-a456-426614174002",
                "request_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "response_id": "res-123e4567-e89b-12d3-a456-426614174001",
                "client_agent_id": 0,
                "service_agent_id": 1,
                "payment_scheme": "upto",
                "amount": 3040000000000000000,
                "tx_hash": "0xabcd1234...",
                "block_number": 12345,
                "status": "completed"
            }
        }


def jpyc_to_wei(jpyc_amount: float) -> int:
    """
    JPYC額をwei単位に変換

    Args:
        jpyc_amount: JPYC額（小数点可）

    Returns:
        wei単位の額（整数）
    """
    return int(jpyc_amount * 10**18)


def wei_to_jpyc(wei_amount: int) -> float:
    """
    wei単位をJPYC額に変換

    Args:
        wei_amount: wei単位の額（整数）

    Returns:
        JPYC額（浮動小数点）
    """
    return wei_amount / 10**18
