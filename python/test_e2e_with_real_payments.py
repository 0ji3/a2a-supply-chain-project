"""
エンドツーエンド統合テスト（実決済版）

LLMエージェント（CrewAI）+ X402実決済 + Polygon Amoy
需要予測 → 在庫最適化 → レポート生成の全フローで実際のブロックチェーン決済を実行
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# .envファイルを読み込み
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from protocols.blockchain_service import get_blockchain_service
from protocols.x402 import (
    PaymentScheme,
    X402Client,
    X402Response,
    PaymentStatus,
)
from protocols.x402.models import jpyc_to_wei, wei_to_jpyc


def test_e2e_with_real_payments():
    """エンドツーエンドテスト（LLMエージェント + 実決済）"""

    print("\n" + "=" * 70)
    print("E2E統合テスト: LLMエージェント + X402実決済 + Polygon Amoy")
    print("=" * 70)

    # ========================================
    # 初期化
    # ========================================
    print("\n📊 システム初期化...")

    # Blockchain Service
    blockchain_service = get_blockchain_service()
    balance = blockchain_service.get_balance()

    print(f"\n✓ Blockchain Service:")
    print(f"  Network: Polygon Amoy (Chain ID: {blockchain_service.w3.eth.chain_id})")
    print(f"  Account: {blockchain_service.address}")
    print(f"  MATIC: {balance['matic_balance']:.4f} MATIC")
    print(f"  JPYC: {balance['jpyc_balance']} JPYC")

    if balance['matic_balance'] < 0.01:
        print(f"\n⚠️  Warning: Low MATIC balance!")
        return

    # X402 Client
    x402_client = X402Client(
        blockchain_service=blockchain_service,
        client_agent_id=0
    )
    print(f"\n✓ X402 Client initialized")

    # エージェントウォレット（Phase 5）
    agent_wallets = {
        "demand_forecast": os.getenv("AGENT_DEMAND_FORECAST_ADDRESS"),
        "inventory_optimizer": os.getenv("AGENT_INVENTORY_OPTIMIZER_ADDRESS"),
        "report_generator": os.getenv("AGENT_REPORT_GENERATOR_ADDRESS"),
    }
    print(f"\n✓ Agent Wallets:")
    for agent, address in agent_wallets.items():
        print(f"  {agent}: {address}")

    # ========================================
    # ビジネスパラメータ
    # ========================================
    print(f"\n📊 ビジネスパラメータ:")
    print(f"   店舗: 渋谷店")
    print(f"   商品: トマト (SKU: TOMATO-001)")
    print(f"   明日の天気: 晴れ")
    print(f"   明日のタイプ: 週末")
    print(f"   販売単価: 200円")

    # エージェント料金設定（テスト用に少額）
    agent_fees = {
        "demand_forecast": {"amount": 0.003, "scheme": PaymentScheme.UPTO, "max": 0.01},
        "inventory_optimizer": {"amount": 0.015, "scheme": PaymentScheme.EXACT},
        "report_generator": {"amount": 0.005, "scheme": PaymentScheme.DEFERRED},
    }

    print(f"\n💰 エージェント料金:")
    for agent, fee in agent_fees.items():
        print(f"   - {agent}: {fee['amount']} JPYC ({fee['scheme'].value})")

    total_estimated = sum(f["amount"] for f in agent_fees.values())
    print(f"   合計見積: {total_estimated} JPYC")

    # ========================================
    # LLMエージェント準備
    # ========================================
    print(f"\n🤖 LLMエージェント準備...")

    try:
        from crewai import Agent, Task, Crew, LLM

        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        os.environ["OLLAMA_API_BASE"] = ollama_url

        llm = LLM(
            model="ollama/gemma2:9b",
            base_url=ollama_url
        )
        print(f"   ✓ LLM initialized: gemma2:9b")

        # エージェント作成
        demand_analyst = Agent(
            role="需要予測アナリスト",
            goal="販売データから需要を予測する",
            backstory="あなたは需要予測の専門家です。",
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=2
        )

        inventory_manager = Agent(
            role="在庫最適化マネージャー",
            goal="最適な発注量とサプライヤーを決定する",
            backstory="あなたは在庫管理の専門家です。",
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=2
        )

        report_generator = Agent(
            role="レポートジェネレーター",
            goal="分析結果を分かりやすくまとめる",
            backstory="あなたはビジネスレポートの専門家です。",
            llm=llm,
            verbose=False,
            allow_delegation=False,
            max_iter=2
        )

        print(f"   ✓ 3つのエージェント作成完了")

    except ImportError as e:
        print(f"\n✗ CrewAI not installed: {e}")
        return

    # ========================================
    # Phase 1: 需要予測 + X402決済
    # ========================================
    print("\n" + "=" * 70)
    print("Phase 1: 需要予測エージェント + X402決済")
    print("=" * 70)

    # X402リクエスト作成
    demand_request = x402_client.create_request(
        service_agent_id=1,
        service_description="需要予測サービス",
        payment_scheme=agent_fees["demand_forecast"]["scheme"],
        base_amount_jpyc=agent_fees["demand_forecast"]["amount"],
        max_amount_jpyc=agent_fees["demand_forecast"]["max"]
    )

    print(f"\n✓ X402 Request: {demand_request.request_id}")
    print(f"  Scheme: {demand_request.payment_scheme.value}")
    print(f"  Amount: {wei_to_jpyc(demand_request.base_amount)} JPYC")

    # 需要予測タスク実行
    print(f"\n🔄 需要予測実行中...")
    forecast_task = Task(
        description="""
