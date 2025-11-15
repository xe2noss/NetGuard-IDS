from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Alert(Base):
    """
    SQLAlchemy model for an alert.
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    source_ip = Column(String(45), nullable=False, index=True)
    dest_ip = Column(String(45), nullable=False)
    source_port = Column(Integer)
    dest_port = Column(Integer)
    protocol = Column(String(10))
    threat_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    description = Column(Text)
    raw_packet_summary = Column(Text)
    acknowledged = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "source_port": self.source_port,
            "dest_port": self.dest_port,
            "protocol": self.protocol,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "description": self.description,
            "raw_packet_summary": self.raw_packet_summary,
            "acknowledged": self.acknowledged
        }