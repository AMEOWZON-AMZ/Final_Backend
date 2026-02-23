from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Friend(Base):
    __tablename__ = "friends"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    friend_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])