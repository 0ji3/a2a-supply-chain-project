"""
設定管理

環境変数から設定を読み込む。
"""
import os
from typing import Optional
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class Settings:
    """アプリケーション設定"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/a2a_supply_chain"
    )

    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Redis (Phase 2)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Blockchain (Phase 2)
    ANVIL_RPC_URL: Optional[str] = os.getenv("ANVIL_RPC_URL")
    PRIVATE_KEY: Optional[str] = os.getenv("PRIVATE_KEY")


settings = Settings()
