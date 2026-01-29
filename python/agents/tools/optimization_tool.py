"""
最適化ツール

在庫最適化の計算を行うツール
"""
from typing import Dict
from crewai.tools import tool
import math


@tool("Calculate Optimal Order Quantity")
def calculate_optimal_order_quantity(
    demand_mean: float,
    demand_std: float,
    unit_cost: float,
    selling_price: float,
    disposal_cost: float,
    shortage_cost: float
) -> str:
    """
    ニュースベンダーモデルで最適発注量を計算する

    Args:
        demand_mean: 需要の平均
        demand_std: 需要の標準偏差
        unit_cost: 仕入れ単価
        selling_price: 販売単価
        disposal_cost: 廃棄コスト
        shortage_cost: 欠品機会損失

    Returns:
        最適発注量と期待値の文字列表現
    """
    try:
        # クリティカルレシオを計算
        # CR = (selling_price - unit_cost + shortage_cost) / (selling_price - unit_cost + shortage_cost + disposal_cost)
        numerator = selling_price - unit_cost + shortage_cost
        denominator = selling_price - unit_cost + shortage_cost + disposal_cost

        if denominator == 0:
            return "エラー: 無効なコストパラメータ"

        critical_ratio = numerator / denominator

        # 正規分布の逆関数を使って最適発注量を計算
        # 簡易的な近似計算（scipy不使用）
        z_score = approximate_inverse_normal_cdf(critical_ratio)
        optimal_quantity = demand_mean + z_score * demand_std

        # 整数に丸める
        optimal_quantity = round(optimal_quantity)

        # 期待値を計算
        expected_sales = min(optimal_quantity, demand_mean)
        expected_waste = max(0, optimal_quantity - demand_mean)
        expected_shortage = max(0, demand_mean - optimal_quantity)

        expected_revenue = expected_sales * selling_price
        expected_cost = optimal_quantity * unit_cost
        expected_disposal = expected_waste * disposal_cost
        expected_shortage_loss = expected_shortage * shortage_cost
        expected_profit = expected_revenue - expected_cost - expected_disposal - expected_shortage_loss

        # 結果をフォーマット
        result = "【最適発注量計算結果】\n\n"
        result += f"最適発注量: {optimal_quantity}個\n\n"
        result += "期待値:\n"
        result += f"  販売数: {expected_sales:.1f}個\n"
        result += f"  廃棄数: {expected_waste:.1f}個\n"
        result += f"  欠品数: {expected_shortage:.1f}個\n\n"
        result += f"期待売上: ¥{expected_revenue:,.0f}\n"
        result += f"期待コスト: ¥{expected_cost:,.0f}\n"
        result += f"期待廃棄損: ¥{expected_disposal:,.0f}\n"
        result += f"期待欠品損: ¥{expected_shortage_loss:,.0f}\n"
        result += f"期待利益: ¥{expected_profit:,.0f}\n\n"
        result += f"クリティカルレシオ: {critical_ratio:.3f}\n"

        return result

    except Exception as e:
        return f"計算エラー: {str(e)}"


def approximate_inverse_normal_cdf(p: float) -> float:
    """
    正規分布の累積分布関数の逆関数の近似計算

    Args:
        p: 確率 (0 < p < 1)

    Returns:
        z値
    """
    if p <= 0 or p >= 1:
        raise ValueError("確率pは0と1の間でなければなりません")

    # 簡易的な近似（Beasley-Springer-Moro approximation）
    a = [
        2.50662823884,
        -18.61500062529,
        41.39119773534,
        -25.44106049637
    ]

    b = [
        -8.47351093090,
        23.08336743743,
        -21.06224101826,
        3.13082909833
    ]

    c = [
        0.3374754822726147,
        0.9761690190917186,
        0.1607979714918209,
        0.0276438810333863,
        0.0038405729373609,
        0.0003951896511919,
        0.0000321767881768,
        0.0000002888167364,
        0.0000003960315187
    ]

    if p < 0.5:
        # 下側
        q = p
        sign = -1.0
    else:
        # 上側
        q = 1.0 - p
        sign = 1.0

    if q > 0.02425:
        # 中央領域
        q = q - 0.5
        r = q * q
        z = (((a[3] * r + a[2]) * r + a[1]) * r + a[0]) * q / ((((b[3] * r + b[2]) * r + b[1]) * r + b[0]) * r + 1.0)
    else:
        # 末端領域
        r = math.sqrt(-math.log(q))
        z = (((((((c[8] * r + c[7]) * r + c[6]) * r + c[5]) * r + c[4]) * r + c[3]) * r + c[2]) * r + c[1]) * r + c[0]

    return sign * z
