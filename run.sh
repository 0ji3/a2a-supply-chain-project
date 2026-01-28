#!/bin/bash
# A2A Supply Chain MVP - 実行スクリプト

echo "=== A2A Supply Chain MVP - 起動中 ==="
echo ""

# Dockerコンテナ確認
echo "1. Dockerコンテナ確認..."
docker-compose ps

echo ""
echo "2. データベース接続テスト..."
docker-compose exec -T postgres psql -U postgres -d a2a_supply_chain -c "SELECT COUNT(*) as pos_records FROM pos_sales;"

echo ""
echo "3. MVPアプリケーション実行..."
./venv/bin/python python/main.py

echo ""
echo "=== 実行完了 ==="
