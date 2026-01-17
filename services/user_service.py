from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict
from database import User, AuditLog, Consent, AuditCategory, Severity
import json


class UserService:
    """Service for managing user data (DPDP Rights)"""
    
    @staticmethod
    def get_user_profile(db: Session, user_id: str, ip_address: Optional[str] = None) -> User:
        """Get user profile (Right to Access)"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Log data access
        audit_log = AuditLog(
            user_id=user_id,
            action="data_access",
            category=AuditCategory.DATA_ACCESS,
            severity=Severity.INFO,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> User:
        """Update user profile (Right to Correction)"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Store old data for audit
        old_data = {
            "name": user.name,
            "phone": user.phone,
            "address": user.address
        }
        
        # Update fields
        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone
        if address is not None:
            user.address = address
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Log data modification
        new_data = {
            "name": user.name,
            "phone": user.phone,
            "address": user.address
        }
        
        audit_log = AuditLog(
            user_id=user_id,
            action="data_updated",
            category=AuditCategory.DATA_MODIFICATION,
            severity=Severity.INFO,
            resource_type="user",
            resource_id=user_id,
            details={"old_data": old_data, "new_data": new_data},
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def export_user_data(
        db: Session,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> Dict:
        """Export user data (Right to Data Portability)"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Get all related data
        consents = db.query(Consent).filter(Consent.user_id == user_id).all()
        audit_logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(100).all()
        
        # Create export data
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "personal_data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "address": user.address,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            },
            "consents": [
                {
                    "purpose": c.purpose.value,
                    "status": c.status.value,
                    "granted_at": c.granted_at.isoformat(),
                    "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None
                }
                for c in consents
            ],
            "recent_activity": [
                {
                    "action": log.action,
                    "category": log.category.value,
                    "timestamp": log.created_at.isoformat()
                }
                for log in audit_logs
            ]
        }
        
        # Log data export
        audit_log = AuditLog(
            user_id=user_id,
            action="data_export",
            category=AuditCategory.DATA_ACCESS,
            severity=Severity.INFO,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return export_data
    
    @staticmethod
    def request_deletion(
        db: Session,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> User:
        """Request account deletion (Right to Erasure)"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Schedule deletion for 30 days later (DPDP guideline)
        scheduled_date = datetime.utcnow() + timedelta(days=30)
        
        user.deletion_requested_at = datetime.utcnow()
        user.scheduled_deletion_at = scheduled_date
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        # Log deletion request
        audit_log = AuditLog(
            user_id=user_id,
            action="deletion_requested",
            category=AuditCategory.DATA_DELETION,
            severity=Severity.WARNING,
            resource_type="user",
            resource_id=user_id,
            details={"scheduled_deletion_at": scheduled_date.isoformat()},
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def cancel_deletion(
        db: Session,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> User:
        """Cancel account deletion request"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        if not user.deletion_requested_at:
            raise ValueError("No deletion request found")
        
        user.deletion_requested_at = None
        user.scheduled_deletion_at = None
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        # Log cancellation
        audit_log = AuditLog(
            user_id=user_id,
            action="deletion_cancelled",
            category=AuditCategory.DATA_DELETION,
            severity=Severity.INFO,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def delete_user_permanently(db: Session, user_id: str):
        """Permanently delete user (execute scheduled deletion)"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Final audit log before deletion
        audit_log = AuditLog(
            user_id=user_id,
            action="user_deleted_permanently",
            category=AuditCategory.DATA_DELETION,
            severity=Severity.CRITICAL,
            resource_type="user",
            resource_id=user_id,
            details={"deleted_at": datetime.utcnow().isoformat()}
        )
        db.add(audit_log)
        db.commit()
        
        # Delete user (cascade will handle related records)
        db.delete(user)
        db.commit()