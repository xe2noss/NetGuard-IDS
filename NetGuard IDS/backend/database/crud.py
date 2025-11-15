from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from . import models

def create_alert(db: Session, alert_data: dict):
    """
    Create a new alert entry in the database.
    """
    alert = models.Alert(**alert_data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_alerts(db: Session, skip: int = 0, limit: int = 50):
    """
    Retrieve the most recent alerts.
    """
    return db.query(models.Alert).order_by(desc(models.Alert.timestamp)).offset(skip).limit(limit).all()

def get_alert_by_id(db: Session, alert_id: int):
    """
    Get a single alert by its ID.
    """
    return db.query(models.Alert).filter(models.Alert.id == alert_id).first()

def acknowledge_alert(db: Session, alert_id: int):
    """
    Mark an alert as acknowledged.
    """
    alert = get_alert_by_id(db, alert_id)
    if alert:
        alert.acknowledged = True
        db.commit()
        db.refresh(alert)
    return alert

def get_statistics(db: Session, hours: int = 24):
    """
    Get summary statistics for the dashboard.
    """
    since = datetime.now() - timedelta(hours=hours)
    
    total_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.timestamp >= since
    ).scalar()
    
    top_attackers = db.query(
        models.Alert.source_ip,
        func.count(models.Alert.id).label('count')
    ).filter(
        models.Alert.timestamp >= since
    ).group_by(models.Alert.source_ip).order_by(desc('count')).limit(5).all()
    
    alerts_by_type = db.query(
        models.Alert.threat_type,
        func.count(models.Alert.id).label('count')
    ).filter(
        models.Alert.timestamp >= since
    ).group_by(models.Alert.threat_type).all()
    
    return {
        "total_alerts": total_alerts,
        "top_attackers": [{"ip": ip, "count": count} for ip, count in top_attackers],
        "alerts_by_type": [{"type": t, "count": count} for t, count in alerts_by_type]
    }