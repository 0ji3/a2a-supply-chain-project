"""
在庫最適化LLMエージェント

需要予測を基に最適な発注量を決定するLLMエージェント
"""
import os
from crewai import Agent, LLM
from agents.tools import get_supplier_info, calculate_optimal_order_quantity


def create_inventory_optimizer_agent() -> Agent:
    """
    在庫最適化エージェントを作成

    Returns:
        在庫最適化Agent
    """
    # Ollama LLMを設定
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    os.environ["OLLAMA_API_BASE"] = ollama_url

    llm = LLM(
        model="ollama/gemma2:9b",
        base_url=ollama_url
    )

    agent = Agent(
        role="在庫最適化マネージャー",
        goal="需要予測を基に最適な発注量を決定し、コストを最小化する",
        backstory="""
        あなたは効率的な在庫管理のプロフェッショナルです。
        スーパーマーケットの生鮮品において、廃棄ロスと欠品のバランスを取り、
        利益を最大化する発注戦略を立案してきました。

        ニュースベンダーモデルなどの最適化理論を駆使し、
        需要の不確実性を考慮した科学的な意思決定を行います。
        サプライヤーの選定も含め、総合的なコスト最適化を実現します。
        """,
        llm=llm,
        tools=[get_supplier_info, calculate_optimal_order_quantity],
        verbose=True,
        allow_delegation=False,
        max_iter=5  # 無限ループ防止
    )

    return agent


def create_inventory_optimization_task(
    agent: Agent,
    product_category: str,
    selling_price: float,
    disposal_cost: float,
    shortage_cost: float
):
    """
    在庫最適化タスクを作成

    Args:
        agent: 在庫最適化Agent
        product_category: 商品カテゴリ
        selling_price: 販売単価
        disposal_cost: 廃棄コスト
        shortage_cost: 欠品機会損失

    Returns:
        Task
    """
    from crewai import Task

    description = f"""
    需要予測結果を基に、最適な発注量を決定してください。

    商品情報:
    - 商品カテゴリ: {product_category}
    - 販売単価: {selling_price}円
    - 廃棄コスト: {disposal_cost}円
    - 欠品機会損失: {shortage_cost}円

    タスク手順:
    1. 前タスク（需要予測）の結果から、需要の平均と標準偏差を抽出
    2. get_supplier_info ツールでサプライヤー情報を取得
    3. サプライヤーを品質・価格・リードタイムで評価
    4. 最適なサプライヤーを選定
    5. calculate_optimal_order_quantity ツールで最適発注量を計算
       - demand_mean: 需要平均
       - demand_std: 需要標準偏差
       - unit_cost: 選定したサプライヤーの仕入れ単価
       - selling_price: {selling_price}
       - disposal_cost: {disposal_cost}
       - shortage_cost: {shortage_cost}
    6. 結果を解釈し、意思決定の理由を説明

    出力形式:
    - 推奨発注量: XXX個
    - 選定サプライヤー: サプライヤー名
    - 期待利益: ¥XXX,XXX
    - 意思決定の理由: （簡潔に説明）
    """

    expected_output = """
    以下の情報を含む在庫最適化結果:
    1. 推奨発注量（個数）
    2. 選定したサプライヤー名と選定理由
    3. 期待利益
    4. 期待廃棄数と期待欠品数
    5. 意思決定の理由（コスト分析、リスク評価など）
    """

    task = Task(
        description=description,
        agent=agent,
        expected_output=expected_output
    )

    return task
