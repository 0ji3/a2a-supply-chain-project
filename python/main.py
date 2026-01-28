"""
メインスクリプト

MVPアプリケーションのエントリーポイント。
"""
import asyncio
import logging
import sys
from datetime import datetime

from database import get_db, test_connection
from orchestrator import AgentCoordinator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def print_banner():
    """バナー表示"""
    print("\n" + "=" * 70)
    print("  A2A Supply Chain Optimization System - MVP")
    print("  生鮮品サプライチェーン最適化AI協調システム")
    print("=" * 70 + "\n")


def print_result(result):
    """結果表示"""
    print("\n" + "=" * 70)
    print("📊 最適化結果レポート")
    print("=" * 70)

    if not result.success:
        print(f"\n❌ エラー: {result.error_message}\n")
        return

    print(f"\n商品: {result.product_sku}")
    print(f"店舗: {result.store_id}")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- 需要予測 ---")
    demand_data = result.demand_forecast.get("data", {})
    print(f"  予測販売数量: {demand_data.get('predicted_demand', 0)} 個")
    ci = demand_data.get("confidence_interval", {})
    print(f"  信頼区間: {ci.get('lower', 0)} ~ {ci.get('upper', 0)} 個")
    print(
        f"  信頼度: {result.demand_forecast.get('confidence', 0) * 100:.1f}%"
    )
    print(f"  コスト: {result.demand_forecast.get('cost', 0)} JPYC")

    print("\n--- 在庫最適化 ---")
    inv_data = result.inventory_optimization.get("data", {})
    print(f"  推奨発注量: {inv_data.get('order_quantity', 0)} 個")
    supplier = inv_data.get("supplier", {})
    print(f"  推奨サプライヤー: {supplier.get('name', 'N/A')}")
    print(f"  単価: {supplier.get('unit_price', 0):.2f} 円")
    print(f"  リードタイム: {supplier.get('lead_time_hours', 0)} 時間")
    print(f"  期待廃棄量: {inv_data.get('expected_waste', 0)} 個")
    print(f"  期待欠品量: {inv_data.get('expected_shortage', 0)} 個")
    print(
        f"  信頼度: {result.inventory_optimization.get('confidence', 0) * 100:.1f}%"
    )
    print(f"  コスト: {result.inventory_optimization.get('cost', 0)} JPYC")

    print("\n--- サマリー ---")
    summary = result.summary
    print(f"  合計コスト: {result.total_cost} JPYC")
    print(f"  実行時間: {result.total_execution_time:.3f} 秒")
    print(f"  総合信頼度: {summary.get('confidence', {}).get('overall', 0) * 100:.1f}%")

    print("\n" + "=" * 70 + "\n")


async def main():
    """メイン処理"""
    print_banner()

    # データベース接続テスト
    logger.info("Testing database connection...")
    if not test_connection():
        logger.error("Database connection failed. Please check your configuration.")
        return

    # データベースセッション取得
    db = next(get_db())

    try:
        # Orchestrator初期化
        coordinator = AgentCoordinator(db)

        # 最適化タスク実行
        logger.info("Starting optimization task...")
        result = await coordinator.execute_optimization_task(
            product_sku="tomato-medium-domestic", store_id="S001"
        )

        # 結果表示
        print_result(result)

        if result.success:
            logger.info("✅ Optimization completed successfully!")
        else:
            logger.error("❌ Optimization failed!")

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
