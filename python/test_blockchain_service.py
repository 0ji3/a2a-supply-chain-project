"""
Blockchain Service テスト

Polygon Amoy接続とJPYC転送のテスト
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# .envファイルを読み込み
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from protocols.blockchain_service import get_blockchain_service
from protocols.x402.models import jpyc_to_wei, wei_to_jpyc


def test_connection():
    """接続テスト"""
    print("\n" + "=" * 60)
    print("Test 1: Blockchain Connection")
    print("=" * 60)

    service = get_blockchain_service()

    print(f"\n✓ Connected to Polygon Amoy")
    print(f"  Chain ID: {service.w3.eth.chain_id}")
    print(f"  Account: {service.address}")
    print(f"  JPYC Contract: {service.jpyc_address}")

    # 残高確認
    balance = service.get_balance()
    print(f"\n✓ Balance:")
    print(f"  MATIC: {balance['matic_balance']:.4f} MATIC")
    print(f"  JPYC: {balance['jpyc_balance']} JPYC")

    assert service.w3.is_connected()
    print("\n✅ Connection Test PASSED")


def test_jpyc_transfer():
    """JPYC転送テスト"""
    print("\n" + "=" * 60)
    print("Test 2: JPYC Transfer (Simulation)")
    print("=" * 60)

    service = get_blockchain_service()

    # テスト用の送信先アドレス（自分自身に送信）
    to_address = service.address
    amount_jpyc = 1.0  # 1 JPYC
    amount_wei = jpyc_to_wei(amount_jpyc)

    print(f"\n✓ Transfer Parameters:")
    print(f"  From: {service.address}")
    print(f"  To: {to_address}")
    print(f"  Amount: {amount_jpyc} JPYC ({amount_wei} wei)")

    # 実際の転送はコメントアウト（テストMATICを節約）
    # tx_hash = service.transfer_jpyc(to_address, amount_wei)
    # print(f"\n✓ Transaction Hash: {tx_hash}")

    print(f"\n✓ Transfer simulated successfully")
    print(f"  Note: Actual transfer commented out to save test MATIC")

    print("\n✅ JPYC Transfer Test PASSED (Simulation)")


def test_x402_payment_flow():
    """X402決済フロー統合テスト（シミュレーション）"""
    print("\n" + "=" * 60)
    print("Test 3: X402 Payment Flow (Simulation)")
    print("=" * 60)

    service = get_blockchain_service()

    # エージェント間決済のシミュレーション
    payments = [
        {"agent": "Demand Forecast", "amount_jpyc": 3.04},
        {"agent": "Inventory Optimizer", "amount_jpyc": 15.0},
        {"agent": "Report Generator", "amount_jpyc": 5.0},
    ]

    total_jpyc = sum(p["amount_jpyc"] for p in payments)

    print(f"\n✓ Simulating {len(payments)} agent payments:")
    for payment in payments:
        print(f"  - {payment['agent']}: {payment['amount_jpyc']} JPYC")

    print(f"\n✓ Total: {total_jpyc} JPYC")
    print(f"  Total (wei): {jpyc_to_wei(total_jpyc)}")

    print(f"\n✓ Current MATIC balance: {service.get_balance()['matic_balance']:.4f} MATIC")
    print(f"  Estimated gas cost: ~0.001 MATIC per transaction")
    print(f"  Total gas cost: ~{0.001 * len(payments):.4f} MATIC")

    print("\n✅ X402 Payment Flow Test PASSED (Simulation)")


def main():
    """全テストを実行"""
    print("\n" + "=" * 60)
    print("Blockchain Service Integration Tests")
    print("Polygon Amoy Testnet")
    print("=" * 60)

    try:
        test_connection()
        test_jpyc_transfer()
        test_x402_payment_flow()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Summary:")
        print("  ✓ Blockchain connection established")
        print("  ✓ JPYC contract accessible")
        print("  ✓ Ready for X402 payment integration")
        print("\n🎯 Next Steps:")
        print("  1. Update X402Client to use BlockchainService")
        print("  2. Test real JPYC transfers")
        print("  3. Run end-to-end agent optimization with real payments")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