過去3日の販売: 305個、320個、315個
明日: 週末、晴れ

明日の需要を予測してください。
回答: 予測需要: XXX個
        """,
        agent=demand_analyst,
        expected_output="予測需要量"
    )

    forecast_crew = Crew(
        agents=[demand_analyst],
        tasks=[forecast_task],
        verbose=False
    )

    forecast_result = forecast_crew.kickoff()
    print(f"\n✓ 需要予測結果: {forecast_result}")

    # X402決済実行
    print(f"\n💳 X402決済実行中...")
    demand_response = X402Response(
        request_id=demand_request.request_id,
        response_id=f"res-demand-{datetime.now().timestamp()}",
        status="success",
        result={"forecast": str(forecast_result)},
        actual_amount=demand_request.base_amount,
        payment_address=agent_wallets["demand_forecast"],
        execution_time_ms=1000
    )

    demand_tx = x402_client.process_response(demand_request, demand_response)
    print(f"\n✅ 決済完了!")
    print(f"  TX Hash: {demand_tx.tx_hash}")
    print(f"  Amount: {wei_to_jpyc(demand_tx.amount)} JPYC")
    print(f"  Explorer: https://amoy.polygonscan.com/tx/{demand_tx.tx_hash}")

    # トランザクション確認
    print(f"\n🔄 トランザクション確認中...")
    receipt = blockchain_service.wait_for_transaction(demand_tx.tx_hash, timeout=60)
    print(f"✓ Block: {receipt['block_number']}, Gas: {receipt['gas_used']}")

    # ========================================
    # Phase 2: 在庫最適化 + X402決済
    # ========================================
    print("\n" + "=" * 70)
    print("Phase 2: 在庫最適化エージェント + X402決済")
    print("=" * 70)

    # X402リクエスト作成
    inventory_request = x402_client.create_request(
        service_agent_id=2,
        service_description="在庫最適化サービス",
        payment_scheme=agent_fees["inventory_optimizer"]["scheme"],
        base_amount_jpyc=agent_fees["inventory_optimizer"]["amount"]
    )

    print(f"\n✓ X402 Request: {inventory_request.request_id}")

    # 在庫最適化タスク実行
    print(f"\n🔄 在庫最適化実行中...")
    optimize_task = Task(
        description=f"""
需要予測結果: {forecast_result}

サプライヤー:
A農園: 115円、品質95
B農園: 110円、品質88

推奨発注量とサプライヤーを決定。
回答: 発注量: XXX個、サプライヤー: X農園
        """,
        agent=inventory_manager,
        expected_output="発注量とサプライヤー"
    )

    optimize_crew = Crew(
        agents=[inventory_manager],
        tasks=[optimize_task],
        verbose=False
    )

    optimize_result = optimize_crew.kickoff()
    print(f"\n✓ 在庫最適化結果: {optimize_result}")

    # X402決済実行
    print(f"\n💳 X402決済実行中...")
    inventory_response = X402Response(
        request_id=inventory_request.request_id,
        response_id=f"res-inventory-{datetime.now().timestamp()}",
        status="success",
        result={"optimization": str(optimize_result)},
        actual_amount=inventory_request.base_amount,
        payment_address=agent_wallets["inventory_optimizer"],
        execution_time_ms=500
    )

    inventory_tx = x402_client.process_response(inventory_request, inventory_response)
    print(f"\n✅ 決済完了!")
    print(f"  TX Hash: {inventory_tx.tx_hash}")
    print(f"  Explorer: https://amoy.polygonscan.com/tx/{inventory_tx.tx_hash}")

    # トランザクション確認
    print(f"\n🔄 トランザクション確認中...")
    receipt = blockchain_service.wait_for_transaction(inventory_tx.tx_hash, timeout=60)
    print(f"✓ Block: {receipt['block_number']}, Gas: {receipt['gas_used']}")

    # ========================================
    # Phase 3: レポート生成 + X402決済
    # ========================================
    print("\n" + "=" * 70)
    print("Phase 3: レポート生成エージェント + X402決済")
    print("=" * 70)

    # X402リクエスト作成
    report_request = x402_client.create_request(
        service_agent_id=3,
        service_description="レポート生成サービス",
        payment_scheme=agent_fees["report_generator"]["scheme"],
        base_amount_jpyc=agent_fees["report_generator"]["amount"]
    )

    print(f"\n✓ X402 Request: {report_request.request_id}")

    # レポート生成タスク実行
    print(f"\n🔄 レポート生成中...")
    report_task = Task(
        description=f"""
