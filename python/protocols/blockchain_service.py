"""
Blockchain Service

Polygon Amoyテストネットとの接続・トランザクション実行
"""
import os
from typing import Optional, Dict, Any
from decimal import Decimal
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_typing import Address

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    ブロックチェーンサービス

    Web3接続、トランザクション送信、JPYC転送を管理
    """

    # ERC-20 Transfer関数のシグネチャ
    ERC20_TRANSFER_ABI = [{
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }]

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        jpyc_address: Optional[str] = None
    ):
        """
        初期化

        Args:
            rpc_url: Polygon Amoy RPC URL（Noneの場合は環境変数から取得）
            private_key: 秘密鍵（Noneの場合は環境変数から取得）
            jpyc_address: JPYCコントラクトアドレス（Noneの場合は環境変数から取得）
        """
        # 環境変数から設定を読み込み
        self.rpc_url = rpc_url or os.getenv("POLYGON_AMOY_RPC_URL")
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        self.jpyc_address = jpyc_address or os.getenv("MOCK_JPYC",
            "0xafac6B9175D5c51C5F73ab1aAb6d2c35bDC3A302"  # デフォルト値
        )

        if not self.rpc_url:
            raise ValueError("POLYGON_AMOY_RPC_URL not set")
        if not self.private_key:
            raise ValueError("PRIVATE_KEY not set")

        # Web3インスタンスを作成
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Polygon PoS用ミドルウェア（EIP-1559対応）
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # アカウント設定
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address

        # JPYCコントラクト
        self.jpyc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.jpyc_address),
            abi=self.ERC20_TRANSFER_ABI
        )

        # 接続確認
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")

        logger.info(
            f"BlockchainService initialized\n"
            f"  Network: Polygon Amoy (Chain ID: {self.w3.eth.chain_id})\n"
            f"  Account: {self.address}\n"
            f"  JPYC: {self.jpyc_address}"
        )

    def get_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """
        残高を取得

        Args:
            address: アドレス（Noneの場合は自分のアドレス）

        Returns:
            残高情報
        """
        addr = address or self.address
        checksum_addr = Web3.to_checksum_address(addr)

        # MATIC残高
        matic_balance = self.w3.eth.get_balance(checksum_addr)
        matic_balance_eth = self.w3.from_wei(matic_balance, 'ether')

        # JPYC残高（balanceOf関数を呼び出し）
        # 簡易版: transfer ABIしかないので、別途取得が必要
        # ここでは0を返す（後で拡張可能）
        jpyc_balance = 0

        return {
            "address": addr,
            "matic_balance": float(matic_balance_eth),
            "jpyc_balance": jpyc_balance,
            "matic_balance_wei": matic_balance
        }

    def transfer_jpyc(
        self,
        to_address: str,
        amount: int,
        gas_limit: int = 100000
    ) -> str:
        """
        JPYC転送を実行

        Args:
            to_address: 送信先アドレス
            amount: 送信額（wei単位、18 decimals）
            gas_limit: ガスリミット

        Returns:
            トランザクションハッシュ
        """
        try:
            # アドレスをチェックサム形式に変換
            to_checksum = Web3.to_checksum_address(to_address)

            # トランザクションを構築
            transaction = self.jpyc_contract.functions.transfer(
                to_checksum,
                amount
            ).build_transaction({
                'from': self.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            # トランザクションに署名
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.private_key
            )

            # トランザクションを送信
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            logger.info(
                f"JPYC transfer initiated\n"
                f"  From: {self.address}\n"
                f"  To: {to_address}\n"
                f"  Amount: {amount} wei ({self.w3.from_wei(amount, 'ether')} JPYC)\n"
                f"  TX Hash: {tx_hash_hex}"
            )

            # トランザクションの完了を待つ（オプション）
            # receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            # logger.info(f"Transaction confirmed in block {receipt['blockNumber']}")

            return tx_hash_hex

        except Exception as e:
            logger.error(f"JPYC transfer failed: {e}")
            raise

    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """
        トランザクションレシートを取得

        Args:
            tx_hash: トランザクションハッシュ

        Returns:
            トランザクションレシート
        """
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)

        return {
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber'],
            "gas_used": receipt['gasUsed'],
            "status": receipt['status'],  # 1 = success, 0 = failed
            "from": receipt['from'],
            "to": receipt['to']
        }

    def wait_for_transaction(
        self,
        tx_hash: str,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        トランザクションの完了を待つ

        Args:
            tx_hash: トランザクションハッシュ
            timeout: タイムアウト（秒）

        Returns:
            トランザクションレシート
        """
        logger.info(f"Waiting for transaction {tx_hash}...")

        receipt = self.w3.eth.wait_for_transaction_receipt(
            tx_hash,
            timeout=timeout
        )

        if receipt['status'] == 1:
            logger.info(f"Transaction confirmed in block {receipt['blockNumber']}")
        else:
            logger.error(f"Transaction failed: {tx_hash}")

        return self.get_transaction_receipt(tx_hash)


# グローバルインスタンス（シングルトン）
_blockchain_service_instance: Optional[BlockchainService] = None


def get_blockchain_service() -> BlockchainService:
    """
    BlockchainServiceのシングルトンインスタンスを取得

    Returns:
        BlockchainService
    """
    global _blockchain_service_instance

    if _blockchain_service_instance is None:
        _blockchain_service_instance = BlockchainService()

    return _blockchain_service_instance
