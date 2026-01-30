"""
需要予測LLMエージェント

過去の販売データから需要を予測するLLMエージェント
"""
import os
from crewai import Agent, LLM
from agents.tools import get_sales_history


def create_demand_forecast_agent() -> Agent:
    """
    需要予測エージェントを作成

    Returns:
        需要予測Agent
    """
    # Ollama LLMを設定
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    os.environ["OLLAMA_API_BASE"] = ollama_url

    llm = LLM(
        model="ollama/gemma2:2b",
        base_url=ollama_url
    )

    agent = Agent(
        role="需要予測アナリスト",
        goal="過去の販売データから正確な需要予測を行い、信頼区間を提示する",
        backstory="""
        あなたは10年以上の経験を持つ需要予測の専門家です。
        スーパーマーケットの生鮮品販売において、季節性、天候、曜日、イベントなどの
        多様な要因を考慮した高精度な需要予測を行ってきました。

        あなたの予測は在庫最適化の基礎となり、食品ロス削減と欠品防止に貢献します。
        統計的手法とドメイン知識を組み合わせ、実用的な予測値と信頼区間を提供します。
        """,
        llm=llm,
        tools=[get_sales_history],
        verbose=True,
        allow_delegation=False,
        max_iter=5  # 無限ループ防止
    )

    return agent


def create_demand_forecast_task(agent: Agent, product_sku: str, weather: str, day_type: str):
    """
    需要予測タスクを作成

    Args:
        agent: 需要予測Agent
        product_sku: 商品SKU
        weather: 明日の天気
        day_type: 明日の曜日タイプ（平日/週末）

    Returns:
        Task
    """
    from crewai import Task

    description = f"""
    商品SKU「{product_sku}」の明日の需要を予測してください。

    条件:
    - 明日の天気: {weather}
    - 明日のタイプ: {day_type}

    タスク手順:
    1. get_sales_history ツールを使って過去7日間の販売履歴を取得
    2. 販売トレンド（増加/減少/安定）を分析
    3. 天気と曜日タイプの影響を考慮
    4. 需要の予測値（平均）と信頼区間（上限・下限）を算出
    5. 予測の根拠を説明

    出力形式:
    - 予測需要（個数）: XXX個
    - 信頼区間: [下限, 上限]
    - 標準偏差: XX個
    - 予測根拠: （簡潔に説明）
    """

    expected_output = """
    以下の情報を含む需要予測結果:
    1. 予測需要量（個数）
    2. 信頼区間（95%信頼区間）
    3. 需要の標準偏差
    4. 予測の根拠（トレンド分析、天候・曜日の影響など）
    """

    task = Task(
        description=description,
        agent=agent,
        expected_output=expected_output
    )

    return task
