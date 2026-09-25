from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class DNSRecord(Base):
    __tablename__ = "dns_records"
    id = Column(Integer, primary_key=True)
    hosted_zone_id = Column(Integer, ForeignKey("hosted_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(10), nullable=False, index=True)
    ttl = Column(Integer, nullable=False, default=300)
    value = Column(Text, nullable=False)
    routing_policy = Column(String(40), default="Simple")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    hosted_zone = relationship("HostedZone", back_populates="records")
