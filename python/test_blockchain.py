"""
ブロックチェーン接続テスト
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from blockchain import BlockchainService

def test_blockchain_connection():
    """ブロックチェーン接続とコントラクト読み込みテスト"""

    # Anvil RPC URL（環境に応じて変更）
    import os
    rpc_url = os.getenv("ANVIL_RPC_URL", "http://localhost:8545")

    # Anvilのデフォルトアカウント0の秘密鍵
    private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    print("=" * 60)
    print("ブロックチェーン接続テスト")
    print("=" * 60)

    # BlockchainServiceを初期化
    print("\n1. BlockchainServiceを初期化...")
    blockchain = BlockchainService(rpc_url, private_key)
    print(f"   ✓ 接続成功: {rpc_url}")
    print(f"   ✓ アカウント: {blockchain.account.address}")

    # コントラクトをロード
    print("\n2. デプロイ済みコントラクトをロード...")
    # deployments.txtのパスを環境に応じて調整
    if Path("/deployments.txt").exists():
        # Dockerコンテナ内
        deployments_path = "/deployments.txt"
    else:
        # ホストマシン
        deployments_path = str(Path(__file__).parent.parent / "deployments.txt")
    blockchain.load_contracts(deployments_path)
    print("   ✓ ERC8004Identity ロード完了")
    print("   ✓ ERC8004Reputation ロード完了")
    print("   ✓ MockJPYC ロード完了")

    # Agent 1の情報を取得
    print("\n3. Agent 1 (Demand Forecast)の情報を取得...")
    reputation = blockchain.get_agent_reputation(1)
    print(f"   ✓ Agent ID: {reputation['agent_id']}")
    print(f"   ✓ Total Feedbacks: {reputation['total_feedbacks']}")
    print(f"   ✓ Average Score: {reputation['average_score']}")

    # JPYCの残高を取得
    print("\n4. JPYCの残高を取得...")
    balance = blockchain.get_jpyc_balance(blockchain.account.address)
    jpyc_amount = balance / 10**18
    print(f"   ✓ 残高: {jpyc_amount:,.2f} JPYC")

    # フィードバックを送信（テスト）
    print("\n5. Agent 1にフィードバックを送信...")
    tx_hash = blockchain.submit_feedback(
        agent_id=1,
        score=95,
        tags=["accurate", "fast"],
        report_uri="ipfs://QmTestReport"
    )
    print(f"   ✓ フィードバック送信完了: {tx_hash[:10]}...")

    # フィードバック後の評判を確認
    print("\n6. フィードバック後の評判を確認...")
    reputation = blockchain.get_agent_reputation(1)
    print(f"   ✓ Total Feedbacks: {reputation['total_feedbacks']}")
    print(f"   ✓ Average Score: {reputation['average_score']}")

    print("\n" + "=" * 60)
    print("✓ 全てのテストが成功しました！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_blockchain_connection()
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
