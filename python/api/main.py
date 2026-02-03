"""
FastAPI バックエンド - Phase 5
リアルタイムログストリーミング + エージェント協調制御
"""
import os
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, List
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from web3 import Web3
import sys

# .envファイルを読み込み
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# プロジェクトルートをPythonパスに追加（protocols importのため）
sys.path.insert(0, str(Path(__file__).parent.parent))

# ブロックチェーン関連のインポート
try:
    from protocols.blockchain_service import get_blockchain_service
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Blockchain service not available: {e}")
    BLOCKCHAIN_AVAILABLE = False

# Web3接続（Polygon Amoy）
RPC_URL = os.getenv("POLYGON_AMOY_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# JPYCコントラクト
JPYC_ADDRESS = os.getenv("MOCK_JPYC")
JPYC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

app = FastAPI(
    title="A2A Supply Chain API",
    description="Agent-to-Agent決済システム デモAPI",
    version="1.0.0"
)

# CORS設定（Next.js フロントエンド用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル状態（簡易実装、本番ではRedis等を使用）
current_logs: List[Dict] = []
current_status: Dict = {
    "demand_forecast": {"status": "idle", "progress": 0},
    "inventory_optimizer": {"status": "idle", "progress": 0},
    "report_generator": {"status": "idle", "progress": 0},
}
transactions: List[Dict] = []


# ==========================================
# リクエスト/レスポンスモデル
# ==========================================

class OptimizationRequest(BaseModel):
    product_sku: str
    store_id: str
    weather: str = "晴れ"
    day_type: str = "週末"
    unit_price: float = 200.0


class LogEntry(BaseModel):
    timestamp: str
    level: str  # info, success, warning, error, payment, transaction
    agent: str | None = None
    message: str
    details: Dict | None = None


# ==========================================
# ログ管理
# ==========================================

def add_log(level: str, message: str, agent: str = None, details: Dict = None):
    """ログを追加"""
    log_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "level": level,
        "agent": agent,
        "message": message,
        "details": details or {}
    }
    current_logs.append(log_entry)
    print(f"[{log_entry['timestamp']}] {level.upper()}: {message}")  # サーバーログ


def update_agent_status(agent: str, status: str, progress: int = 0):
    """エージェントステータスを更新"""
    if agent in current_status:
        current_status[agent]["status"] = status
        current_status[agent]["progress"] = progress


def add_transaction(agent: str, amount: float, address: str, tx_hash: str):
    """トランザクション履歴を追加"""
    transactions.append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "amount": amount,
        "address": address,
        "tx_hash": tx_hash,
        "status": "completed"
    })


def get_jpyc_balance(address: str) -> int:
    """JPYCの残高を取得（Wei単位）"""
    try:
        jpyc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(JPYC_ADDRESS),
            abi=JPYC_ABI
        )
        balance = jpyc_contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()
        return balance
    except Exception as e:
        print(f"Error getting balance for {address}: {e}")
        return 0


# ==========================================
# エンドポイント
# ==========================================

@app.get("/")
def root():
    """ヘルスチェック"""
    return {
        "status": "ok",
        "message": "A2A Supply Chain API v1.0.0"
    }


@app.get("/api/status")
def get_status():
    """現在のエージェントステータスを取得"""
    return {
        "agents": current_status,
        "total_transactions": len(transactions)
    }


@app.get("/api/transactions")
def get_transactions():
    """トランザクション履歴を取得"""
    return {
        "transactions": transactions
    }


@app.get("/api/logs")
def get_logs(limit: int = 100):
    """ログを取得"""
    return {
        "logs": current_logs[-limit:]
    }


