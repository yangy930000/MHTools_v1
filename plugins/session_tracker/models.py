from sqlalchemy import Column, Integer, String, DateTime, func
from core.database import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_name = Column(String(100), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, default=0) # 存储持续秒数
    notes = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<GameSession(game='{self.game_name}', duration={self.duration_seconds})>"