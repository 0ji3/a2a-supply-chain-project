// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC8004Identity
 * @notice エージェント登録用NFTコントラクト（ERC-8004 Identity Registry）
 * @dev 各AIエージェントに一意のIDを付与し、メタデータを管理
 */
contract ERC8004Identity is ERC721, Ownable {
    /// @notice エージェントメタデータ構造体
    struct AgentMetadata {
        string name;              // エージェント名
        string category;          // カテゴリ（demand_forecast, inventory_optimizer等）
        string vendor;            // ベンダー名
        string modelType;         // モデルタイプ（GPT-4, Claude等）
        string metadataURI;       // IPFS URI（詳細メタデータ）
        uint256 registeredAt;     // 登録日時
        address walletAddress;    // エージェントのウォレットアドレス
    }

    /// @notice エージェントID → メタデータのマッピング
    mapping(uint256 => AgentMetadata) public agents;

    /// @notice 次のエージェントID
    uint256 private _nextAgentId;

    /// @notice イベント: エージェント登録
    event AgentRegistered(
        uint256 indexed agentId,
        string name,
        string category,
        address indexed walletAddress
    );

    /// @notice イベント: メタデータ更新
    event MetadataUpdated(
        uint256 indexed agentId,
        string key,
        string value
    );

    /// @notice イベント: ウォレットアドレス更新
    event WalletAddressUpdated(
        uint256 indexed agentId,
        address indexed oldAddress,
        address indexed newAddress
    );

    constructor() ERC721("A2A Agent Identity", "A2A-AGENT") Ownable(msg.sender) {
        _nextAgentId = 1; // ID 0は予約
    }

    /**
     * @notice エージェントを登録してNFTをミント
     * @param _name エージェント名
     * @param _category カテゴリ
     * @param _metadataURI メタデータURI（IPFS等）
     * @return agentId 登録されたエージェントID
     */
    function registerAgent(
        string memory _name,
        string memory _category,
        string memory _metadataURI
    ) external returns (uint256) {
        uint256 agentId = _nextAgentId++;

        // NFTをミント
        _safeMint(msg.sender, agentId);

        // メタデータを保存
        agents[agentId] = AgentMetadata({
            name: _name,
            category: _category,
            vendor: "",
            modelType: "",
            metadataURI: _metadataURI,
            registeredAt: block.timestamp,
            walletAddress: msg.sender
        });

        emit AgentRegistered(agentId, _name, _category, msg.sender);

        return agentId;
    }

    /**
     * @notice エージェントのウォレットアドレスを更新
     * @param agentId エージェントID
     * @param newWalletAddress 新しいウォレットアドレス
     */
    function updateWalletAddress(
        uint256 agentId,
        address newWalletAddress
    ) external {
        require(ownerOf(agentId) == msg.sender, "Not the agent owner");
        require(newWalletAddress != address(0), "Invalid address");

        address oldAddress = agents[agentId].walletAddress;
        agents[agentId].walletAddress = newWalletAddress;

        emit WalletAddressUpdated(agentId, oldAddress, newWalletAddress);
    }

    /**
     * @notice エージェントのベンダー情報を更新
     * @param agentId エージェントID
     * @param _vendor ベンダー名
     * @param _modelType モデルタイプ
     */
    function updateVendorInfo(
        uint256 agentId,
        string memory _vendor,
        string memory _modelType
    ) external {
        require(ownerOf(agentId) == msg.sender, "Not the agent owner");

        agents[agentId].vendor = _vendor;
        agents[agentId].modelType = _modelType;

        emit MetadataUpdated(agentId, "vendor", _vendor);
        emit MetadataUpdated(agentId, "modelType", _modelType);
    }

    /**
     * @notice エージェントメタデータを取得
     * @param agentId エージェントID
     * @return メタデータ
     */
    function getAgentMetadata(uint256 agentId)
        external
        view
        returns (AgentMetadata memory)
    {
        require(_exists(agentId), "Agent does not exist");
        return agents[agentId];
    }

    /**
     * @notice 次のエージェントIDを取得
     * @return 次のエージェントID
     */
    function getNextAgentId() external view returns (uint256) {
        return _nextAgentId;
    }

    /**
     * @notice トークンが存在するかチェック
     * @param tokenId トークンID
     * @return 存在する場合はtrue
     */
    function _exists(uint256 tokenId) internal view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }
}
