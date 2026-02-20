"""
Database models for IndoCloth Market.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database.connection import Base


class EventLog(Base):
    """Event logging table."""
    __tablename__ = "event_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    event_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RecommendationLog(Base):
    """Recommendation logging table."""
    __tablename__ = "recommendation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    product_id = Column(String(100), index=True)
    recommendation_score = Column(Float, nullable=False)
    model_version = Column(String(50))
    clicked = Column(Boolean, default=False)
    purchased = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class DriftEvent(Base):
    """Drift detection events."""
    __tablename__ = "drift_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drift_type = Column(String(50), nullable=False)  # data_drift, concept_drift
    drift_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    affected_features = Column(JSON)
    model_version = Column(String(50))
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    notified = Column(Boolean, default=False)


class RevenueMetric(Base):
    """Revenue metrics table."""
    __tablename__ = "revenue_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False, index=True)
    total_revenue = Column(Float, nullable=False)
    ai_driven_revenue = Column(Float, nullable=False)
    ai_revenue_share = Column(Float, nullable=False)  # percentage
    avg_cart_uplift = Column(Float)
    conversion_rate = Column(Float)
    top_recommended_item_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessInsight(Base):
    """Business insights and learnings."""
    __tablename__ = "business_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    insight_type = Column(String(50), nullable=False)  # daily, weekly, pattern, trend
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