@app.get("/api/agents")
def get_agents():
    """エージェント情報とウォレット残高を取得"""
    agent_wallets = {
        "demand_forecast": os.getenv("AGENT_DEMAND_FORECAST_ADDRESS"),
        "inventory_optimizer": os.getenv("AGENT_INVENTORY_OPTIMIZER_ADDRESS"),
        "report_generator": os.getenv("AGENT_REPORT_GENERATOR_ADDRESS"),
    }

    agents_info = []
    for agent_key, address in agent_wallets.items():
        if address:
            balance = get_jpyc_balance(address)
            agents_info.append({
                "id": agent_key,
                "name": {
                    "demand_forecast": "需要予測エージェント",
                    "inventory_optimizer": "在庫最適化エージェント",
                    "report_generator": "レポート生成エージェント"
                }[agent_key],
                "address": address,
                "jpyc_balance": balance,
                "status": current_status.get(agent_key, {}).get("status", "idle"),
                "progress": current_status.get(agent_key, {}).get("progress", 0)
            })

    return {
        "agents": agents_info
    }


@app.post("/api/optimize")
async def optimize(request: OptimizationRequest):
    """
    最適化タスクを実行
    非同期でエージェントを実行し、タスクIDを返す
    """
    # ログとステータスをリセット
    current_logs.clear()
    for agent in current_status:
        update_agent_status(agent, "idle", 0)
    transactions.clear()

    add_log("info", f"🚀 最適化タスク開始")
    add_log("info", f"   商品: {request.product_sku}")
    add_log("info", f"   店舗: {request.store_id}")
    add_log("info", f"   天気: {request.weather}, タイプ: {request.day_type}")

    # バックグラウンドでタスクを実行
    asyncio.create_task(run_optimization_task(request))

    return {
        "status": "started",
        "message": "最適化タスクを開始しました。/api/logs/stream でリアルタイムログを確認できます。"
    }


@app.get("/api/logs/stream")
async def stream_logs():
    """
    Server-Sent Events (SSE) でリアルタイムログをストリーミング
    """
    async def log_generator() -> AsyncGenerator[str, None]:
        """ログを生成"""
        last_log_count = 0

        while True:
            # 新しいログがあるか確認
            if len(current_logs) > last_log_count:
                new_logs = current_logs[last_log_count:]
                for log in new_logs:
                    # SSE形式で送信
                    yield f"data: {json.dumps(log)}\n\n"
                last_log_count = len(current_logs)

            # ステータス更新も送信
            yield f"data: {json.dumps({'type': 'status', 'data': current_status})}\n\n"

            await asyncio.sleep(0.5)  # 0.5秒ごとにポーリング

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ==========================================
# エージェント協調制御（モック実装）
# ==========================================

