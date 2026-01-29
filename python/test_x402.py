"""
X402 v2 プロトコルテスト

Agent-to-Agent決済フローの検証
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from protocols.x402 import (
    PaymentScheme,
    X402Client,
    X402Request,
    X402Response,
    PaymentStatus,
)
from protocols.x402.models import jpyc_to_wei, wei_to_jpyc


def test_x402_exact_payment():
    """X402 EXACTスキームテスト（固定料金）"""
    print("\n" + "=" * 60)
    print("Test 1: EXACT Payment Scheme（固定料金）")
    print("=" * 60)

    # クライアント初期化（エージェントID 0）
    client = X402Client(client_agent_id=0)

    # リクエスト作成（在庫最適化サービス: 15 JPYC固定）
    request = client.create_request(
        service_agent_id=2,
        service_description="在庫最適化サービス",
        payment_scheme=PaymentScheme.EXACT,
        base_amount_jpyc=15.0
    )

    print(f"\n✓ リクエスト作成:")
    print(f"  Request ID: {request.request_id}")
    print(f"  Client Agent: {request.client_agent_id}")
    print(f"  Service Agent: {request.service_agent_id}")
    print(f"  Payment Scheme: {request.payment_scheme.value}")
    print(f"  Base Amount: {wei_to_jpyc(request.base_amount)} JPYC")

    # レスポンス作成（サービス提供側）
    response = X402Response(
        request_id=request.request_id,
        response_id=f"res-{request.request_id[4:]}",
        status="success",
        result={"optimal_order_quantity": 340, "expected_profit": 12500},
        actual_amount=request.base_amount,  # EXACT: 固定料金
        payment_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        execution_time_ms=500
    )

    print(f"\n✓ レスポンス受信:")
    print(f"  Response ID: {response.response_id}")
    print(f"  Status: {response.status}")
    print(f"  Actual Amount: {wei_to_jpyc(response.actual_amount)} JPYC")

    # 決済処理
    transaction = client.process_response(request, response)

    print(f"\n✓ 決済完了:")
    print(f"  Transaction ID: {transaction.transaction_id}")
    print(f"  Amount: {wei_to_jpyc(transaction.amount)} JPYC")
    print(f"  Status: {transaction.status.value}")
    print(f"  TX Hash: {transaction.tx_hash}")

    assert transaction.status == PaymentStatus.COMPLETED
    assert transaction.amount == request.base_amount
    print("\n✅ EXACT Payment Test PASSED")


def test_x402_upto_payment():
    """X402 UPTOスキームテスト（従量課金、上限付き）"""
    print("\n" + "=" * 60)
    print("Test 2: UPTO Payment Scheme（従量課金）")
    print("=" * 60)

    # クライアント初期化（エージェントID 0）
    client = X402Client(client_agent_id=0)

    # リクエスト作成（需要予測サービス: 3 JPYC + 従量課金、上限10 JPYC）
    request = client.create_request(
        service_agent_id=1,
        service_description="需要予測サービス",
        payment_scheme=PaymentScheme.UPTO,
        base_amount_jpyc=3.0,
        max_amount_jpyc=10.0,
        metadata={"product_sku": "TOMATO-001", "days": 7}
    )

    print(f"\n✓ リクエスト作成:")
    print(f"  Request ID: {request.request_id}")
    print(f"  Payment Scheme: {request.payment_scheme.value}")
    print(f"  Base Amount: {wei_to_jpyc(request.base_amount)} JPYC")
    print(f"  Max Amount: {wei_to_jpyc(request.max_amount)} JPYC")

    # レスポンス作成（2000レコード処理 → 0.02 JPYC/1000レコード = 0.04 JPYC追加）
    actual_amount_jpyc = 3.0 + (2000 / 1000 * 0.02)  # 3.04 JPYC

    response = X402Response(
        request_id=request.request_id,
        response_id=f"res-{request.request_id[4:]}",
        status="success",
        result={
            "predicted_demand": 340,
            "confidence_interval": [325, 355],
            "std_dev": 15
        },
        actual_amount=jpyc_to_wei(actual_amount_jpyc),
        payment_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        execution_time_ms=1200,
        usage_metrics={"records_processed": 2000}
    )

    print(f"\n✓ レスポンス受信:")
    print(f"  Records Processed: {response.usage_metrics['records_processed']}")
    print(f"  Actual Amount: {wei_to_jpyc(response.actual_amount)} JPYC")

    # 決済処理
    transaction = client.process_response(request, response)

    print(f"\n✓ 決済完了:")
    print(f"  Transaction ID: {transaction.transaction_id}")
    print(f"  Amount: {wei_to_jpyc(transaction.amount)} JPYC")
    print(f"  Status: {transaction.status.value}")
    print(f"  TX Hash: {transaction.tx_hash}")

    assert transaction.status == PaymentStatus.COMPLETED
    assert transaction.amount == jpyc_to_wei(actual_amount_jpyc)
    assert transaction.amount <= request.max_amount
    print("\n✅ UPTO Payment Test PASSED")


def test_x402_upto_exceeds_max():
    """X402 UPTOスキーム上限超過テスト"""
    print("\n" + "=" * 60)
    print("Test 3: UPTO Payment Scheme - Max Exceeded（上限超過）")
    print("=" * 60)

    client = X402Client(client_agent_id=0)

    request = client.create_request(
        service_agent_id=1,
        service_description="需要予測サービス",
        payment_scheme=PaymentScheme.UPTO,
        base_amount_jpyc=3.0,
        max_amount_jpyc=10.0
    )

    print(f"\n✓ リクエスト作成:")
    print(f"  Max Amount: {wei_to_jpyc(request.max_amount)} JPYC")

    # 上限を超える請求（15 JPYC）
    response = X402Response(
        request_id=request.request_id,
        response_id=f"res-{request.request_id[4:]}",
        status="success",
        result={"predicted_demand": 340},
        actual_amount=jpyc_to_wei(15.0),  # 上限10 JPYCを超過
        payment_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    )

    print(f"\n✗ レスポンスで上限超過:")
    print(f"  Actual Amount: {wei_to_jpyc(response.actual_amount)} JPYC")

    # 決済処理（エラーが発生するはず）
    try:
        transaction = client.process_response(request, response)
        print("\n❌ Test FAILED: Should have raised ValueError")
        assert False
    except ValueError as e:
        print(f"\n✓ エラー検出: {e}")
        print("\n✅ UPTO Max Exceeded Test PASSED")


def test_x402_deferred_payment():
    """X402 DEFERREDスキームテスト（後払い）"""
    print("\n" + "=" * 60)
    print("Test 4: DEFERRED Payment Scheme（後払い）")
    print("=" * 60)

    client = X402Client(client_agent_id=0)

    # リクエスト作成（レポート生成サービス: 5 JPYC後払い）
    request = client.create_request(
        service_agent_id=3,
        service_description="レポート生成サービス",
        payment_scheme=PaymentScheme.DEFERRED,
        base_amount_jpyc=5.0
    )

    print(f"\n✓ リクエスト作成:")
    print(f"  Payment Scheme: {request.payment_scheme.value}")
    print(f"  Base Amount: {wei_to_jpyc(request.base_amount)} JPYC")

    # レスポンス作成
    response = X402Response(
        request_id=request.request_id,
        response_id=f"res-{request.request_id[4:]}",
        status="success",
        result={"report_url": "https://example.com/report.pdf"},
        actual_amount=request.base_amount,
        payment_address="0x90F79bf6EB2c4f870365E785982E1f101E93b906",
        execution_time_ms=800
    )

    print(f"\n✓ レスポンス受信:")
    print(f"  Status: {response.status}")

    # 決済処理
    transaction = client.process_response(request, response)

    print(f"\n✓ 決済完了:")
    print(f"  Transaction ID: {transaction.transaction_id}")
    print(f"  Amount: {wei_to_jpyc(transaction.amount)} JPYC")
    print(f"  Status: {transaction.status.value}")

    assert transaction.status == PaymentStatus.COMPLETED
    print("\n✅ DEFERRED Payment Test PASSED")


def test_x402_transaction_summary():
    """X402トランザクションサマリーテスト"""
    print("\n" + "=" * 60)
    print("Test 5: Transaction Summary（トランザクション集計）")
    print("=" * 60)

    client = X402Client(client_agent_id=0)

    # 複数のトランザクションを実行
    print("\n✓ 3つの決済を実行中...")

    # 1. 需要予測（UPTO: 3.04 JPYC）
    req1 = client.create_request(1, "需要予測", PaymentScheme.UPTO, 3.0, 10.0)
    res1 = X402Response(
        request_id=req1.request_id,
        response_id=f"res-1",
        status="success",
        result={},
        actual_amount=jpyc_to_wei(3.04),
        payment_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    )
    client.process_response(req1, res1)

    # 2. 在庫最適化（EXACT: 15.0 JPYC）
    req2 = client.create_request(2, "在庫最適化", PaymentScheme.EXACT, 15.0)
    res2 = X402Response(
        request_id=req2.request_id,
        response_id=f"res-2",
        status="success",
        result={},
        actual_amount=jpyc_to_wei(15.0),
        payment_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    )
    client.process_response(req2, res2)

    # 3. レポート生成（DEFERRED: 5.0 JPYC）
    req3 = client.create_request(3, "レポート生成", PaymentScheme.DEFERRED, 5.0)
    res3 = X402Response(
        request_id=req3.request_id,
        response_id=f"res-3",
        status="success",
        result={},
        actual_amount=jpyc_to_wei(5.0),
        payment_address="0x90F79bf6EB2c4f870365E785982E1f101E93b906"
    )
    client.process_response(req3, res3)

    # サマリー取得
    summary = client.get_transaction_summary()
    total_spent = client.get_total_spent()

    print(f"\n✓ トランザクションサマリー:")
    print(f"  Total Transactions: {summary['total_transactions']}")
    print(f"  Completed: {summary['completed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total Spent: {summary['total_spent_jpyc']:.2f} JPYC")
    print(f"\n  By Scheme:")
    print(f"    EXACT: {summary['by_scheme']['exact']} transactions")
    print(f"    UPTO: {summary['by_scheme']['upto']} transactions")
    print(f"    DEFERRED: {summary['by_scheme']['deferred']} transactions")

    expected_total = 3.04 + 15.0 + 5.0  # 23.04 JPYC
    assert summary['total_transactions'] == 3
    assert summary['completed'] == 3
    assert abs(total_spent - expected_total) < 0.01

    print("\n✅ Transaction Summary Test PASSED")


def main():
    """全テストを実行"""
    print("\n" + "=" * 60)
    print("X402 v2 Protocol Integration Tests")
    print("=" * 60)

    try:
        test_x402_exact_payment()
        test_x402_upto_payment()
        test_x402_upto_exceeds_max()
        test_x402_deferred_payment()
        test_x402_transaction_summary()

        print("\n" + "=" * 60)
        print("✅ ALL X402 TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Summary:")
        print("  ✓ EXACT payment scheme (fixed fee)")
        print("  ✓ UPTO payment scheme (usage-based with cap)")
        print("  ✓ UPTO max amount validation")
        print("  ✓ DEFERRED payment scheme (post-payment)")
        print("  ✓ Transaction tracking and summary")
        print("\n🎯 X402 v2 protocol is ready for agent integration!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
