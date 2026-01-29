"""
LLMエージェント + X402決済 統合テスト

エージェント実行と決済フローを統合した実践的なテスト
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any

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


class AgentWithPayment:
    """
    X402決済を統合したエージェントラッパー

    Phase 3ではモック実装、Phase 4で実際のLLMエージェントを統合
    """

    def __init__(
        self,
        agent_id: int,
        agent_name: str,
        payment_scheme: PaymentScheme,
        base_cost_jpyc: float,
        max_cost_jpyc: float = None,
        payment_address: str = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.payment_scheme = payment_scheme
        self.base_cost_jpyc = base_cost_jpyc
        self.max_cost_jpyc = max_cost_jpyc
        self.payment_address = payment_address or f"0xAgent{agent_id:040x}"

    def execute(self, task_description: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        エージェントタスクを実行（Phase 3ではモック）

        Args:
            task_description: タスクの説明
            input_data: 入力データ

        Returns:
            実行結果と使用量メトリクス
        """
        print(f"\n🤖 {self.agent_name} - タスク実行中...")
        print(f"   タスク: {task_description}")

        # Phase 3: モック実装（Phase 4で実際のLLMエージェントに置き換え）
        if self.agent_id == 1:
            # 需要予測エージェント
            result = {
                "predicted_demand": 340,
                "confidence_interval": [325, 355],
                "std_dev": 15,
                "trend": "stable"
            }
            usage_metrics = {"records_processed": 2000}
            execution_time_ms = 1200

        elif self.agent_id == 2:
            # 在庫最適化エージェント
            result = {
                "optimal_order_quantity": 340,
                "expected_profit": 12500,
                "selected_supplier": "サプライヤーA",
                "supplier_quality_score": 95
            }
            usage_metrics = {}
            execution_time_ms = 500

        elif self.agent_id == 3:
            # レポート生成エージェント
            result = {
                "report_summary": "渋谷店トマト最適化レポート",
                "report_sections": [
                    "需要予測結果",
                    "在庫最適化提案",
                    "期待効果"
                ]
            }
            usage_metrics = {}
            execution_time_ms = 800

        else:
            result = {"status": "completed"}
            usage_metrics = {}
            execution_time_ms = 100

        print(f"   ✓ 実行完了（{execution_time_ms}ms）")

        return {
            "status": "success",
            "result": result,
            "usage_metrics": usage_metrics,
            "execution_time_ms": execution_time_ms
        }

    def calculate_actual_cost(self, usage_metrics: Dict[str, Any]) -> float:
        """
        使用量に基づいて実際のコストを計算

        Args:
            usage_metrics: 使用量メトリクス

        Returns:
            実際のコスト（JPYC）
        """
        if self.payment_scheme == PaymentScheme.EXACT:
            # 固定料金
            return self.base_cost_jpyc

        elif self.payment_scheme == PaymentScheme.UPTO:
            # 従量課金（需要予測: 3 JPYC + 0.02 JPYC/1000レコード）
            records = usage_metrics.get("records_processed", 0)
            variable_cost = (records / 1000) * 0.02
            return self.base_cost_jpyc + variable_cost

        elif self.payment_scheme == PaymentScheme.DEFERRED:
            # 後払い（固定）
            return self.base_cost_jpyc

        return self.base_cost_jpyc