async def run_optimization_task(request: OptimizationRequest):
    """
    最適化タスクを実行
    実際のブロックチェーン決済を実行（LLM推論はモック）
    """
    try:
        # エージェントウォレット
        agent_wallets = {
            "demand_forecast": os.getenv("AGENT_DEMAND_FORECAST_ADDRESS"),
            "inventory_optimizer": os.getenv("AGENT_INVENTORY_OPTIMIZER_ADDRESS"),
            "report_generator": os.getenv("AGENT_REPORT_GENERATOR_ADDRESS"),
        }

        # BlockchainService初期化
        if not BLOCKCHAIN_AVAILABLE:
            add_log("error", "❌ Blockchain service not available")
            return

        blockchain_service = get_blockchain_service()
        add_log("info", f"✅ Blockchain接続成功 (Chain ID: {blockchain_service.w3.eth.chain_id})")

        # 残高確認
        balance = blockchain_service.get_balance()
        add_log("info", f"   Deployer残高: {balance['jpyc_balance']:,} JPYC")

        # ==========================================
        # Phase 1: 需要予測エージェント
        # ==========================================
        add_log("info", "📊 Phase 1: 需要予測エージェント", agent="demand_forecast")
        update_agent_status("demand_forecast", "running", 10)

        await asyncio.sleep(1)

        add_log("info", "   LLMモデル準備中...", agent="demand_forecast")
        update_agent_status("demand_forecast", "running", 30)

        # 実際のLLMエージェント実行（モック）
        await asyncio.sleep(2)
        add_log("success", "   ✅ LLM推論完了", agent="demand_forecast")
        update_agent_status("demand_forecast", "running", 60)

        # 決済処理（実ブロックチェーン）
        add_log("payment", f"💰 決済処理開始: 3 JPYC", agent="demand_forecast")
        add_log("info", f"   送信先: {agent_wallets['demand_forecast']}", agent="demand_forecast")

        # 実際のJPYC送金
        try:
            tx_hash = blockchain_service.transfer_jpyc(
                to_address=agent_wallets['demand_forecast'],
                amount=3  # 3 JPYC (Wei単位で送信される)
            )
            add_log("info", f"   トランザクション送信中...", agent="demand_forecast")
            add_log("info", f"   TX: {tx_hash}", agent="demand_forecast")

            # トランザクション確認待ち（非同期）
            await asyncio.sleep(3)  # Polygon Amoyは約2-3秒

            add_log("transaction", f"✅ トランザクション成功", agent="demand_forecast", details={
                "tx_hash": tx_hash,
                "amount": 3,
                "address": agent_wallets['demand_forecast'],
                "explorer": f"https://amoy.polygonscan.com/tx/{tx_hash}"
            })

            add_transaction(
                agent="需要予測エージェント",
                amount=3,
                address=agent_wallets['demand_forecast'],
                tx_hash=tx_hash
            )
        except Exception as e:
            add_log("error", f"❌ 決済エラー: {str(e)}", agent="demand_forecast")
            update_agent_status("demand_forecast", "error", 0)
            return

        update_agent_status("demand_forecast", "running", 80)

        # 結果
        forecast_result = {
            "predicted_demand": 250,
            "confidence_interval": [220, 280],
            "model": "moving_average_7d"
        }

        add_log("success", f"📈 需要予測結果: {forecast_result['predicted_demand']} 個",
                agent="demand_forecast", details=forecast_result)
        update_agent_status("demand_forecast", "completed", 100)

        await asyncio.sleep(1)

        # ==========================================
        # Phase 2: 在庫最適化エージェント
        # ==========================================
        add_log("info", "📦 Phase 2: 在庫最適化エージェント", agent="inventory_optimizer")
        update_agent_status("inventory_optimizer", "running", 10)

        await asyncio.sleep(1)

        add_log("info", "   需要予測データを受信", agent="inventory_optimizer")
        add_log("info", f"   予測需要: {forecast_result['predicted_demand']} 個",
                agent="inventory_optimizer")
        update_agent_status("inventory_optimizer", "running", 30)

        # LLM推論
        await asyncio.sleep(2)
        add_log("success", "   ✅ 最適化計算完了", agent="inventory_optimizer")
        update_agent_status("inventory_optimizer", "running", 60)

        # 決済処理（実ブロックチェーン）
        add_log("payment", f"💰 決済処理開始: 15 JPYC", agent="inventory_optimizer")
        add_log("info", f"   送信先: {agent_wallets['inventory_optimizer']}",
                agent="inventory_optimizer")

        # 実際のJPYC送金
        try:
            tx_hash2 = blockchain_service.transfer_jpyc(
                to_address=agent_wallets['inventory_optimizer'],
                amount=15  # 15 JPYC
            )
            add_log("info", f"   トランザクション送信中...", agent="inventory_optimizer")
            add_log("info", f"   TX: {tx_hash2}", agent="inventory_optimizer")

            await asyncio.sleep(3)

            add_log("transaction", f"✅ トランザクション成功", agent="inventory_optimizer", details={
                "tx_hash": tx_hash2,
                "amount": 15,
                "address": agent_wallets['inventory_optimizer'],
                "explorer": f"https://amoy.polygonscan.com/tx/{tx_hash2}"
            })

            add_transaction(
                agent="在庫最適化エージェント",
                amount=15,
                address=agent_wallets['inventory_optimizer'],
                tx_hash=tx_hash2
            )
        except Exception as e:
            add_log("error", f"❌ 決済エラー: {str(e)}", agent="inventory_optimizer")
            update_agent_status("inventory_optimizer", "error", 0)
            return

        update_agent_status("inventory_optimizer", "running", 80)

        # 結果
        optimization_result = {
            "recommended_order": 280,
            "supplier": "Supplier A",
            "unit_cost": 120,
            "total_cost": 33600
        }

        add_log("success", f"📦 推奨発注量: {optimization_result['recommended_order']} 個",
                agent="inventory_optimizer", details=optimization_result)
        update_agent_status("inventory_optimizer", "completed", 100)

        await asyncio.sleep(1)

        # ==========================================
        # Phase 3: レポート生成エージェント
        # ==========================================
        add_log("info", "📄 Phase 3: レポート生成エージェント", agent="report_generator")
        update_agent_status("report_generator", "running", 10)

        await asyncio.sleep(1)

        add_log("info", "   最適化結果を集計中...", agent="report_generator")
        update_agent_status("report_generator", "running", 40)

        await asyncio.sleep(2)
        add_log("success", "   ✅ レポート生成完了", agent="report_generator")
        update_agent_status("report_generator", "running", 70)

        # 決済処理（実ブロックチェーン）
        add_log("payment", f"💰 決済処理開始: 5 JPYC", agent="report_generator")
        add_log("info", f"   送信先: {agent_wallets['report_generator']}",
                agent="report_generator")

        # 実際のJPYC送金
        try:
            tx_hash3 = blockchain_service.transfer_jpyc(
                to_address=agent_wallets['report_generator'],
                amount=5  # 5 JPYC
            )
            add_log("info", f"   トランザクション送信中...", agent="report_generator")
            add_log("info", f"   TX: {tx_hash3}", agent="report_generator")

            await asyncio.sleep(3)

            add_log("transaction", f"✅ トランザクション成功", agent="report_generator", details={
                "tx_hash": tx_hash3,
                "amount": 5,
                "address": agent_wallets['report_generator'],
                "explorer": f"https://amoy.polygonscan.com/tx/{tx_hash3}"
            })

            add_transaction(
                agent="レポート生成エージェント",
                amount=5,
                address=agent_wallets['report_generator'],
                tx_hash=tx_hash3
            )
        except Exception as e:
            add_log("error", f"❌ 決済エラー: {str(e)}", agent="report_generator")
            update_agent_status("report_generator", "error", 0)
            return

        # レポート結果
        total_cost = 3 + 15 + 5  # 23 JPYC
        report_result = {
            "forecast_accuracy": "98%",
            "recommended_order": optimization_result["recommended_order"],
            "predicted_demand": forecast_result["predicted_demand"],
            "expected_gross_profit": 22400,  # 280個 × (200円 - 120円)
            "expected_loss_rate": "4.5%",
            "cost_reduction": 3200,  # 従来比
            "roi": "2182%",
            "execution_time": "45秒",
            "total_cost": f"{total_cost} JPYC"
        }

        add_log("success", f"📊 レポート生成完了", agent="report_generator", details=report_result)
        add_log("info", f"   需要予測精度: {report_result['forecast_accuracy']}", agent="report_generator")
        add_log("info", f"   推奨発注量: {report_result['recommended_order']}個", agent="report_generator")
        add_log("info", f"   予想粗利: ¥{report_result['expected_gross_profit']:,}", agent="report_generator")
        add_log("info", f"   予想ロス率: {report_result['expected_loss_rate']} (従来12% → 目標達成)", agent="report_generator")
        add_log("info", f"   コスト削減効果: ¥{report_result['cost_reduction']:,}/日", agent="report_generator")

        update_agent_status("report_generator", "completed", 100)

        # ==========================================
        # 完了
        # ==========================================
        await asyncio.sleep(1)
        add_log("success", f"🎉 すべてのエージェント実行完了！")
        add_log("info", f"   総決済額: {total_cost} JPYC")
        add_log("info", f"   トランザクション数: {len(transactions)}")
        add_log("info", f"   実行時間: 約45秒")

        # 最終残高確認
        final_balance = blockchain_service.get_balance()
        add_log("info", f"   Deployer残高（決済後）: {final_balance['jpyc_balance']:,} JPYC")

        # タスク完了通知（フロントエンド用）
        current_logs.append({
            "type": "task_complete",
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "message": "Task completed successfully"
        })

    except Exception as e:
        add_log("error", f"❌ エラー: {str(e)}")
        for agent in current_status:
            update_agent_status(agent, "error", 0)

        # エラー時も完了通知
        current_logs.append({
            "type": "task_complete",
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "message": "Task failed"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
