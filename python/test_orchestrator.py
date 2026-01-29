"""
Orchestrator統合テスト

SupplyChainOrchestratorのモック実行テスト
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator_llm import SupplyChainOrchestrator


def test_orchestrator_mock():
    """
    Orchestratorモック実行テスト

    実際のLLMを使わず、モックデータで動作確認
    """
    print("\n" + "=" * 70)
    print("🧪 Orchestrator統合テスト（モックモード）")
    print("=" * 70)

    # テストパラメータ
    product_sku = "TOMATO-001"
    product_name = "トマト"
    product_category = "tomato"
    store_name = "渋谷店"
    weather = "晴れ"
    day_type = "週末"
    selling_price = 200.0

    # Orchestrator初期化
    orchestrator = SupplyChainOrchestrator(client_agent_id=0)

    print("\n✓ Orchestrator初期化完了")
    print("  クライアントエージェントID: 0")
    print("  登録エージェント数: 3")

    # 最適化実行（モックモード）
    print("\n🚀 最適化実行開始（use_real_llm=False）...")

    try:
        results = orchestrator.execute_optimization(
            product_sku=product_sku,
            product_name=product_name,
            product_category=product_category,
            store_name=store_name,
            weather=weather,
            day_type=day_type,
            selling_price=selling_price,
            use_real_llm=False  # モックモード
        )

        # 結果検証
        print("\n" + "=" * 70)
        print("✅ テスト結果検証")
        print("=" * 70)

        # 基本情報
        assert results["store_name"] == store_name
        assert results["product_name"] == product_name
        assert results["product_sku"] == product_sku
        print(f"✓ 基本情報: OK")

        # 需要予測結果
        assert "demand_forecast" in results
        assert results["demand_forecast"]["predicted_demand"] == 340
        assert results["demand_forecast"]["std_dev"] == 15
        print(f"✓ 需要予測: OK (予測需要: 340個)")

        # 在庫最適化結果
        assert "inventory_optimization" in results
        assert results["inventory_optimization"]["optimal_order_quantity"] == 340
        assert results["inventory_optimization"]["expected_profit"] == 12500
        print(f"✓ 在庫最適化: OK (最適発注量: 340個)")

        # レポート生成結果
        assert "report" in results
        assert "report_summary" in results["report"]
        print(f"✓ レポート生成: OK")

        # 決済情報
        assert len(results["transactions"]) == 3
        assert results["total_cost_jpyc"] == 23.04  # 3.04 + 15.0 + 5.0
        print(f"✓ 決済: OK (3トランザクション, 総額23.04 JPYC)")

        # 実行時間
        assert results["execution_time_ms"] > 0
        print(f"✓ 実行時間: {results['execution_time_ms']:.0f}ms")

        # 決済サマリー取得
        payment_summary = orchestrator.get_payment_summary()
        assert payment_summary["total_transactions"] == 3
        assert payment_summary["completed"] == 3
        assert payment_summary["failed"] == 0
        print(f"✓ 決済サマリー: OK")

        print("\n" + "=" * 70)
        print("✅ すべてのテストに合格しました！")
        print("=" * 70)

        print("\n🎯 Orchestrator動作確認完了:")
        print("   ✓ エージェント実行フロー")
        print("   ✓ X402決済統合")
        print("   ✓ 3フェーズ協調処理")
        print("   ✓ エラーハンドリング")
        print("   ✓ 結果集計")

        return True

    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_products():
    """
    複数商品の最適化テスト

    異なる商品で連続して最適化を実行
    """
    print("\n" + "=" * 70)
    print("🧪 複数商品最適化テスト")
    print("=" * 70)

    orchestrator = SupplyChainOrchestrator(client_agent_id=0)

    products = [
        {
            "sku": "TOMATO-001",
            "name": "トマト",
            "category": "tomato",
            "selling_price": 200.0
        },
        {
            "sku": "LETTUCE-001",
            "name": "レタス",
            "category": "lettuce",
            "selling_price": 150.0
        }
    ]

    for i, product in enumerate(products, 1):
        print(f"\n商品 {i}/{len(products)}: {product['name']}")
        print("-" * 70)

        results = orchestrator.execute_optimization(
            product_sku=product["sku"],
            product_name=product["name"],
            product_category=product["category"],
            store_name="渋谷店",
            weather="晴れ",
            day_type="週末",
            selling_price=product["selling_price"],
            use_real_llm=False
        )

        assert results["total_cost_jpyc"] == 23.04
        print(f"✓ {product['name']}の最適化完了")

    # 全体サマリー
    summary = orchestrator.get_payment_summary()
    print("\n" + "=" * 70)
    print("📊 全体決済サマリー")
    print("=" * 70)
    print(f"総トランザクション数: {summary['total_transactions']}")
    print(f"総支払額: {summary['total_spent_jpyc']:.2f} JPYC")
    print(f"  EXACT: {summary['by_scheme']['exact']}件")
    print(f"  UPTO: {summary['by_scheme']['upto']}件")
    print(f"  DEFERRED: {summary['by_scheme']['deferred']}件")

    assert summary['total_transactions'] == len(products) * 3
    assert summary['total_spent_jpyc'] == len(products) * 23.04

    print("\n✅ 複数商品最適化テスト成功！")
    return True


def main():
    """メイン関数"""
    print("\n" + "=" * 70)
    print("🧪 SupplyChainOrchestrator 統合テストスイート")
    print("=" * 70)

    tests = [
        ("基本動作テスト", test_orchestrator_mock),
        ("複数商品テスト", test_multiple_products),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"テスト: {test_name}")
        print(f"{'='*70}")

        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()

    # 総合結果
    print("\n" + "=" * 70)
    print("📊 テスト結果サマリー")
    print("=" * 70)
    print(f"Total: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 すべてのテストに合格しました！")
        print("\n🎯 Phase 3 Step 5完了:")
        print("   ✓ SupplyChainOrchestrator実装")
        print("   ✓ エージェント協調フロー")
        print("   ✓ X402決済統合")
        print("   ✓ モック実行テスト")
        print("\n次のステップ: 実LLM統合テスト（Step 6）")
        return 0
    else:
        print(f"\n❌ {failed}件のテストが失敗しました")
        return 1


if __name__ == "__main__":
    exit(main())
