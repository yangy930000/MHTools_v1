from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime
from .models import GameSession

class SessionService:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory
        self._current_session_id = None

    async def start_session(self, game_name: str) -> GameSession:
        async with self.session_factory() as session:
            new_session = GameSession(game_name=game_name, start_time=datetime.now())
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            self._current_session_id = new_session.id
            return new_session

    async def stop_session(self) -> GameSession | None:
        if not self._current_session_id:
            return None
        
        async with self.session_factory() as session:
            # 获取当前会话
            stmt = select(GameSession).where(GameSession.id == self._current_session_id)
            result = await session.execute(stmt)
            current_session = result.scalar_one_or_none()
            
            if current_session and current_session.end_time is None:
                end_time = datetime.now()
                # 计算并存储持续时间（秒）
                # 注意：sqlite 存储 datetime 可能丢失时区信息，这里简化处理，假定都是本地时间
                start_time = current_session.start_time
                # 如果 start_time 是 naive 的 (没有时区)，假定它是本地时间
                if start_time.tzinfo is None:
                    start_time = start_time.astimezone()

                duration = (end_time.astimezone() - start_time).total_seconds()

                current_session.end_time = end_time
                current_session.duration_seconds = int(duration)
                await session.commit()
                await session.refresh(current_session)
                self._current_session_id = None
                return current_session
        return None

    async def get_recent_history(self, limit=20):
        """异步获取最近的记录"""
        async with self.session_factory() as session:
            # 查询已结束的会话，按结束时间倒序
            stmt = select(GameSession).where(GameSession.end_time.is_not(None))\
                .order_by(desc(GameSession.end_time)).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    def is_tracking(self):
        return self._current_session_id is not None