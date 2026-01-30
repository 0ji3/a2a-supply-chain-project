"""
CrewAI + Ollama統合テスト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_crewai_basic():
    """CrewAI基本動作テスト"""

    print("=" * 60)
    print("CrewAI + Ollama統合テスト")
    print("=" * 60)

    try:
        from crewai import Agent, Task, Crew, LLM
        from langchain_ollama import ChatOllama

        # Ollama LLMを初期化
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # LiteLLM用の環境変数を設定
        os.environ["OLLAMA_API_BASE"] = ollama_url

        print(f"\n1. Ollama LLMを初期化...")
        print(f"   URL: {ollama_url}")

        # CrewAI LLMインスタンスを作成
        llm = LLM(
            model="ollama/gemma2:2b",
            base_url=ollama_url
        )
        print("   ✓ LLM初期化完了")

        # エージェント1: 需要予測アナリスト
        print("\n2. エージェントを作成...")
        demand_analyst = Agent(
            role="需要予測アナリスト",
            goal="過去のデータから正確な需要を予測する",
            backstory="""あなたは10年の経験を持つ需要予測の専門家です。
            季節性、天候、イベントなどの要因を考慮して、高精度な予測を行います。""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        print("   ✓ 需要予測アナリスト作成完了")

        # エージェント2: 在庫マネージャー
        inventory_manager = Agent(
            role="在庫マネージャー",
            goal="最適な発注量を決定し、廃棄ロスと欠品を最小化する",
            backstory="""あなたは効率的な在庫管理のプロフェッショナルです。
            需要予測を基に、コストを最小化する発注戦略を立案します。""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        print("   ✓ 在庫マネージャー作成完了")

        # タスク1: 需要予測
        print("\n3. タスクを定義...")
        forecast_task = Task(
            description="""
            以下のトマトの販売データを分析し、明日の需要を予測してください：
            - 先週の販売数: 300個
            - 今週の販売数: 320個
            - 明日の天気: 晴れ
            - 明日: 週末

            予測需要量と信頼区間を提示してください。
            """,
            agent=demand_analyst,
            expected_output="予測需要量（個数）と信頼区間、予測の根拠"
        )
        print("   ✓ 需要予測タスク作成完了")

        # タスク2: 在庫最適化
        optimize_task = Task(
            description="""
            需要予測結果を基に、最適な発注量を決定してください。
            以下の情報を考慮してください：
            - 仕入れ単価: 120円
            - 販売単価: 200円
            - 廃棄コスト: 120円
            - 欠品機会損失: 80円

            推奨発注量と期待利益を提示してください。
            """,
            agent=inventory_manager,
            expected_output="推奨発注量（個数）、期待利益、意思決定の理由"
        )
        print("   ✓ 在庫最適化タスク作成完了")

        # Crewを作成
        print("\n4. Crewを編成...")
        supply_chain_crew = Crew(
            agents=[demand_analyst, inventory_manager],
            tasks=[forecast_task, optimize_task],
            verbose=True
        )
        print("   ✓ Crew編成完了")

        # Crewを実行
        print("\n5. Crewを実行...")
        print("-" * 60)
        result = supply_chain_crew.kickoff()
        print("-" * 60)

        # 結果を表示
        print("\n6. 実行結果:")
        print(f"\n{result}")

        print("\n" + "=" * 60)
        print("✓ CrewAI + Ollama統合テスト成功！")
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
    test_crewai_basic()
