# 生鮮品サプライチェーン最適化AI協調システム

X402 v2プロトコル、ERC-8004、JPYCを活用したマルチエージェント決済システムのサンプル実装

## 📋 プロジェクト概要

このプロジェクトは、AIエージェントが協調して生鮮品の需要予測・在庫最適化・価格設定を行い、X402マイクロペイメントで決済し、ERC-8004で信頼性を担保するA2A（Agent-to-Agent）経済圏のデモンストレーションです。

**主な目的:**
- X402 v2プロトコルとERC-8004の体系的理解
- マイクロペイメント決済システムの実装パターン習得
- Python + Foundry + Anvilでの開発環境構築
- チーム全体へのナレッジ共有

**ビジネス効果:**
- 食品ロス削減: 年間約3億円 → 1.1億円（-63%）
- 粗利率改善: 42% → 45.2%（+3.2pt）
- 予測精度向上: MAPE 15% → 8.2%

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│           ユーザー（バイヤー）                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         最終サマリー生成エージェント              │
│              (5 JPYC - deferred)                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           総合検証エージェント                    │
│              (5 JPYC - exact)                   │
│         ★A2A経済圏の本質★                        │
└─────┬──────────┬──────────┬────────────┬────────┘
      │          │          │            │
      ▼          ▼          ▼            ▼
┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│需要予測  │ │在庫最適化│ │価格設定  │ │品質検証  │
│(10 JPYC) │ │(15 JPYC)│ │(12 JPYC) │ │(8 JPYC)  │
│  upto    │ │  exact  │ │  upto    │ │  exact   │
└──────────┘ └─────────┘ └──────────┘ └────┬─────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │  DID/VC基盤   │
                                    │サプライヤー認証│
                                    └───────────────┘
      │          │          │            │
      └──────────┴──────────┴────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  X402 Facilitator  │
        │  (JPYC決済処理)    │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │   Blockchain       │
        │  (ERC-8004)        │
        │  - Identity        │
        │  - Reputation      │
        │  - Validation      │
        └────────────────────┘
```

## 🛠️ 技術スタック

### ブロックチェーン
- **開発**: Anvil (Foundry)
- **テスト**: Sepolia testnet
- **本番想定**: Polygon

### スマートコントラクト
- **フレームワーク**: Foundry
- **言語**: Solidity ^0.8.20
- **標準**: ERC-8004 (Trustless Agents)

### バックエンド
- **言語**: Python 3.11+
- **Web3**: web3.py
- **ML**: scikit-learn, LightGBM
- **エージェント**: LangChain / AutoGen

### 決済・認証
- **プロトコル**: X402 v2
- **通貨**: JPYC (日本円ステーブルコイン)
- **認証**: DID/VC (既存コンソーシアム基盤)

## 📁 ディレクトリ構造

```
a2a-supply-chain-project/
├── docs/
│   ├── requirements/          # 要件定義書
│   │   └── usecase-requirements.md
│   ├── specifications/        # 技術仕様書（今後作成）
│   └── diagrams/             # アーキテクチャ図、シーケンス図
├── contracts/                # Solidityスマートコントラクト
│   ├── src/
│   ├── test/
│   └── script/
├── python/                   # Pythonエージェント実装
│   ├── agents/
│   ├── protocols/
│   └── utils/
├── tests/                    # 統合テスト
└── README.md
```

## 🚀 クイックスタート

### 前提条件

```bash
# Foundryインストール
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Pythonインストール（3.11+）
python --version

# 依存パッケージ
pip install web3 python-dotenv requests
```

### ローカル開発環境セットアップ

```bash
# リポジトリクローン
cd a2a-supply-chain-project

# Anvilローカルチェーン起動
anvil

# 別のターミナルで
# スマートコントラクトデプロイ（予定）
cd contracts
forge build
forge test

# Pythonエージェント実行（予定）
cd python
python main.py
```

## 📊 実装フェーズ

### Phase 1: MVP（1-2週間）
- [x] 要件定義完了
- [ ] 需要予測エージェント実装
- [ ] 在庫最適化エージェント実装
- [ ] X402 exact決済実装
- [ ] Anvilローカル動作確認

### Phase 2: プロトコル拡張（1週間）
- [ ] 価格設定エージェント追加
- [ ] ERC-8004 Identity Registry実装
- [ ] X402 upto決済実装
- [ ] Sepolia testnet展開

### Phase 3: 信頼レイヤー（2週間）★重要
- [ ] DID/VC統合（品質検証エージェント）
- [ ] 総合検証エージェント実装
- [ ] ERC-8004 Reputation Registry実装
- [ ] ERC-8004 Validation Registry実装
- [ ] X402 deferred決済実装

### Phase 4: 本番展開（3ヶ月）
- [ ] 西友統合対応
- [ ] 全店舗・全商品スケール
- [ ] Polygon本番環境移行
- [ ] ダッシュボード構築

## 📖 ドキュメント

- [要件定義書](./docs/requirements/usecase-requirements.md)
- 技術仕様書（作成予定）
- シーケンス図（作成予定）
- API仕様書（作成予定）

## 🎯 主要KPI

| 指標 | 現状 | 目標 | 改善率 |
|------|------|------|--------|
| 食品ロス率 | 12% | 4.5% | -62.5% |
| 粗利率 | 42% | 45.2% | +3.2pt |
| 予測精度（MAPE） | 15% | 8.2% | -45% |
| 意思決定時間 | 30分 | 45秒 | -97.5% |

## 🔗 関連リソース

### プロトコル・標準
- [X402 v2](https://x402.org)
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)
- [JPYC Documentation](https://jpyc.gitbook.io)

### 技術リファレンス
- [Foundry Book](https://book.getfoundry.sh)
- [web3.py](https://web3py.readthedocs.io)
- [A2A Protocol](https://a2a-protocol.org)

## 📝 ライセンス

TBD

## 👥 コントリビューター

プロジェクトチームメンバー向けのナレッジ共有プロジェクトです。

---

**Last Updated**: 2025-01-22