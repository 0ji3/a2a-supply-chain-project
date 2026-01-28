# コーディング規約

このドキュメントは、プロジェクト全体で統一されたコーディングスタイルを維持するための規約です。

---

## 📋 目次

1. [Python コーディング規約](#1-python-コーディング規約)
2. [Solidity コーディング規約](#2-solidity-コーディング規約-phase-2以降)
3. [Git コミット規約](#3-git-コミット規約)
4. [ドキュメント規約](#4-ドキュメント規約)

---

## 1. Python コーディング規約

### 1.1 基本原則

- **PEP 8** を基本として従う
- **PEP 257** (Docstring) を遵守
- **型ヒント** を可能な限り使用（Python 3.11+）
- **可読性** を最優先

### 1.2 コードフォーマット

#### Black（自動フォーマッター）

```bash
# 実行
black python/

# 設定（pyproject.tomlまたはsetup.cfg）
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # 除外ディレクトリ
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

**ルール**:
- 行の最大長: 100文字
- インデント: スペース4つ
- 文字列: ダブルクォート `"` を使用

#### isort（インポート整理）

```bash
# 実行
isort python/

# 設定（pyproject.toml）
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
```

**インポート順序**:
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルアプリケーション

```python
# Good
import os
from datetime import datetime
from typing import Dict, List

import numpy as np
from fastapi import FastAPI
from sqlalchemy import create_engine

from agents.base import Agent
from config import settings
```

### 1.3 命名規約

| 種類 | 規約 | 例 |
|------|------|-----|
| **モジュール** | snake_case | `demand_forecast.py` |
| **クラス** | PascalCase | `DemandForecastAgent` |
| **関数** | snake_case | `execute_optimization()` |
| **変数** | snake_case | `predicted_demand` |
| **定数** | UPPER_CASE | `MAX_RETRIES = 3` |
| **プライベート** | _prefix | `_fetch_pos_data()` |

**例**:
```python
# クラス
class AgentCoordinator:
    pass

# 定数
MAX_CACHE_TTL = 86400

# 関数
def calculate_cost(usage_metrics: Dict) -> int:
    pass

# プライベートメソッド
def _internal_method(self):
    pass
```

### 1.4 型ヒント

**常に型ヒントを使用**:

```python
# Good
from typing import Dict, List, Optional

async def execute(self, input_data: Dict) -> AgentResult:
    predicted_demand: int = 350
    confidence: float = 0.85
    return AgentResult(...)

def get_supplier(self, supplier_id: str) -> Optional[Dict]:
    pass

# Bad
async def execute(self, input_data):
    predicted_demand = 350
    return AgentResult(...)
```

**複雑な型の場合はTypeAliasを使用**:
```python
from typing import Dict, List, TypeAlias

POSDataRow: TypeAlias = Dict[str, any]
POSData: TypeAlias = List[POSDataRow]

def fetch_pos_data(...) -> POSData:
    pass
```

### 1.5 Docstring

**Google Style** を使用:

```python
def execute_optimization_task(
    self,
    product_sku: str,
    store_id: str
) -> OptimizationResult:
    """
    最適化タスクの実行
    
    Args:
        product_sku: 商品SKU（例: "tomato-medium-domestic"）
        store_id: 店舗ID（例: "S001"）
        
    Returns:
        OptimizationResult: 最適化結果
        
    Raises:
        ValueError: product_skuまたはstore_idが不正な場合
        DatabaseError: データベース接続エラー
        
    Examples:
        >>> coordinator = AgentCoordinator()
        >>> result = await coordinator.execute_optimization_task(
        ...     "tomato-medium-domestic",
        ...     "S001"
        ... )
    """
    pass
```

**モジュールレベル**:
```python
"""
需要予測エージェント

POSデータと気象データから翌日の販売数量を予測する。
Phase 1では簡易的な移動平均ベースの予測を使用。

Classes:
    DemandForecastAgent: 需要予測エージェント

Usage:
    agent = DemandForecastAgent()
    result = await agent.execute(input_data)
"""
```

### 1.6 エラーハンドリング

**具体的な例外を使用**:

```python
# Good
try:
    result = await self._fetch_pos_data(...)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    return AgentResult(success=False, error_message=str(e))

# Bad
try:
    result = await self._fetch_pos_data(...)
except Exception as e:
    pass  # エラーを無視しない
```

**カスタム例外の定義**:
```python
# python/exceptions.py
class A2AException(Exception):
    """基底例外クラス"""
    pass

class AgentExecutionError(A2AException):
    """エージェント実行エラー"""
    pass

class DatabaseConnectionError(A2AException):
    """データベース接続エラー"""
    pass
```

### 1.7 ロギング

**標準ライブラリのloggingを使用**:

```python
import logging

logger = logging.getLogger(__name__)

# レベル別使用
logger.debug("詳細なデバッグ情報")
logger.info("一般的な情報")
logger.warning("警告")
logger.error("エラー")
logger.critical("致命的エラー")

# コンテキスト情報を含める
logger.error(
    "Agent execution failed",
    extra={
        "agent_name": self.name,
        "execution_id": execution_id,
        "error": str(e)
    }
)
```

### 1.8 非同期処理

**asyncio使用時の規約**:

```python
# Good
async def execute(self, input_data: Dict) -> AgentResult:
    # awaitを使用
    result = await self._fetch_data()
    return result

# I/O処理は非同期に
async def _fetch_pos_data(self, ...):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Bad
async def execute(self, input_data: Dict):
    # 同期処理を非同期関数内で使用（blocking）
    time.sleep(1)  # NG
    # 代わりに asyncio.sleep(1) を使用
```

### 1.9 テスト

**pytest使用時の規約**:

```python
# tests/test_demand_forecast.py
import pytest
from python.agents.demand_forecast import DemandForecastAgent


class TestDemandForecastAgent:
    """需要予測エージェントのテスト"""
    
    @pytest.fixture
    def agent(self):
        """テスト用エージェントインスタンス"""
        return DemandForecastAgent()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """正常系テスト"""
        # Arrange
        input_data = {...}
        
        # Act
        result = await agent.execute(input_data)
        
        # Assert
        assert result.success is True
        assert result.cost == 3
    
    @pytest.mark.asyncio
    async def test_execute_missing_input(self, agent):
        """異常系テスト: 入力不足"""
        # Arrange
        input_data = {}
        
        # Act
        result = await agent.execute(input_data)
        
        # Assert
        assert result.success is False
        assert "Missing required input" in result.error_message
```

**テストファイル命名**:
- `test_<module_name>.py`
- テスト関数: `test_<function_name>_<scenario>`

---

## 2. Solidity コーディング規約（Phase 2以降）

### 2.1 基本原則

- **Solidity Style Guide** を遵守
- **最新のセキュリティベストプラクティス** を適用
- **ガス効率** を考慮

### 2.2 命名規約

```solidity
// コントラクト: PascalCase
contract ERC8004Identity {
    // 定数: UPPER_CASE
    uint256 public constant MAX_AGENTS = 10000;
    
    // 状態変数: camelCase
    mapping(uint256 => AgentMetadata) public agents;
    uint256 private _nextAgentId;
    
    // 関数: camelCase
    function register(string memory _name) external returns (uint256) {
        // ...
    }
    
    // イベント: PascalCase
    event AgentRegistered(uint256 indexed agentId, string name);
}
```

### 2.3 セキュリティチェック

```solidity
// Good
function register(string memory _name) external {
    require(bytes(_name).length > 0, "Name cannot be empty");
    require(_nextAgentId < MAX_AGENTS, "Maximum agents reached");
    
    // Checks-Effects-Interactions pattern
    uint256 agentId = _nextAgentId++;
    agents[agentId] = AgentMetadata({...});
    
    emit AgentRegistered(agentId, _name);
}

// OpenZeppelin使用
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
```

---

## 3. Git コミット規約

### 3.1 コミットメッセージフォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 Type（必須）

| Type | 説明 | 例 |
|------|------|-----|
| `feat` | 新機能 | `feat(agents): add report generator agent` |
| `fix` | バグ修正 | `fix(database): resolve connection pool leak` |
| `docs` | ドキュメント | `docs: update README with setup instructions` |
| `style` | コードフォーマット | `style: apply black formatting` |
| `refactor` | リファクタリング | `refactor(orchestrator): simplify task execution` |
| `test` | テスト追加・修正 | `test: add integration tests for API` |
| `chore` | ビルド・設定 | `chore: update dependencies` |
| `perf` | パフォーマンス改善 | `perf(cache): optimize Redis key structure` |

### 3.3 Scope（オプション）

- `agents`: エージェント関連
- `api`: REST API関連
- `database`: データベース関連
- `contracts`: スマートコントラクト関連
- `docs`: ドキュメント関連

### 3.4 例

```bash
# Good
git commit -m "feat(agents): implement demand forecast caching"
git commit -m "fix(database): add missing index on pos_sales table"
git commit -m "docs: add phase1 implementation guide"

# Subject + Body
git commit -m "feat(api): add optimize endpoint

Implement POST /api/v1/optimize endpoint for task creation.
- Add request validation
- Implement background task execution
- Add error handling"

# Breaking Change
git commit -m "feat(agents)!: change AgentResult data structure

BREAKING CHANGE: AgentResult.data is now always a dict.
Previous code expecting different types must be updated."
```

### 3.5 ブランチ戦略

```
main (production)
  ↑
develop (development)
  ↑
feature/xxx (feature branches)
```

**ブランチ命名**:
- `feature/<issue-number>-<description>`: 新機能
- `fix/<issue-number>-<description>`: バグ修正
- `docs/<description>`: ドキュメント
- `refactor/<description>`: リファクタリング

**例**:
```bash
git checkout -b feature/23-report-generator
git checkout -b fix/45-database-connection
git checkout -b docs/coding-standards
```

---

## 4. ドキュメント規約

### 4.1 Markdownフォーマット

- **見出し**: `#` で階層化
- **コードブロック**: 言語指定 ` ```python `
- **リスト**: 統一した記号（`-` または `*`）
- **リンク**: 相対パスで記載

### 4.2 ドキュメント構造

```markdown
# タイトル

**ドキュメント情報**:
- バージョン: 1.0.0
- 最終更新: 2025-01-23

---

## 目次

1. [セクション1](#1-セクション1)
2. [セクション2](#2-セクション2)

---

## 1. セクション1

### 1.1 サブセクション

内容...

---

## まとめ

**最終更新**: 2025-01-23
```

### 4.3 コード例の記載

```markdown
## 使用例

### Python

\```python
# コメント
agent = DemandForecastAgent()
result = await agent.execute(input_data)
\```

### Bash

\```bash
# コマンド実行
docker-compose up -d
\```
```

---

## ✅ チェックリスト

コミット前に以下を確認:

### コード品質
- [ ] Black でフォーマット済み
- [ ] isort でインポート整理済み
- [ ] flake8 でリント済み（エラーなし）
- [ ] mypy で型チェック済み（重大なエラーなし）

### テスト
- [ ] 新規コードに対応するテストを追加
- [ ] すべてのテストが成功（`pytest tests/ -v`）
- [ ] カバレッジが低下していない

### ドキュメント
- [ ] 新機能にDocstringを追加
- [ ] README/ドキュメントを更新
- [ ] コミットメッセージが規約に従っている

### セキュリティ
- [ ] 機密情報（秘密鍵など）がコードに含まれていない
- [ ] 環境変数を適切に使用
- [ ] ユーザー入力のバリデーション実装

---

## 🛠️ 自動化

### pre-commit フック

```bash
# インストール
pip install pre-commit

# 設定ファイル作成
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
EOF

# フック有効化
pre-commit install

# 手動実行
pre-commit run --all-files
```

### Makefile

```makefile
# Makefile
.PHONY: format lint test

format:
	black python/
	isort python/

lint:
	flake8 python/ --max-line-length=100
	mypy python/

test:
	pytest tests/ -v --cov=python --cov-report=html

all: format lint test
```

使用例:
```bash
make format
make lint
make test
make all
```

---

**最終更新**: 2025-01-23  
**次回更新予定**: Phase 2開始時