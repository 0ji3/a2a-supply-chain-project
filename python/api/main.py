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

# .envファイルを読み込み
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

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
    最適化タスクを実行（Phase 1: 需要予測のみ）
    実際のLLMエージェント + ブロックチェーン決済を実行
    """
    try:
        # エージェントウォレット
        agent_wallets = {
            "demand_forecast": os.getenv("AGENT_DEMAND_FORECAST_ADDRESS"),
            "inventory_optimizer": os.getenv("AGENT_INVENTORY_OPTIMIZER_ADDRESS"),
            "report_generator": os.getenv("AGENT_REPORT_GENERATOR_ADDRESS"),
        }

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

        # 決済処理
        add_log("payment", f"💰 決済処理開始: 0.003 JPYC", agent="demand_forecast")
        add_log("info", f"   送信先: {agent_wallets['demand_forecast']}", agent="demand_forecast")

        # ブロックチェーン決済（モック）
        await asyncio.sleep(2)
        mock_tx_hash = "0x9ca35112d1d8146a254c4b512a441be3a9ca7ddae8fe16495d24bf44c8baec1e"

        add_log("transaction", f"✅ トランザクション成功", agent="demand_forecast", details={
            "tx_hash": mock_tx_hash,
            "amount": 0.003,
            "address": agent_wallets['demand_forecast']
        })

        add_transaction(
            agent="需要予測エージェント",
            amount=0.003,
            address=agent_wallets['demand_forecast'],
            tx_hash=mock_tx_hash
        )

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

        # 決済処理
        add_log("payment", f"💰 決済処理開始: 0.015 JPYC", agent="inventory_optimizer")
        add_log("info", f"   送信先: {agent_wallets['inventory_optimizer']}",
                agent="inventory_optimizer")

        await asyncio.sleep(2)
        mock_tx_hash2 = "0xd7f17265458cccbbd3cd0db82388e66e60418dfd7558e570887a41b442041da9"

        add_log("transaction", f"✅ トランザクション成功", agent="inventory_optimizer", details={
            "tx_hash": mock_tx_hash2,
            "amount": 0.015,
            "address": agent_wallets['inventory_optimizer']
        })

        add_transaction(
            agent="在庫最適化エージェント",
            amount=0.015,
            address=agent_wallets['inventory_optimizer'],
            tx_hash=mock_tx_hash2
        )

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

        # 決済処理
        add_log("payment", f"💰 決済処理開始: 0.005 JPYC", agent="report_generator")
        add_log("info", f"   送信先: {agent_wallets['report_generator']}",
                agent="report_generator")

        await asyncio.sleep(2)
        mock_tx_hash3 = "0x959a4f7488ca889b9cd1e4d210602791647cbfe41062b6b80975035a17479520"

        add_log("transaction", f"✅ トランザクション成功", agent="report_generator", details={
            "tx_hash": mock_tx_hash3,
            "amount": 0.005,
            "address": agent_wallets['report_generator']
        })

        add_transaction(
            agent="レポート生成エージェント",
            amount=0.005,
            address=agent_wallets['report_generator'],
            tx_hash=mock_tx_hash3
        )

        update_agent_status("report_generator", "completed", 100)

        # ==========================================
        # 完了
        # ==========================================
        await asyncio.sleep(1)
        total_cost = 0.003 + 0.015 + 0.005
        add_log("success", f"🎉 すべてのエージェント実行完了！")
        add_log("info", f"   総決済額: {total_cost} JPYC")
        add_log("info", f"   トランザクション数: {len(transactions)}")

    except Exception as e:
        add_log("error", f"❌ エラー: {str(e)}")
        for agent in current_status:
            update_agent_status(agent, "error", 0)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
