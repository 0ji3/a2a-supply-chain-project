#!/usr/bin/env python3
"""
エージェントウォレットに資金を配布するスクリプト
- Deployer → Agent wallets にJPYCを送信
- Polygon Amoy testnet
"""

import os
from dotenv import load_dotenv
from web3 import Web3
import time

# .envファイルを読み込み
load_dotenv()

# Web3接続
RPC_URL = os.getenv("POLYGON_AMOY_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Deployer設定
DEPLOYER_ADDRESS = os.getenv("DEPLOYER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# エージェントウォレット
AGENT_WALLETS = {
    "Demand Forecast": os.getenv("AGENT_DEMAND_FORECAST_ADDRESS"),
    "Inventory Optimizer": os.getenv("AGENT_INVENTORY_OPTIMIZER_ADDRESS"),
    "Report Generator": os.getenv("AGENT_REPORT_GENERATOR_ADDRESS"),
}

# JPYCコントラクト
JPYC_ADDRESS = os.getenv("MOCK_JPYC")
JPYC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

def check_connection():
    """接続確認"""
    if not w3.is_connected():
        print("❌ Web3接続エラー")
        return False
    print(f"✅ Polygon Amoy接続成功")
    print(f"   Chain ID: {w3.eth.chain_id}")
    return True

def check_deployer_balance():
    """Deployerの残高確認"""
    jpyc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(JPYC_ADDRESS),
        abi=JPYC_ABI
    )

    jpyc_balance = jpyc_contract.functions.balanceOf(
        Web3.to_checksum_address(DEPLOYER_ADDRESS)
    ).call()

    matic_balance = w3.eth.get_balance(Web3.to_checksum_address(DEPLOYER_ADDRESS))

    print(f"\n📊 Deployer残高:")
    print(f"   Address: {DEPLOYER_ADDRESS}")
    print(f"   JPYC: {jpyc_balance:,} JPYC")
    print(f"   MATIC: {w3.from_wei(matic_balance, 'ether'):.4f} MATIC")

    return jpyc_balance

def send_jpyc(to_address: str, amount: int, agent_name: str):
    """JPYCを送信"""
    jpyc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(JPYC_ADDRESS),
        abi=JPYC_ABI
    )

    # トランザクション構築
    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(DEPLOYER_ADDRESS))

    txn = jpyc_contract.functions.transfer(
        Web3.to_checksum_address(to_address),
        amount
    ).build_transaction({
        'from': Web3.to_checksum_address(DEPLOYER_ADDRESS),
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
    })

    # 署名
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

    # 送信
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f"   💸 {agent_name}: {amount:,} JPYC 送信中...")
    print(f"      TX: {tx_hash.hex()}")

    # トランザクション確認待ち
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if receipt['status'] == 1:
        print(f"      ✅ 成功")
        return True
    else:
        print(f"      ❌ 失敗")
        return False

def main():
    print("=" * 80)
    print("💰 エージェントウォレットへ資金配布")
    print("=" * 80)

    # 接続確認
    if not check_connection():
        return

    # Deployer残高確認
    deployer_jpyc = check_deployer_balance()

    if deployer_jpyc < 300000:  # 各エージェントに100,000 JPYC = 300,000 JPYC必要
        print("\n⚠️  警告: Deployer のJPYC残高が不足しています")
        print("   各エージェントに 100,000 JPYC を配布するには 300,000 JPYC 必要です")
        response = input("   続行しますか? (y/N): ")
        if response.lower() != 'y':
            print("中止しました")
            return

    print(f"\n🚀 配布開始...")
    print(f"   各エージェントに 100,000 JPYC を送信します\n")

    # 各エージェントに送信
    success_count = 0
    for agent_name, agent_address in AGENT_WALLETS.items():
        if send_jpyc(agent_address, 100000, agent_name):
            success_count += 1
        time.sleep(2)  # レート制限対策

    print("\n" + "=" * 80)
    print(f"✅ 完了: {success_count}/{len(AGENT_WALLETS)} エージェントに配布成功")
    print("=" * 80)

    # 配布後の残高確認
    print("\n📊 配布後の残高:")
    jpyc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(JPYC_ADDRESS),
        abi=JPYC_ABI
    )

    for agent_name, agent_address in AGENT_WALLETS.items():
        balance = jpyc_contract.functions.balanceOf(
            Web3.to_checksum_address(agent_address)
        ).call()
        print(f"   {agent_name}: {balance:,} JPYC")

    print("\n⚠️  注意: MATIC（ガス代）は別途 Polygon Faucet から取得してください")
    print("   https://faucet.polygon.technology/")

if __name__ == "__main__":
    main()
