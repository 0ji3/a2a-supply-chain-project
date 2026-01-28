"""
ブロックチェーン統合

Anvil/Ethereum互換チェーンとの統合。
ERC-8004（Identity, Reputation）およびJPYCとのやり取り。
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account

logger = logging.getLogger(__name__)


class BlockchainService:
    """ブロックチェーンサービス"""

    def __init__(self, rpc_url: str, private_key: str):
        """
        Args:
            rpc_url: RPC URL（例: http://localhost:8545）
            private_key: デプロイヤーの秘密鍵
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # PoA（Proof of Authority）チェーン対応
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # アカウント設定
        self.account = Account.from_key(private_key)
        self.w3.eth.default_account = self.account.address

        logger.info(f"Connected to blockchain: {rpc_url}")
        logger.info(f"Account: {self.account.address}")

        # コントラクトインスタンス（後でロード）
        self.identity_contract = None
        self.reputation_contract = None
        self.jpyc_contract = None

    def load_contracts(self, deployments_file: str = "../deployments.txt"):
        """
        デプロイ情報からコントラクトをロード

        Args:
            deployments_file: デプロイ情報ファイルのパス
        """
        try:
            # デプロイ情報を読み込み
            deployments = {}
            with open(deployments_file, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=")
                        deployments[key] = value

            logger.info(f"Loaded deployments: {deployments}")

            # ABIファイルのパス
            contracts_dir = Path(__file__).parent.parent / "contracts"
            out_dir = contracts_dir / "out"

            # ERC8004Identityのロード
            identity_address = deployments["ERC8004Identity"]
            identity_abi_path = out_dir / "ERC8004Identity.sol" / "ERC8004Identity.json"
            with open(identity_abi_path, "r") as f:
                identity_artifact = json.load(f)
                self.identity_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(identity_address),
                    abi=identity_artifact["abi"]
                )
            logger.info(f"Identity contract loaded: {identity_address}")

            # ERC8004Reputationのロード
            reputation_address = deployments["ERC8004Reputation"]
            reputation_abi_path = out_dir / "ERC8004Reputation.sol" / "ERC8004Reputation.json"
            with open(reputation_abi_path, "r") as f:
                reputation_artifact = json.load(f)
                self.reputation_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(reputation_address),
                    abi=reputation_artifact["abi"]
                )
            logger.info(f"Reputation contract loaded: {reputation_address}")

            # MockJPYCのロード
            jpyc_address = deployments["MockJPYC"]
            jpyc_abi_path = out_dir / "MockJPYC.sol" / "MockJPYC.json"
            with open(jpyc_abi_path, "r") as f:
                jpyc_artifact = json.load(f)
                self.jpyc_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(jpyc_address),
                    abi=jpyc_artifact["abi"]
                )
            logger.info(f"JPYC contract loaded: {jpyc_address}")

        except Exception as e:
            logger.error(f"Failed to load contracts: {e}")
            raise

    def register_agent(
        self,
        name: str,
        category: str,
        metadata_uri: str = "ipfs://QmDemo"
    ) -> int:
        """
        エージェントを登録

        Args:
            name: エージェント名
            category: カテゴリ
            metadata_uri: メタデータURI

        Returns:
            int: エージェントID
        """
        try:
            # トランザクションを送信
            tx_hash = self.identity_contract.functions.registerAgent(
                name,
                category,
                metadata_uri
            ).transact({
                "from": self.account.address,
                "gas": 500000
            })

            # トランザクション確認待ち
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(f"Agent registered: {name} (tx: {tx_hash.hex()})")

            # イベントからエージェントIDを取得
            event = self.identity_contract.events.AgentRegistered().process_receipt(receipt)[0]
            agent_id = event["args"]["agentId"]

            return agent_id

        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            raise

    def submit_feedback(
        self,
        agent_id: int,
        score: int,
        tags: list,
        report_uri: str = ""
    ) -> str:
        """
        エージェントにフィードバックを送信

        Args:
            agent_id: エージェントID
            score: スコア（0-100）
            tags: タグ配列
            report_uri: レポートURI

        Returns:
            str: トランザクションハッシュ
        """
        try:
            # トランザクションを送信
            tx_hash = self.reputation_contract.functions.submitFeedback(
                agent_id,
                score,
                tags,
                report_uri
            ).transact({
                "from": self.account.address,
                "gas": 300000
            })

            # トランザクション確認待ち
            self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(f"Feedback submitted for agent {agent_id} (tx: {tx_hash.hex()})")

            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            raise

    def get_agent_reputation(self, agent_id: int) -> Dict[str, Any]:
        """
        エージェントの評判を取得

        Args:
            agent_id: エージェントID

        Returns:
            Dict: 評判情報
        """
        try:
            total_feedbacks, average_score = self.reputation_contract.functions.getReputationStats(
                agent_id
            ).call()

            return {
                "agent_id": agent_id,
                "total_feedbacks": total_feedbacks,
                "average_score": average_score
            }

        except Exception as e:
            logger.error(f"Failed to get reputation: {e}")
            raise

    def transfer_jpyc(
        self,
        to_address: str,
        amount: int
    ) -> str:
        """
        JPYCを転送

        Args:
            to_address: 受信者アドレス
            amount: 金額（wei単位、10^18 = 1 JPYC）

        Returns:
            str: トランザクションハッシュ
        """
        try:
            # トランザクションを送信
            tx_hash = self.jpyc_contract.functions.transfer(
                Web3.to_checksum_address(to_address),
                amount
            ).transact({
                "from": self.account.address,
                "gas": 100000
            })

            # トランザクション確認待ち
            self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(f"JPYC transferred: {amount} to {to_address} (tx: {tx_hash.hex()})")

            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Failed to transfer JPYC: {e}")
            raise

    def get_jpyc_balance(self, address: str) -> int:
        """
        JPYCの残高を取得

        Args:
            address: アドレス

        Returns:
            int: 残高（wei単位）
        """
        try:
            balance = self.jpyc_contract.functions.balanceOf(
                Web3.to_checksum_address(address)
            ).call()

            return balance

        except Exception as e:
            logger.error(f"Failed to get JPYC balance: {e}")
            raise
