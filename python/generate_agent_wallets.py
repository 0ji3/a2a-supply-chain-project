#!/usr/bin/env python3
"""
エージェント用ウォレット生成スクリプト
3つのエージェント用に新しいウォレットアドレスと秘密鍵を生成します
"""

from eth_account import Account
import secrets

def generate_wallet(agent_name: str) -> dict:
    """ウォレットを生成"""
    # ランダムな秘密鍵を生成
    private_key = "0x" + secrets.token_hex(32)

    # アカウントを作成
    account = Account.from_key(private_key)

    return {
        "name": agent_name,
        "address": account.address,
        "private_key": private_key
    }

def main():
    agents = [
        "Demand Forecast Agent",
        "Inventory Optimizer Agent",
        "Report Generator Agent"
    ]

    print("=" * 80)
    print("🔑 エージェント用ウォレット生成")
    print("=" * 80)
    print()

    wallets = []
    for agent_name in agents:
        wallet = generate_wallet(agent_name)
        wallets.append(wallet)

        print(f"### {wallet['name']}")
        print(f"Address:     {wallet['address']}")
        print(f"Private Key: {wallet['private_key']}")
        print()

    print("=" * 80)
    print("📝 .env に追加する設定")
    print("=" * 80)
    print()
    print("# Agent Wallets")
    print(f"AGENT_DEMAND_FORECAST_ADDRESS={wallets[0]['address']}")
    print(f"AGENT_DEMAND_FORECAST_PRIVATE_KEY={wallets[0]['private_key']}")
    print()
    print(f"AGENT_INVENTORY_OPTIMIZER_ADDRESS={wallets[1]['address']}")
    print(f"AGENT_INVENTORY_OPTIMIZER_PRIVATE_KEY={wallets[1]['private_key']}")
    print()
    print(f"AGENT_REPORT_GENERATOR_ADDRESS={wallets[2]['address']}")
    print(f"AGENT_REPORT_GENERATOR_PRIVATE_KEY={wallets[2]['private_key']}")
    print()

    print("=" * 80)
    print("⚠️  重要: これらの秘密鍵は安全に保管してください")
    print("=" * 80)

if __name__ == "__main__":
    main()
