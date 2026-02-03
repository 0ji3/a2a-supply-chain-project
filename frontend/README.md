# A2A Supply Chain - Live Demo Dashboard

エージェント協調制御 + ブロックチェーン決済のリアルタイムモニタリングダッシュボード

## 特徴

- **リアルタイムログストリーミング** - Server-Sent Events (SSE) によるライブログ表示
- **ターミナル風UI** - 開発者コンソールスタイルのログビューア
- **エージェントステータス** - 各エージェントの進捗状況をリアルタイム表示
- **トランザクション履歴** - ブロックチェーン決済の詳細情報
- **Polygonscan連携** - トランザクションをエクスプローラーで確認可能

## セットアップ

```bash
# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

http://localhost:3000 でアクセス

## バックエンド要件

バックエンドAPIが `http://localhost:8000` で起動している必要があります。

```bash
cd ../python
uvicorn api.main:app --reload --port 8000
```

## 使い方

1. 「🚀 最適化タスクを開始」ボタンをクリック
2. リアルタイムでエージェントの動作を観察
3. ログストリームで詳細な処理内容を確認
4. トランザクション履歴で決済情報をチェック

## 技術スタック

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Server-Sent Events (SSE)
