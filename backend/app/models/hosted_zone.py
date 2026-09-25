from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class HostedZone(Base):
    __tablename__ = "hosted_zones"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    zone_id = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    zone_type = Column(String(20), nullable=False, default="Public")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    records = relationship("DNSRecord", back_populates="hosted_zone", cascade="all, delete-orphan")
