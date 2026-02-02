# Phase 5 実装計画：UI実装 + ウォレット連携

**作成日**: 2026-02-02
**対象期間**: 1-2週間
**前提**: Phase 4完了（Polygon Amoy統合、公式テストJPYC統合確認済み）

---

## 📋 Phase 4完了時の状況

### ✅ 達成済み

- Polygon Amoyにコントラクトデプロイ
  - ERC8004 Identity: `0x4E30252d10316E0A360023a8264A407625250C45`
  - ERC8004 Reputation: `0xeFe985B85B04715b866C67eA971ABBb9F3848466`
  - MockJPYC（初期テスト用）: `0xafac6B9175D5c51C5F73ab1aAb6d2c35bDC3A302`
- 公式テストJPYC統合: `0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29`
- BlockchainService実装（Web3.py）
- X402Client実装（3つの決済スキーム）
- LLMエージェント統合（CrewAI + gemma2:9b）
- E2Eテスト（Phase 1成功確認）

### 🔧 Phase 5で修正が必要な項目

#### 1. エージェント用ウォレット設定

**現状の問題:**
```python
# test_e2e_with_real_payments.py
payment_address=blockchain_service.address  # 自分自身に送信（テスト用）
```

**修正内容:**
```python
# 各エージェント専用のウォレットアドレスを設定
AGENT_WALLETS = {
    "demand_forecast": "0x...",    # エージェント1のウォレット
    "inventory_optimizer": "0x...", # エージェント2のウォレット
    "report_generator": "0x..."     # エージェント3のウォレット
}

payment_address=AGENT_WALLETS[agent_type]
```

**実装方法:**
- 新しいウォレットを3つ生成（`cast wallet new`）
- .envに追加
- テストJPYCを各ウォレットに配布（faucet）

---

## 🎯 Phase 5 実装タスク

### タスク1: エージェントウォレットのセットアップ（1時間）

#### 1.1 ウォレット生成
```bash
# 3つのエージェント用ウォレットを生成
cast wallet new  # エージェント1
cast wallet new  # エージェント2
cast wallet new  # エージェント3
```

#### 1.2 .env設定
```bash
# .envに追加
AGENT_DEMAND_FORECAST_ADDRESS=0x...
AGENT_DEMAND_FORECAST_PRIVATE_KEY=0x...

AGENT_INVENTORY_OPTIMIZER_ADDRESS=0x...
AGENT_INVENTORY_OPTIMIZER_PRIVATE_KEY=0x...

AGENT_REPORT_GENERATOR_ADDRESS=0x...
AGENT_REPORT_GENERATOR_PRIVATE_KEY=0x...
```

#### 1.3 テスト資金配布
- 各ウォレットにテストMATIC配布（faucet）
- 各ウォレットにテストJPYC配布（faucet）

#### 1.4 決済フロー修正
- `test_e2e_with_real_payments.py` 修正
- `protocols/x402/client.py` 修正（必要に応じて）

---

### タスク2: バックエンドAPI実装（1日）

#### 2.1 FastAPI エンドポイント作成

**ファイル:** `python/api/main.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class OptimizationRequest(BaseModel):
    product_sku: str
    store_id: str
    weather: str
    day_type: str

@app.post("/api/optimize")
async def optimize(request: OptimizationRequest):
    """最適化タスクを実行"""
    # orchestratorを呼び出し
    # X402決済を実行
    # 結果を返す
    pass

@app.get("/api/transactions")
async def get_transactions():
    """X402決済履歴を取得"""
    pass

@app.get("/api/agents")
async def get_agents():
    """エージェント情報を取得"""
    pass
```

#### 2.2 CORS設定
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### タスク3: フロントエンド基盤構築（1日）

#### 3.1 Next.js プロジェクト作成

```bash
# プロジェクトルートで実行
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install
```

#### 3.2 必要なライブラリインストール

```bash
# Web3関連
npm install ethers wagmi viem @rainbow-me/rainbowkit

# UI関連
npm install @headlessui/react @heroicons/react
npm install react-hot-toast  # 通知
npm install recharts  # グラフ表示
```

