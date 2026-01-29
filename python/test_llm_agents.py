"""
LLMエージェント統合テスト

需要予測、在庫最適化、レポート生成の3つのエージェントを連携させるテスト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))


def test_llm_agents_integration():
    """LLMエージェント統合テスト"""

    print("=" * 60)
    print("LLMエージェント統合テスト")
    print("=" * 60)

    try:
        from crewai import Crew
        from agents.llm import (
            create_demand_forecast_agent,
            create_inventory_optimizer_agent,
            create_report_generator_agent,
        )
        from agents.llm.demand_forecast_llm import create_demand_forecast_task
        from agents.llm.inventory_optimizer_llm import create_inventory_optimization_task
        from agents.llm.report_generator_llm import create_report_generation_task

        # テストパラメータ
        product_sku = "TOMATO-001"
        product_name = "トマト"
        product_category = "tomato"
        store_name = "渋谷店"
        weather = "晴れ"
        day_type = "週末"
        selling_price = 200
        disposal_cost = 120
        shortage_cost = 80

        print("\n📊 テストパラメータ:")
        print(f"   店舗: {store_name}")
        print(f"   商品: {product_name} (SKU: {product_sku})")
        print(f"   明日の天気: {weather}")
        print(f"   明日のタイプ: {day_type}")
        print(f"   販売単価: {selling_price}円")

        # エージェント作成
        print("\n1. エージェントを作成...")
        demand_agent = create_demand_forecast_agent()
        print("   ✓ 需要予測エージェント作成完了")

        inventory_agent = create_inventory_optimizer_agent()
        print("   ✓ 在庫最適化エージェント作成完了")

        report_agent = create_report_generator_agent()
        print("   ✓ レポート生成エージェント作成完了")

        # タスク作成
        print("\n2. タスクを作成...")
        demand_task = create_demand_forecast_task(
            agent=demand_agent,
            product_sku=product_sku,
            weather=weather,
            day_type=day_type
        )
        print("   ✓ 需要予測タスク作成完了")

        inventory_task = create_inventory_optimization_task(
            agent=inventory_agent,
            product_category=product_category,
            selling_price=selling_price,
            disposal_cost=disposal_cost,
            shortage_cost=shortage_cost
        )
        print("   ✓ 在庫最適化タスク作成完了")

        report_task = create_report_generation_task(
            agent=report_agent,
            store_name=store_name,
            product_name=product_name
        )
        print("   ✓ レポート生成タスク作成完了")

        # Crew編成
        print("\n3. Crewを編成...")
        supply_chain_crew = Crew(
            agents=[demand_agent, inventory_agent, report_agent],
            tasks=[demand_task, inventory_task, report_task],
            verbose=True
        )
        print("   ✓ Crew編成完了（3エージェント、3タスク）")

        # Crew実行
        print("\n4. Crewを実行中...")
        print("   （LLM推論に数分かかる場合があります）")
        print("-" * 60)

        result = supply_chain_crew.kickoff()

        print("-" * 60)
        print("\n5. ✅ Crew実行完了！")

        # 結果を表示
        print("\n" + "=" * 60)
        print("最終レポート")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # 結果をファイルに保存
        output_dir = Path(__file__).parent.parent / "reports"
        output_dir.mkdir(exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"supply_chain_report_{timestamp}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(str(result))

        print(f"\n📄 レポート保存: {report_file}")

        print("\n" + "=" * 60)
        print("✓ LLMエージェント統合テスト成功！")
        print("=" * 60)

    except ImportError as e:
        print(f"\n✗ エラー: 必要なパッケージがインストールされていません")
        print(f"   {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_llm_agents_integration()