def test_supply_chain_optimization_with_x402():
    """
    サプライチェーン最適化フロー + X402決済の統合テスト
    """
    print("\n" + "=" * 60)
    print("サプライチェーン最適化 + X402決済 統合テスト")
    print("=" * 60)

    # テストパラメータ
    product_sku = "TOMATO-001"
    product_name = "トマト"
    store_name = "渋谷店"
    weather = "晴れ"
    day_type = "週末"

    print(f"\n📊 テストパラメータ:")
    print(f"   店舗: {store_name}")
    print(f"   商品: {product_name} (SKU: {product_sku})")
    print(f"   明日の天気: {weather}")
    print(f"   明日のタイプ: {day_type}")

    # X402クライアント初期化（店舗エージェント ID: 0）
    x402_client = X402Client(client_agent_id=0)

    print(f"\n✓ X402クライアント初期化完了（Agent ID: 0）")

    # エージェント定義
    agents = [
        AgentWithPayment(
            agent_id=1,
            agent_name="需要予測エージェント",
            payment_scheme=PaymentScheme.UPTO,
            base_cost_jpyc=3.0,
            max_cost_jpyc=10.0,
            payment_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
        ),
        AgentWithPayment(
            agent_id=2,
            agent_name="在庫最適化エージェント",
            payment_scheme=PaymentScheme.EXACT,
            base_cost_jpyc=15.0,
            payment_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        ),
        AgentWithPayment(
            agent_id=3,
            agent_name="レポート生成エージェント",
            payment_scheme=PaymentScheme.DEFERRED,
            base_cost_jpyc=5.0,
            payment_address="0x90F79bf6EB2c4f870365E785982E1f101E93b906"
        )
    ]

    print(f"\n✓ 3つのエージェント定義完了")
    for agent in agents:
        print(f"   - {agent.agent_name} ({agent.payment_scheme.value})")

    # フェーズ1: 需要予測
    print("\n" + "-" * 60)
    print("Phase 1: 需要予測")
    print("-" * 60)

    demand_agent = agents[0]

    # X402リクエスト作成
    demand_request = x402_client.create_request(
        service_agent_id=demand_agent.agent_id,
        service_description=f"{product_name}の需要予測",
        payment_scheme=demand_agent.payment_scheme,
        base_amount_jpyc=demand_agent.base_cost_jpyc,
        max_amount_jpyc=demand_agent.max_cost_jpyc,
        metadata={"product_sku": product_sku, "weather": weather, "day_type": day_type}
    )

    # エージェント実行
    demand_execution = demand_agent.execute(
        task_description=f"{product_name}の明日の需要を予測",
        input_data={"product_sku": product_sku, "weather": weather, "day_type": day_type}
    )

    # 実際のコストを計算
    demand_actual_cost = demand_agent.calculate_actual_cost(
        demand_execution["usage_metrics"]
    )

    # X402レスポンス作成
    demand_response = X402Response(
        request_id=demand_request.request_id,
        response_id=f"res-demand-{demand_request.request_id[4:12]}",
        status=demand_execution["status"],
        result=demand_execution["result"],
        actual_amount=jpyc_to_wei(demand_actual_cost),
        payment_address=demand_agent.payment_address,
        execution_time_ms=demand_execution["execution_time_ms"],
        usage_metrics=demand_execution["usage_metrics"]
    )

    # 決済実行
    demand_tx = x402_client.process_response(demand_request, demand_response)

    print(f"\n💰 決済完了:")
    print(f"   Amount: {wei_to_jpyc(demand_tx.amount)} JPYC")
    print(f"   TX Hash: {demand_tx.tx_hash}")

    # 需要予測結果を保存
    predicted_demand = demand_execution["result"]["predicted_demand"]
    demand_std = demand_execution["result"]["std_dev"]

    print(f"\n📈 需要予測結果:")
    print(f"   予測需要: {predicted_demand}個")
    print(f"   標準偏差: {demand_std}個")

    # フェーズ2: 在庫最適化
    print("\n" + "-" * 60)
    print("Phase 2: 在庫最適化")
    print("-" * 60)

    inventory_agent = agents[1]

    # X402リクエスト作成
    inventory_request = x402_client.create_request(
        service_agent_id=inventory_agent.agent_id,
        service_description=f"{product_name}の在庫最適化",
        payment_scheme=inventory_agent.payment_scheme,
        base_amount_jpyc=inventory_agent.base_cost_jpyc,
        metadata={
            "product_sku": product_sku,
            "predicted_demand": predicted_demand,
            "demand_std": demand_std
        }
    )

    # エージェント実行
    inventory_execution = inventory_agent.execute(
        task_description=f"{product_name}の最適発注量を計算",
        input_data={
            "product_sku": product_sku,
            "predicted_demand": predicted_demand,
            "demand_std": demand_std
        }
    )

    # 実際のコストを計算
    inventory_actual_cost = inventory_agent.calculate_actual_cost(
        inventory_execution["usage_metrics"]
    )

    # X402レスポンス作成
    inventory_response = X402Response(
        request_id=inventory_request.request_id,
        response_id=f"res-inventory-{inventory_request.request_id[4:12]}",
        status=inventory_execution["status"],
        result=inventory_execution["result"],
        actual_amount=jpyc_to_wei(inventory_actual_cost),
        payment_address=inventory_agent.payment_address,
        execution_time_ms=inventory_execution["execution_time_ms"]
    )

    # 決済実行
    inventory_tx = x402_client.process_response(inventory_request, inventory_response)

    print(f"\n💰 決済完了:")
    print(f"   Amount: {wei_to_jpyc(inventory_tx.amount)} JPYC")
    print(f"   TX Hash: {inventory_tx.tx_hash}")

    # 在庫最適化結果を保存
    optimal_quantity = inventory_execution["result"]["optimal_order_quantity"]
    expected_profit = inventory_execution["result"]["expected_profit"]

    print(f"\n📦 在庫最適化結果:")
    print(f"   最適発注量: {optimal_quantity}個")
    print(f"   期待利益: {expected_profit:,}円")

    # フェーズ3: レポート生成
    print("\n" + "-" * 60)
    print("Phase 3: レポート生成")
    print("-" * 60)

    report_agent = agents[2]

    # X402リクエスト作成
    report_request = x402_client.create_request(
        service_agent_id=report_agent.agent_id,
        service_description=f"{store_name} {product_name}最適化レポート",
        payment_scheme=report_agent.payment_scheme,
        base_amount_jpyc=report_agent.base_cost_jpyc,
        metadata={
            "store_name": store_name,
            "product_name": product_name,
            "predicted_demand": predicted_demand,
            "optimal_quantity": optimal_quantity
        }
    )

    # エージェント実行
    report_execution = report_agent.execute(
        task_description=f"{store_name}向け最適化レポートを生成",
        input_data={
            "store_name": store_name,
            "product_name": product_name,
            "demand_result": demand_execution["result"],
            "inventory_result": inventory_execution["result"]
        }
    )

    # 実際のコストを計算
    report_actual_cost = report_agent.calculate_actual_cost(
        report_execution["usage_metrics"]
    )

    # X402レスポンス作成
    report_response = X402Response(
        request_id=report_request.request_id,
        response_id=f"res-report-{report_request.request_id[4:12]}",
        status=report_execution["status"],
        result=report_execution["result"],
        actual_amount=jpyc_to_wei(report_actual_cost),
        payment_address=report_agent.payment_address,
        execution_time_ms=report_execution["execution_time_ms"]
    )

    # 決済実行
    report_tx = x402_client.process_response(report_request, report_response)

    print(f"\n💰 決済完了:")
    print(f"   Amount: {wei_to_jpyc(report_tx.amount)} JPYC")
    print(f"   TX Hash: {report_tx.tx_hash}")

    print(f"\n📄 レポート生成完了:")
    print(f"   {report_execution['result']['report_summary']}")

    # 総コスト集計
    print("\n" + "=" * 60)
    print("総コスト集計")
    print("=" * 60)

    summary = x402_client.get_transaction_summary()
    total_spent = x402_client.get_total_spent()

    print(f"\n💳 決済サマリー:")
    print(f"   Total Transactions: {summary['total_transactions']}")
    print(f"   Completed: {summary['completed']}")
    print(f"   Total Spent: {total_spent:.2f} JPYC")
    print(f"\n   内訳:")
    print(f"   - 需要予測 (UPTO): {wei_to_jpyc(demand_tx.amount):.2f} JPYC")
    print(f"   - 在庫最適化 (EXACT): {wei_to_jpyc(inventory_tx.amount):.2f} JPYC")
    print(f"   - レポート生成 (DEFERRED): {wei_to_jpyc(report_tx.amount):.2f} JPYC")

    # アサーション
    assert summary['completed'] == 3
    assert summary['failed'] == 0
    expected_total = demand_actual_cost + inventory_actual_cost + report_actual_cost
    assert abs(total_spent - expected_total) < 0.01

    print("\n" + "=" * 60)
    print("✅ 統合テスト成功！")
    print("=" * 60)
    print("\n🎯 Phase 3 Step 4完了:")
    print("   ✓ エージェント実行フロー")
    print("   ✓ X402決済統合")
    print("   ✓ 3つの決済スキーム（EXACT, UPTO, DEFERRED）")
    print("   ✓ トランザクション追跡")
    print("\n次のステップ: Phase 4でブロックチェーン統合")


def main():
    """メイン関数"""
    try:
        test_supply_chain_optimization_with_x402()
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
