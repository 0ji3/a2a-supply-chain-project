"""
データベースツール

販売履歴やサプライヤー情報を取得するツール
"""
from typing import Dict, List
from crewai.tools import tool
import os


@tool("Get Sales History")
def get_sales_history(product_sku: str, days: int = 7) -> str:
    """
    指定商品の過去の販売履歴を取得する

    Args:
        product_sku: 商品SKU
        days: 取得日数（デフォルト7日）

    Returns:
        販売履歴の文字列表現
    """
    # Phase 3ではモックデータを返す
    # Phase 4以降で実際のデータベース接続を実装

    mock_data = {
        "TOMATO-001": [
            {"date": "2026-01-22", "quantity": 285, "price": 200},
            {"date": "2026-01-23", "quantity": 295, "price": 200},
            {"date": "2026-01-24", "quantity": 310, "price": 200},
            {"date": "2026-01-25", "quantity": 300, "price": 200},
            {"date": "2026-01-26", "quantity": 305, "price": 200},
            {"date": "2026-01-27", "quantity": 320, "price": 200},
            {"date": "2026-01-28", "quantity": 315, "price": 200},
        ]
    }

    if product_sku not in mock_data:
        return f"商品SKU {product_sku} のデータが見つかりません"

    sales_data = mock_data[product_sku][-days:]

    # フォーマットして返す
    result = f"商品SKU: {product_sku}\n"
    result += f"過去{days}日間の販売履歴:\n\n"

    for record in sales_data:
        result += f"日付: {record['date']}, 販売数: {record['quantity']}個, 単価: {record['price']}円\n"

    # 統計情報を追加
    total_qty = sum(r["quantity"] for r in sales_data)
    avg_qty = total_qty / len(sales_data)
    result += f"\n平均販売数: {avg_qty:.1f}個/日"

    return result


@tool("Get Supplier Information")
def get_supplier_info(product_category: str = "tomato") -> str:
    """
    商品カテゴリのサプライヤー情報を取得する

    Args:
        product_category: 商品カテゴリ

    Returns:
        サプライヤー情報の文字列表現
    """
    # Phase 3ではモックデータを返す

    mock_suppliers = {
        "tomato": [
            {
                "name": "静岡農協",
                "unit_price": 120,
                "lead_time_hours": 8,
                "quality_score": 89,
                "reliability": 95
            },
            {
                "name": "千葉ファーム",
                "unit_price": 115,
                "lead_time_hours": 12,
                "quality_score": 85,
                "reliability": 88
            },
            {
                "name": "神奈川野菜センター",
                "unit_price": 125,
                "lead_time_hours": 6,
                "quality_score": 92,
                "reliability": 90
            }
        ]
    }

    if product_category not in mock_suppliers:
        return f"カテゴリ {product_category} のサプライヤー情報が見つかりません"

    suppliers = mock_suppliers[product_category]

    result = f"商品カテゴリ: {product_category}\n"
    result += f"利用可能なサプライヤー: {len(suppliers)}社\n\n"

    for i, supplier in enumerate(suppliers, 1):
        result += f"{i}. {supplier['name']}\n"
        result += f"   仕入れ単価: {supplier['unit_price']}円\n"
        result += f"   リードタイム: {supplier['lead_time_hours']}時間\n"
        result += f"   品質スコア: {supplier['quality_score']}%\n"
        result += f"   信頼性: {supplier['reliability']}%\n\n"

    return result
