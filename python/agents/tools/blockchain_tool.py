"""
ブロックチェーンツール

ERC-8004コントラクトとやり取りするツール
"""
from typing import Dict
from crewai.tools import tool
import os


@tool("Get Agent Reputation")
def get_agent_reputation(agent_id: int) -> str:
    """
    エージェントの評判情報をブロックチェーンから取得する

    Args:
        agent_id: エージェントID

    Returns:
        評判情報の文字列表現
    """
    # Phase 3ではモックデータを返す
    # Phase 4以降で実際のブロックチェーン接続を実装

    mock_reputations = {
        1: {  # Demand Forecast Agent
            "agent_id": 1,
            "name": "Demand Forecast Agent",
            "total_feedbacks": 156,
            "average_score": 87,
            "total_tasks": 180,
            "success_rate": 92
        },
        2: {  # Inventory Optimizer Agent
            "agent_id": 2,
            "name": "Inventory Optimizer Agent",
            "total_feedbacks": 142,
            "average_score": 89,
            "total_tasks": 165,
            "success_rate": 94
        }
    }

    if agent_id not in mock_reputations:
        return f"エージェントID {agent_id} の評判情報が見つかりません"

    rep = mock_reputations[agent_id]

    result = f"エージェント評判情報\n\n"
    result += f"エージェントID: {rep['agent_id']}\n"
    result += f"名前: {rep['name']}\n"
    result += f"総フィードバック数: {rep['total_feedbacks']}\n"
    result += f"平均スコア: {rep['average_score']}点/100点\n"
    result += f"総タスク数: {rep['total_tasks']}\n"
    result += f"成功率: {rep['success_rate']}%\n"

    return result


@tool("Submit Agent Feedback")
def submit_agent_feedback(
    agent_id: int,
    score: int,
    tags: str,
    report_uri: str = ""
) -> str:
    """
    エージェントへのフィードバックをブロックチェーンに記録する

    Args:
        agent_id: エージェントID
        score: スコア (0-100)
        tags: タグ（カンマ区切り）
        report_uri: レポートURI（オプション）

    Returns:
        送信結果の文字列表現
    """
    # Phase 3ではモック応答を返す
    # Phase 4以降で実際のブロックチェーントランザクションを実装

    if score < 0 or score > 100:
        return "エラー: スコアは0-100の範囲でなければなりません"

    tags_list = [tag.strip() for tag in tags.split(",")]

    result = f"フィードバック送信成功\n\n"
    result += f"エージェントID: {agent_id}\n"
    result += f"スコア: {score}点\n"
    result += f"タグ: {', '.join(tags_list)}\n"
    if report_uri:
        result += f"レポートURI: {report_uri}\n"
    result += f"\nトランザクションハッシュ: 0xmock...{agent_id}\n"
    result += "（Phase 3ではモックトランザクション）"

    return result
