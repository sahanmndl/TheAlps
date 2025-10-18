from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=True)    # NSE/BSE
    shares = Column(Integer, nullable=False)
    avg_cost = Column(Float, nullable=False)
    holding_since = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="holdings")
