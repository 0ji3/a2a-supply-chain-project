// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MockJPYC
 * @notice JPYCテストトークン（ERC-20 + EIP-3009対応）
 * @dev ガスレス決済（transferWithAuthorization）に対応したJPYCモックトークン
 */
contract MockJPYC is ERC20, Ownable {
    /// @notice EIP-712ドメイン区切り文字のハッシュ
    bytes32 public DOMAIN_SEPARATOR;

    /// @notice transferWithAuthorizationの型ハッシュ
    bytes32 public constant TRANSFER_WITH_AUTHORIZATION_TYPEHASH =
        keccak256(
            "TransferWithAuthorization(address from,address to,uint256 value,uint256 validAfter,uint256 validBefore,bytes32 nonce)"
        );

    /// @notice ノンスの使用状況を記録
    mapping(address => mapping(bytes32 => bool)) public authorizationState;

    /// @notice イベント: ガスレス転送実行
    event AuthorizationUsed(address indexed authorizer, bytes32 indexed nonce);

    constructor() ERC20("Mock JPY Coin", "JPYC") Ownable(msg.sender) {
        // EIP-712ドメイン区切り文字を計算
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256(
                    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
                ),
                keccak256(bytes("Mock JPY Coin")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );

        // 初期供給: 1億JPYC（18 decimals）
        _mint(msg.sender, 100_000_000 * 10**decimals());
    }

    /**
     * @notice テスト用にトークンをミント（ownerのみ）
     * @param to ミント先アドレス
     * @param amount ミント量
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    /**
     * @notice EIP-3009: ガスレス転送（transferWithAuthorization）
     * @param from 送信者アドレス
     * @param to 受信者アドレス
     * @param value 転送量
     * @param validAfter 有効開始時刻（Unix timestamp）
     * @param validBefore 有効終了時刻（Unix timestamp）
     * @param nonce ノンス（リプレイ攻撃防止）
     * @param v 署名のv
     * @param r 署名のr
     * @param s 署名のs
     */
    function transferWithAuthorization(
        address from,
        address to,
        uint256 value,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        require(block.timestamp > validAfter, "Authorization not yet valid");
        require(block.timestamp < validBefore, "Authorization expired");
        require(!authorizationState[from][nonce], "Authorization already used");

        // EIP-712署名を検証
        bytes32 structHash = keccak256(
            abi.encode(
                TRANSFER_WITH_AUTHORIZATION_TYPEHASH,
                from,
                to,
                value,
                validAfter,
                validBefore,
                nonce
            )
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        address signer = ecrecover(digest, v, r, s);
        require(signer == from, "Invalid signature");

        // ノンスを使用済みにマーク
        authorizationState[from][nonce] = true;

        // トークン転送
        _transfer(from, to, value);

        emit AuthorizationUsed(from, nonce);
    }

    /**
     * @notice テスト用に複数アドレスにエアドロップ
     * @param recipients 受信者アドレス配列
     * @param amount 各受信者への配布量
     */
    function airdrop(address[] memory recipients, uint256 amount)
        external
        onlyOwner
    {
        for (uint256 i = 0; i < recipients.length; i++) {
            _mint(recipients[i], amount);
        }
    }
}
