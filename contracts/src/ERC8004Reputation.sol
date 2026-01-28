// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ERC8004Reputation
 * @notice エージェントの評価・評判を記録するコントラクト（ERC-8004 Reputation Registry）
 * @dev エージェントの実行結果に対するフィードバックを記録し、平均スコアを計算
 */
contract ERC8004Reputation {
    /// @notice フィードバック構造体
    struct Feedback {
        address client;           // フィードバック提供者
        uint8 score;             // スコア（0-100）
        string[] tags;           // タグ（例: "accurate", "fast", "reliable"）
        string reportURI;        // レポートURI（詳細なフィードバック）
        uint256 timestamp;       // タイムスタンプ
    }

    /// @notice 評判統計構造体
    struct ReputationStats {
        uint256 totalFeedbacks;  // 総フィードバック数
        uint256 totalScore;      // 総スコア
        uint8 averageScore;      // 平均スコア
    }

    /// @notice エージェントID → フィードバック配列
    mapping(uint256 => Feedback[]) public feedbacks;

    /// @notice エージェントID → 評判統計
    mapping(uint256 => ReputationStats) private stats;

    /// @notice エージェントID → タグ → カウント
    mapping(uint256 => mapping(string => uint256)) private tagCounts;

    /// @notice イベント: フィードバック送信
    event FeedbackSubmitted(
        uint256 indexed agentId,
        address indexed client,
        uint8 score,
        string reportURI,
        uint256 timestamp
    );

    /// @notice イベント: 平均スコア更新
    event AverageScoreUpdated(
        uint256 indexed agentId,
        uint8 newAverageScore
    );

    /**
     * @notice フィードバックを送信
     * @param agentId エージェントID
     * @param score スコア（0-100）
     * @param tags タグ配列
     * @param reportURI レポートURI
     */
    function submitFeedback(
        uint256 agentId,
        uint8 score,
        string[] memory tags,
        string memory reportURI
    ) external {
        require(score <= 100, "Score must be <= 100");

        // フィードバックを記録
        feedbacks[agentId].push(
            Feedback({
                client: msg.sender,
                score: score,
                tags: tags,
                reportURI: reportURI,
                timestamp: block.timestamp
            })
        );

        // 統計を更新
        ReputationStats storage agentStats = stats[agentId];
        agentStats.totalFeedbacks++;
        agentStats.totalScore += score;
        agentStats.averageScore = uint8(
            agentStats.totalScore / agentStats.totalFeedbacks
        );

        // タグカウントを更新
        for (uint256 i = 0; i < tags.length; i++) {
            tagCounts[agentId][tags[i]]++;
        }

        emit FeedbackSubmitted(
            agentId,
            msg.sender,
            score,
            reportURI,
            block.timestamp
        );
        emit AverageScoreUpdated(agentId, agentStats.averageScore);
    }

    /**
     * @notice 平均スコアを取得
     * @param agentId エージェントID
     * @return 平均スコア（0-100）
     */
    function getAverageScore(uint256 agentId)
        external
        view
        returns (uint8)
    {
        return stats[agentId].averageScore;
    }

    /**
     * @notice フィードバック数を取得
     * @param agentId エージェントID
     * @return フィードバック数
     */
    function getFeedbackCount(uint256 agentId)
        external
        view
        returns (uint256)
    {
        return stats[agentId].totalFeedbacks;
    }

    /**
     * @notice 評判統計を取得
     * @param agentId エージェントID
     * @return totalFeedbacks フィードバック総数
     * @return averageScore 平均スコア
     */
    function getReputationStats(uint256 agentId)
        external
        view
        returns (uint256 totalFeedbacks, uint8 averageScore)
    {
        ReputationStats storage agentStats = stats[agentId];
        return (agentStats.totalFeedbacks, agentStats.averageScore);
    }

    /**
     * @notice タグの出現回数を取得
     * @param agentId エージェントID
     * @param tag タグ
     * @return 出現回数
     */
    function getTagCount(uint256 agentId, string memory tag)
        external
        view
        returns (uint256)
    {
        return tagCounts[agentId][tag];
    }

    /**
     * @notice 特定のフィードバックを取得
     * @param agentId エージェントID
     * @param index フィードバックのインデックス
     * @return フィードバック
     */
    function getFeedback(uint256 agentId, uint256 index)
        external
        view
        returns (Feedback memory)
    {
        require(index < feedbacks[agentId].length, "Index out of bounds");
        return feedbacks[agentId][index];
    }

    /**
     * @notice 最新のフィードバックを取得
     * @param agentId エージェントID
     * @param count 取得件数
     * @return 最新のフィードバック配列
     */
    function getLatestFeedbacks(uint256 agentId, uint256 count)
        external
        view
        returns (Feedback[] memory)
    {
        uint256 totalCount = feedbacks[agentId].length;
        uint256 returnCount = count > totalCount ? totalCount : count;

        Feedback[] memory latestFeedbacks = new Feedback[](returnCount);

        for (uint256 i = 0; i < returnCount; i++) {
            latestFeedbacks[i] = feedbacks[agentId][
                totalCount - returnCount + i
            ];
        }

        return latestFeedbacks;
    }
}
