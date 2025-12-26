import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# 定义 ORM 基类
class Base(DeclarativeBase):
    pass

class DatabaseManager:
    def __init__(self, db_path="data/nextool.db"):
        # 确保 data 目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # 使用 aiosqlite 作为异步驱动
        db_url = f"sqlite+aiosqlite:///{db_path}"
        self.engine = create_async_engine(db_url, echo=False)
        # 创建异步会话工厂
        self.async_session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def initialize_tables(self):
        """异步创建所有定义的数据表"""
        async with self.engine.begin() as conn:
            # Base.metadata.create_all 会扫描所有继承了 Base 的模型并创建表
            await conn.run_sync(Base.metadata.create_all)
            print("数据库表结构已同步。")

    async def close(self):
        await self.engine.dispose()