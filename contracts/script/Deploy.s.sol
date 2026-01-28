// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/ERC8004Identity.sol";
import "../src/ERC8004Reputation.sol";
import "../src/MockJPYC.sol";

/**
 * @title Deploy
 * @notice Anvilローカルチェーンへのデプロイスクリプト
 */
contract Deploy is Script {
    function run() external {
        // Anvilのデフォルトアカウント（account 0）の秘密鍵
        uint256 deployerPrivateKey = vm.envOr(
            "PRIVATE_KEY",
            uint256(0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80)
        );

        vm.startBroadcast(deployerPrivateKey);

        // 1. ERC-8004 Identity Registry デプロイ
        ERC8004Identity identity = new ERC8004Identity();
        console.log("ERC8004Identity deployed at:", address(identity));

        // 2. ERC-8004 Reputation Registry デプロイ
        ERC8004Reputation reputation = new ERC8004Reputation();
        console.log("ERC8004Reputation deployed at:", address(reputation));

        // 3. MockJPYC デプロイ
        MockJPYC jpyc = new MockJPYC();
        console.log("MockJPYC deployed at:", address(jpyc));

        // 4. テスト用アカウントにJPYCをエアドロップ
        address[] memory testAccounts = new address[](5);
        testAccounts[0] = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266; // account 0
        testAccounts[1] = 0x70997970C51812dc3A010C7d01b50e0d17dc79C8; // account 1
        testAccounts[2] = 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC; // account 2
        testAccounts[3] = 0x90F79bf6EB2c4f870365E785982E1f101E93b906; // account 3
        testAccounts[4] = 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65; // account 4

        uint256 airdropAmount = 10_000 * 10**18; // 10,000 JPYC per account
        jpyc.airdrop(testAccounts, airdropAmount);
        console.log("Airdropped 10,000 JPYC to 5 test accounts");

        // 5. デモ用エージェント登録
        uint256 agent1Id = identity.registerAgent(
            "Demand Forecast Agent",
            "demand_forecast",
            "ipfs://QmDemo1"
        );
        console.log("Registered Agent 1 (Demand Forecast):", agent1Id);

        uint256 agent2Id = identity.registerAgent(
            "Inventory Optimizer Agent",
            "inventory_optimizer",
            "ipfs://QmDemo2"
        );
        console.log("Registered Agent 2 (Inventory Optimizer):", agent2Id);

        vm.stopBroadcast();

        // デプロイ情報をファイルに保存（Python連携用）
        string memory deployments = string(
            abi.encodePacked(
                "ERC8004Identity=",
                vm.toString(address(identity)),
                "\n",
                "ERC8004Reputation=",
                vm.toString(address(reputation)),
                "\n",
                "MockJPYC=",
                vm.toString(address(jpyc)),
                "\n",
                "Agent1Id=",
                vm.toString(agent1Id),
                "\n",
                "Agent2Id=",
                vm.toString(agent2Id)
            )
        );

        vm.writeFile("../deployments.txt", deployments);
        console.log("\nDeployment info saved to deployments.txt");
    }
}