#### 3.3 プロジェクト構造

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # ホーム
│   │   ├── dashboard/
│   │   │   └── page.tsx          # ダッシュボード
│   │   ├── agents/
│   │   │   └── page.tsx          # エージェント管理
│   │   └── transactions/
│   │       └── page.tsx          # トランザクション履歴
│   ├── components/
│   │   ├── WalletConnect.tsx     # Metamask接続
│   │   ├── OptimizationForm.tsx  # 最適化実行フォーム
│   │   ├── TransactionList.tsx   # トランザクション一覧
│   │   └── AgentCard.tsx         # エージェントカード
│   ├── hooks/
│   │   ├── useWallet.ts          # ウォレットフック
│   │   └── useOptimization.ts    # 最適化フック
│   └── lib/
│       ├── api.ts                # バックエンドAPI呼び出し
│       └── contracts.ts          # コントラクトABI
```

---

### タスク4: Metamask連携実装（2日）

#### 4.1 RainbowKit セットアップ

**ファイル:** `frontend/src/app/providers.tsx`

```typescript
'use client';

import { RainbowKitProvider, getDefaultWallets } from '@rainbow-me/rainbowkit';
import { configureChains, createConfig, WagmiConfig } from 'wagmi';
import { polygonAmoy } from 'wagmi/chains';
import { publicProvider } from 'wagmi/providers/public';

const { chains, publicClient } = configureChains(
  [polygonAmoy],
  [publicProvider()]
);

const { connectors } = getDefaultWallets({
  appName: 'A2A Supply Chain',
  projectId: 'YOUR_PROJECT_ID',
  chains
});

const wagmiConfig = createConfig({
  autoConnect: true,
  connectors,
  publicClient
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiConfig config={wagmiConfig}>
      <RainbowKitProvider chains={chains}>
        {children}
      </RainbowKitProvider>
    </WagmiConfig>
  );
}
```

#### 4.2 ウォレット接続ボタン

**ファイル:** `frontend/src/components/WalletConnect.tsx`

```typescript
import { ConnectButton } from '@rainbow-me/rainbowkit';

export function WalletConnect() {
  return <ConnectButton />;
}
```

#### 4.3 JPYC残高表示

```typescript
import { useAccount, useContractRead } from 'wagmi';

const JPYC_ADDRESS = '0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29';
const JPYC_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: 'balance', type: 'uint256' }],
  },
];

export function JPYCBalance() {
  const { address } = useAccount();

  const { data: balance } = useContractRead({
    address: JPYC_ADDRESS,
    abi: JPYC_ABI,
    functionName: 'balanceOf',
    args: [address],
  });

  return <div>JPYC残高: {balance?.toString()} JPYC</div>;
}
```

---

### タスク5: ダッシュボード実装（2日）

#### 5.1 最適化実行フォーム

**機能:**
- 商品選択（ドロップダウン）
- 店舗選択
- 天気・曜日タイプ選択
- 「最適化実行」ボタン
- 進捗表示（ローディング）

#### 5.2 リアルタイム進捗表示

```typescript
// WebSocket or Server-Sent Eventsで進捗を受信
const [progress, setProgress] = useState({
  phase: 'idle', // idle, demand_forecast, inventory_optimizer, report
  status: 'pending', // pending, in_progress, completed
  transaction: null
});

// 進捗バー表示
<ProgressBar
  phases={[
    { name: '需要予測', status: progress.phase === 'demand_forecast' ? 'in_progress' : 'completed' },
    { name: '在庫最適化', status: progress.phase === 'inventory_optimizer' ? 'in_progress' : 'pending' },
    { name: 'レポート生成', status: progress.phase === 'report' ? 'in_progress' : 'pending' }
  ]}
/>
```

#### 5.3 結果表示

- 需要予測結果（グラフ）
- 推奨発注量
- サプライヤー情報
- コスト内訳（X402決済）
- トランザクションリンク（Polygonscan）

---

### タスク6: User-to-Agent決済実装（2日）

#### 6.1 決済フロー（2パターン実装）

**パターンA: バックエンド決済（既存）**
```typescript
// ユーザーはMetamask不要
async function runOptimizationWithBackend() {
  const response = await fetch('/api/optimize', {
    method: 'POST',
    body: JSON.stringify(request)
  });
  // バックエンドが自動で決済
}
```

**パターンB: ユーザー決済（新規実装）**
```typescript
// ユーザーがMetamaskで承認
async function runOptimizationWithUserPayment() {
  // 1. ウォレット接続確認
  if (!isConnected) {
    await connectWallet();
  }

  // 2. JPYC approve（初回のみ）
  const allowance = await jpycContract.allowance(userAddress, agentAddress);
  if (allowance < totalCost) {
    await jpycContract.approve(agentAddress, totalCost);
  }

  // 3. 決済実行
  const tx = await jpycContract.transfer(agentAddress, totalCost);
  await tx.wait();

  // 4. バックエンドに最適化実行を依頼
  await fetch('/api/optimize', {
    method: 'POST',
    body: JSON.stringify({ ...request, tx_hash: tx.hash })
  });
}
```

#### 6.2 決済モーダル

```typescript
<PaymentModal
  isOpen={showPaymentModal}
  amount={totalCost}
  breakdown={[
    { agent: '需要予測', cost: 3 },
    { agent: '在庫最適化', cost: 15 },
    { agent: 'レポート生成', cost: 5 }
  ]}
  onApprove={handlePayment}
  onCancel={() => setShowPaymentModal(false)}
