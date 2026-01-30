"""
レポート生成LLMエージェント

最適化結果を分かりやすくレポート化するLLMエージェント
"""
import os
from crewai import Agent, LLM


def create_report_generator_agent() -> Agent:
    """
    レポート生成エージェントを作成

    Returns:
        レポート生成Agent
    """
    # Ollama LLMを設定
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    os.environ["OLLAMA_API_BASE"] = ollama_url

    llm = LLM(
        model="ollama/gemma2:2b",
        base_url=ollama_url
    )

    agent = Agent(
        role="レポートジェネレーター",
        goal="複雑な分析結果を分かりやすいレポートにまとめる",
        backstory="""
        あなたはビジネスコミュニケーションのエキスパートです。
        技術的な分析結果を、経営者やマネージャーが理解しやすい
        簡潔で明確なレポートに変換するスキルを持っています。

        数値だけでなく、ビジネスインパクトや実行可能な推奨事項を
        明示することで、意思決定を支援します。
        日本語の自然な表現で、視覚的にも読みやすいレポートを作成します。
        """,
        llm=llm,
        tools=[],  # レポート生成にツールは不要
        verbose=True,
        allow_delegation=False,
        max_iter=3  # シンプルなタスクなので少なめ
    )

    return agent


def create_report_generation_task(agent: Agent, store_name: str, product_name: str):
    """
    レポート生成タスクを作成

    Args:
        agent: レポート生成Agent
        store_name: 店舗名
        product_name: 商品名

    Returns:
        Task
    """
    from crewai import Task

    description = f"""
    需要予測と在庫最適化の結果を統合し、実行可能なレポートを作成してください。

    対象:
    - 店舗: {store_name}
    - 商品: {product_name}

    タスク手順:
    1. 前タスク（需要予測、在庫最適化）の結果を統合
    2. エグゼクティブサマリーを作成（3-5文）
    3. 主要な数値指標を整理
    4. 実行推奨事項を箇条書きで提示
    5. 期待される効果を定量的に説明

    レポート構成:
    1. エグゼクティブサマリー
    2. 需要予測結果
    3. 在庫最適化結果
    4. 推奨アクション
    5. 期待される効果

    出力形式: Markdown形式
    """

    expected_output = """
    以下のセクションを含むMarkdown形式のレポート:

    # サプライチェーン最適化レポート

    ## エグゼクティブサマリー
    （3-5文で全体像を説明）

    ## 需要予測
    - 予測需要量
    - 信頼区間
    - 予測根拠

    ## 在庫最適化
    - 推奨発注量
    - 選定サプライヤー
    - 期待利益

    ## 推奨アクション
    - [ ] アクション1
    - [ ] アクション2
    - [ ] アクション3

    ## 期待される効果
    - 廃棄ロス削減
    - 欠品削減
    - 利益改善
    """

    task = Task(
        description=description,
        agent=agent,
        expected_output=expected_output
    )

    return task