需要予測: {forecast_result}
在庫最適化: {optimize_result}

以下の形式でレポートを作成:
## サプライチェーン最適化レポート
需要: XXX個
発注: XXX個
サプライヤー: X農園
        """,
        agent=report_generator,
        expected_output="レポート"
    )

    report_crew = Crew(
        agents=[report_generator],
        tasks=[report_task],
        verbose=False
    )

    report_result = report_crew.kickoff()
    print(f"\n✓ レポート生成結果:")
    print("-" * 70)
    print(report_result)
    print("-" * 70)

    # X402決済実行
    print(f"\n💳 X402決済実行中...")
    report_response = X402Response(
        request_id=report_request.request_id,
        response_id=f"res-report-{datetime.now().timestamp()}",
        status="success",
        result={"report": str(report_result)},
        actual_amount=report_request.base_amount,
        payment_address=agent_wallets["report_generator"],
        execution_time_ms=800
    )

    report_tx = x402_client.process_response(report_request, report_response)
    print(f"\n✅ 決済完了!")
    print(f"  TX Hash: {report_tx.tx_hash}")
    print(f"  Explorer: https://amoy.polygonscan.com/tx/{report_tx.tx_hash}")

    # トランザクション確認
    print(f"\n🔄 トランザクション確認中...")
    receipt = blockchain_service.wait_for_transaction(report_tx.tx_hash, timeout=60)
    print(f"✓ Block: {receipt['block_number']}, Gas: {receipt['gas_used']}")

    # ========================================
    # 最終サマリー
    # ========================================
    print("\n" + "=" * 70)
    print("✅ E2Eテスト完了!")
    print("=" * 70)

    # X402トランザクションサマリー
    summary = x402_client.get_transaction_summary()
    total_spent = x402_client.get_total_spent()

    print(f"\n💰 X402決済サマリー:")
    print(f"  Total Transactions: {summary['total_transactions']}")
    print(f"  Completed: {summary['completed']}")
    print(f"  Total Spent: {total_spent:.6f} JPYC")
    print(f"\n  By Scheme:")
    print(f"    EXACT: {summary['by_scheme']['exact']} transactions")
    print(f"    UPTO: {summary['by_scheme']['upto']} transactions")
    print(f"    DEFERRED: {summary['by_scheme']['deferred']} transactions")

    # 全トランザクションのExplorerリンク
    print(f"\n🔍 全トランザクション:")
    for tx_id, tx in x402_client.transactions.items():
        print(f"  - {tx.service_agent_id}: {tx.tx_hash}")
        print(f"    https://amoy.polygonscan.com/tx/{tx.tx_hash}")

    # 最終残高
    final_balance = blockchain_service.get_balance()
    print(f"\n📊 最終残高:")
    print(f"  MATIC: {final_balance['matic_balance']:.4f} MATIC")
    print(f"  Used MATIC: {balance['matic_balance'] - final_balance['matic_balance']:.4f} MATIC")

    print("\n" + "=" * 70)
    print("🎉 Phase 4 完了!")
    print("=" * 70)
    print("\n✅ 達成:")
    print("  - LLMエージェント（CrewAI + gemma2:9b）統合")
    print("  - X402プロトコル実決済統合")
    print("  - Polygon Amoyでトランザクション実行")
    print("  - 3エージェント協調 + 3回の実決済成功")
    print("\n🎯 次のステップ（Phase 5）:")
    print("  - UI実装（Next.js + Web3）")
    print("  - Metamask連携")
    print("  - ユーザーダッシュボード")


def main():
    """メイン実行"""
    print("\n⚠️  このテストは3回の実ブロックチェーントランザクションを実行します")
    print("⚠️  ガス代: 約0.003 MATIC")
    print("⚠️  JPYC決済: 0.023 JPYC")
    print("\n実行には5-10分かかる場合があります（LLM推論時間含む）")
    print("\nPress Ctrl+C to cancel, or wait 10 seconds to proceed...")

    import time
    try:
        time.sleep(10)
        test_e2e_with_real_payments()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