/>
```

---

### タスク7: トランザクション履歴（1日）

#### 7.1 トランザクション一覧表示

```typescript
interface Transaction {
  id: string;
  timestamp: Date;
  agent: string;
  amount: number;
  tx_hash: string;
  status: 'pending' | 'completed' | 'failed';
}

<TransactionList transactions={transactions} />
```

#### 7.2 フィルター・検索機能

- エージェントでフィルター
- 日付範囲でフィルター
- トランザクションハッシュで検索

---

### タスク8: エージェント管理ページ（1日）

#### 8.1 エージェント一覧

```typescript
<AgentCard
  name="需要予測エージェント"
  id={1}
  address="0x..."
  balance="100 JPYC"
  totalEarned="1,500 JPYC"
  totalRequests={150}
  averageResponseTime="2.3s"
/>
```

#### 8.2 エージェントステータス

- オンライン/オフライン
- 稼働時間
- 成功率
- 平均レスポンスタイム

---

## 📅 実装スケジュール

| タスク | 期間 | 優先度 |
|--------|------|--------|
| 1. エージェントウォレットセットアップ | 1h | 🔴 高 |
| 2. バックエンドAPI実装 | 1日 | 🔴 高 |
| 3. フロントエンド基盤構築 | 1日 | 🔴 高 |
| 4. Metamask連携実装 | 2日 | 🟡 中 |
| 5. ダッシュボード実装 | 2日 | 🔴 高 |
| 6. User-to-Agent決済実装 | 2日 | 🟡 中 |
| 7. トランザクション履歴 | 1日 | 🟢 低 |
| 8. エージェント管理ページ | 1日 | 🟢 低 |

**合計見積**: 10-12日

---

## 🎯 Phase 5 完了基準

### 必須（Must Have）

- ✅ Metamask接続機能
- ✅ 最適化実行ボタン
- ✅ 結果表示（需要予測、発注量、コスト）
- ✅ エージェント → エージェント決済動作
- ✅ トランザクション履歴表示
- ✅ Polygonscanリンク

### 推奨（Should Have）

- リアルタイム進捗表示
- User → Agent決済機能
- グラフ・チャート表示
- エージェント管理ページ

### オプション（Nice to Have）

- ダークモード
- 多言語対応
- モバイル対応
- 通知機能

---

## 🔧 開発環境

### フロントエンド
```bash
cd frontend
npm run dev  # http://localhost:3000
```

### バックエンド
```bash
cd python
uvicorn api.main:app --reload  # http://localhost:8000
```

### Docker Compose（統合）
```bash
docker-compose up
```

---

## 📝 メモ・注意事項

### Phase 4からの引き継ぎ事項

1. **決済アドレスの修正**
   - 現在: 自分自身に送信（テスト用）
   - 修正後: エージェント専用ウォレットに送信

2. **公式テストJPYC使用**
   - Contract: `0xE7C3D8C9a439feDe00D2600032D5dB0Be71C3c29`
   - Faucetから取得済み: 1,000,000 JPYC

3. **LLMタイムアウト対策**
   - gemma2:9b でタイムアウト発生（Phase 2）
   - 代替案: gemma2:2b 使用、またはタイムアウト延長

---

## 🚀 明日の開始手順

### 1. 環境確認
```bash
# Docker起動確認
docker-compose ps

# Ollama確認
docker-compose exec ollama ollama list
```

### 2. エージェントウォレット生成
```bash
# 3つのウォレットを生成
cast wallet new > agent1_wallet.txt
cast wallet new > agent2_wallet.txt
cast wallet new > agent3_wallet.txt
```

### 3. Next.jsプロジェクト作成
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install ethers wagmi viem @rainbow-me/rainbowkit
```

### 4. 最初のコミット
```bash
git add frontend/
git commit -m "feat: Initialize Next.js frontend for Phase 5"
```

---

**作成者**: Claude Code
**最終更新**: 2026-02-02
**次回更新**: Phase 5実装開始時
