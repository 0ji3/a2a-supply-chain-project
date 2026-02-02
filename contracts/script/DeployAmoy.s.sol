// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/ERC8004Identity.sol";
import "../src/ERC8004Reputation.sol";
import "../src/MockJPYC.sol";

/**
 * @title DeployAmoy
 * @notice Polygon Amoyテストネットへのデプロイスクリプト
 */
contract DeployAmoy is Script {
    function run() external {
        // 環境変数から秘密鍵を取得
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console.log("Deploying to Polygon Amoy...");
        console.log("Deployer address:", deployer);
        console.log("Deployer balance:", deployer.balance);

        vm.startBroadcast(deployerPrivateKey);

        // 1. ERC-8004 Identity Registry デプロイ
        ERC8004Identity identity = new ERC8004Identity();
        console.log("ERC8004Identity deployed at:", address(identity));

        // 2. ERC-8004 Reputation Registry デプロイ
        ERC8004Reputation reputation = new ERC8004Reputation();
        console.log("ERC8004Reputation deployed at:", address(reputation));

        // 3. MockJPYC デプロイ（テスト用）
        MockJPYC jpyc = new MockJPYC();
        console.log("MockJPYC deployed at:", address(jpyc));

        // 4. デプロイヤーにJPYCをmint
        address[] memory testAccounts = new address[](1);
        testAccounts[0] = deployer;

        uint256 initialSupply = 100_000 * 10**18; // 100,000 JPYC
        jpyc.airdrop(testAccounts, initialSupply);
        console.log("Minted 100,000 JPYC to deployer");

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

        uint256 agent3Id = identity.registerAgent(
            "Report Generator Agent",
            "report_generator",
            "ipfs://QmDemo3"
        );
        console.log("Registered Agent 3 (Report Generator):", agent3Id);

        vm.stopBroadcast();

        // デプロイ情報をファイルに保存（Python連携用）
        string memory deployments = string(
            abi.encodePacked(
                "# Polygon Amoy Testnet Deployment\n",
                "NETWORK=polygon-amoy\n",
                "CHAIN_ID=80002\n",
                "ERC8004_IDENTITY=",
                vm.toString(address(identity)),
                "\n",
                "ERC8004_REPUTATION=",
                vm.toString(address(reputation)),
                "\n",
                "MOCK_JPYC=",
                vm.toString(address(jpyc)),
                "\n",
                "AGENT_DEMAND_FORECAST_ID=",
                vm.toString(agent1Id),
                "\n",
                "AGENT_INVENTORY_OPTIMIZER_ID=",
                vm.toString(agent2Id),
                "\n",
                "AGENT_REPORT_GENERATOR_ID=",
                vm.toString(agent3Id),
                "\n"
            )
        );

        vm.writeFile("../deployments-amoy.txt", deployments);
        console.log("\nDeployment info saved to deployments-amoy.txt");
        console.log("\n=== Deployment Complete ===");
        console.log("Next steps:");
        console.log("1. Update Python config with contract addresses");
        console.log("2. Test X402 payment flow with real blockchain");
    }
}
