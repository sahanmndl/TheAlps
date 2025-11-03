from time import time
from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Float, func, text
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class RiskTolerance(enum.Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class InvestmentHorizon(enum.Enum):
    SHORT_TERM = "short_term"  # < 1 year
    MEDIUM_TERM = "medium_term"  # 1-5 years
    LONG_TERM = "long_term"  # > 5 years

class TargetAnnualReturn(enum.Enum):
    LOW = {"start": 0, "end": 10, "label": f"0% - 10%"}
    MEDIUM = {"start": 10, "end": 20, "label": f"10% - 20%"}
    HIGH = {"start": 20, "end": 100, "label": f"20% - 100%"}

class Sectors(enum.Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIAL_SERVICES = "Financial Services"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    MATERIALS = "Materials"
    REAL_ESTATE = "Real Estate"
    UTILITIES = "Utilities"
    TELECOMMUNICATIONS = "Telecommunications"
    AUTOMOTIVE = "Automotive"
    AEROSPACE_DEFENSE = "Aerospace & Defense"
    BIOTECHNOLOGY = "Biotechnology"
    RENEWABLE_ENERGY = "Renewable Energy"
    E_COMMERCE = "E-Commerce"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    CRYPTOCURRENCY = "Cryptocurrency"
    CLOUD_COMPUTING = "Cloud Computing"
    CYBERSECURITY = "Cybersecurity"

class MonthlyInvestmentRange(enum.Enum):
    TIER_1 = {"start": 1000, "end": 5000, "label": "₹1,000 - ₹5,000"}
    TIER_2 = {"start": 5000, "end": 10000, "label": "₹5,000 - ₹10,000"}
    TIER_3 = {"start": 10000, "end": 25000, "label": "₹10,000 - ₹25,000"}
    TIER_4 = {"start": 25000, "end": 50000, "label": "₹25,000 - ₹50,000"}
    TIER_5 = {"start": 50000, "end": 100000, "label": "₹50,000 - ₹1,00,000"}
    TIER_6 = {"start": 100000, "end": float('inf'), "label": "Above ₹1,00,000"}

class InvestmentPreference(Base):
    __tablename__ = "investment_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    risk_tolerance = Column(Enum(RiskTolerance), nullable=False)
    investment_horizon = Column(Enum(InvestmentHorizon), nullable=False)
    target_annual_return = Column(Enum(TargetAnnualReturn), nullable=False)
    monthly_investment_range = Column(Enum(MonthlyInvestmentRange), nullable=False)
    preferred_sectors = Column(ARRAY(Enum(Sectors)), server_default='{}')
    avoid_sectors = Column(ARRAY(Enum(Sectors)), server_default='{}')
    max_position_size = Column(Float, nullable=True)  # Maximum % in single stock
    dividend_focus = Column(Boolean, default=False)
    esg_focus = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="investment_preference")