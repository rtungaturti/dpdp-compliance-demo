from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database import Grievance, User, AuditLog, GrievanceStatus, GrievanceCategory, AuditCategory, Severity
import uuid


class GrievanceService:
    """Service for handling grievance redressal"""
    
    @staticmethod
    def submit_grievance(
        db: Session,
        user_id: str,
        subject: str,
        description: str,
        category: GrievanceCategory = GrievanceCategory.OTHER,
        ip_address: Optional[str] = None
    ) -> Grievance:
        """Submit a new grievance"""
        if len(subject) < 5 or len(subject) > 200:
            raise ValueError("Subject must be between 5 and 200 characters")
        
        if len(description) < 10 or len(description) > 5000:
            raise ValueError("Description must be between 10 and 5000 characters")
        
        # Create grievance
        grievance = Grievance(
            id=str(uuid.uuid4()),
            user_id=user_id,
            subject=subject,
            description=description,
            category=category,
            status=GrievanceStatus.PENDING,
            priority="medium"
        )
        
        db.add(grievance)
        db.commit()
        db.refresh(grievance)
        
        # Log submission
        audit_log = AuditLog(
            user_id=user_id,
            action="grievance_submitted",
            category=AuditCategory.GRIEVANCE,
            severity=Severity.INFO,
            resource_type="grievance",
            resource_id=grievance.id,
            details={
                "ticket_number": grievance.ticket_number,
                "subject": subject,
                "category": category.value
            },
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return grievance
    
    @staticmethod
    def get_user_grievances(db: Session, user_id: str) -> List[Grievance]:
        """Get all grievances for a user"""
        grievances = db.query(Grievance).filter(
            Grievance.user_id == user_id
        ).order_by(Grievance.created_at.desc()).all()
        
        return grievances
    
    @staticmethod
    def get_grievance_by_id(
        db: Session,
        grievance_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Grievance]:
        """Get specific grievance by ID"""
        query = db.query(Grievance).filter(Grievance.id == grievance_id)
        
        if user_id:
            query = query.filter(Grievance.user_id == user_id)
        
        return query.first()
    
    @staticmethod
    def escalate_grievance(
        db: Session,
        grievance_id: str,
        user_id: str,
        reason: str,
        ip_address: Optional[str] = None
    ) -> Grievance:
        """Escalate grievance to Data Protection Board"""
        grievance = db.query(Grievance).filter(
            Grievance.id == grievance_id,
            Grievance.user_id == user_id
        ).first()
        
        if not grievance:
            raise ValueError("Grievance not found")
        
        if grievance.status == GrievanceStatus.ESCALATED:
            raise ValueError("Grievance already escalated")
        
        # Check if SLA deadline has passed or status allows escalation
        now = datetime.utcnow()
        can_escalate = (
            now >= grievance.sla_deadline or
            grievance.status == GrievanceStatus.RESOLVED
        )
        
        if not can_escalate:
            raise ValueError(
                "Grievance can only be escalated after SLA deadline or "
                "if resolution is unsatisfactory"
            )
        
        # Update grievance
        grievance.status = GrievanceStatus.ESCALATED
        grievance.escalated_at = datetime.utcnow()
        grievance.escalation_reason = reason
        grievance.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(grievance)
        
        # Log escalation
        audit_log = AuditLog(
            user_id=user_id,
            action="grievance_escalated",
            category=AuditCategory.GRIEVANCE,
            severity=Severity.WARNING,
            resource_type="grievance",
            resource_id=grievance.id,
            details={
                "ticket_number": grievance.ticket_number,
                "reason": reason
            },
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return grievance
    
    @staticmethod
    def update_grievance_status(
        db: Session,
        grievance_id: str,
        status: GrievanceStatus,
        resolution: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Grievance:
        """Update grievance status (Admin/DPO only)"""
        grievance = db.query(Grievance).filter(
            Grievance.id == grievance_id
        ).first()
        
        if not grievance:
            raise ValueError("Grievance not found")
        
        # Update fields
        if status:
            grievance.status = status
        
        if resolution:
            grievance.resolution = resolution
            grievance.resolved_at = datetime.utcnow()
        
        if priority:
            grievance.priority = priority
        
        if assigned_to:
            grievance.assigned_to = assigned_to
        
        grievance.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(grievance)
        
        return grievance
    
    @staticmethod
    def get_all_grievances(
        db: Session,
        status: Optional[GrievanceStatus] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Grievance], int]:
        """Get all grievances with filters (Admin/DPO only)"""
        query = db.query(Grievance)
        
        if status:
            query = query.filter(Grievance.status == status)
        
        if priority:
            query = query.filter(Grievance.priority == priority)
        
        total = query.count()
        grievances = query.order_by(
            Grievance.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return grievances, total
    
    @staticmethod
    def get_pending_grievances_count(db: Session) -> int:
        """Get count of pending grievances"""
        return db.query(Grievance).filter(
            Grievance.status == GrievanceStatus.PENDING
        ).count()
    
    @staticmethod
    def get_overdue_grievances(db: Session) -> List[Grievance]:
        """Get grievances past SLA deadline"""
        now = datetime.utcnow()
        return db.query(Grievance).filter(
            Grievance.sla_deadline < now,
            Grievance.status.in_([GrievanceStatus.PENDING, GrievanceStatus.IN_PROGRESS])
        ).all()