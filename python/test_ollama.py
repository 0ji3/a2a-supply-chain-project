"""
Ollama接続テスト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def test_ollama_connection():
    """Ollama接続とモデル動作テスト"""

    print("=" * 60)
    print("Ollama接続テスト")
    print("=" * 60)

    # Ollama URLを環境変数から取得
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"\n1. Ollama URL: {ollama_url}")

    try:
        from langchain_ollama import OllamaLLM

        # Ollamaインスタンスを作成
        print("\n2. Ollamaインスタンスを作成...")
        llm = OllamaLLM(
            base_url=ollama_url,
            model="gemma2:2b",
            temperature=0.7
        )
        print("   ✓ インスタンス作成完了")

        # シンプルなテスト
        print("\n3. シンプルな質問テスト...")
        prompt = "こんにちは。あなたは誰ですか？日本語で簡潔に答えてください。"
        print(f"   質問: {prompt}")

        response = llm.invoke(prompt)
        print(f"\n   回答:\n   {response}\n")
        print("   ✓ テスト成功")

        # サプライチェーン関連のテスト
        print("\n4. サプライチェーン関連のテスト...")
        prompt = """
あなたは需要予測の専門家です。
以下のデータを分析して、明日のトマトの需要を予測してください：
- 先週の販売数: 300個
- 今週の販売数: 320個
- 明日の天気: 晴れ
- 明日: 週末

予測需要量と理由を簡潔に説明してください。
"""
        print(f"   質問: {prompt.strip()}")

        response = llm.invoke(prompt)
        print(f"\n   回答:\n   {response}\n")
        print("   ✓ テスト成功")

        print("\n" + "=" * 60)
        print("✓ 全てのテストが成功しました！")
        print("=" * 60)

    except ImportError as e:
        print(f"\n✗ エラー: 必要なパッケージがインストールされていません")
        print(f"   {e}")
        print("\n   以下のコマンドでインストールしてください:")
        print("   pip install langchain-ollama")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_ollama_connection()
