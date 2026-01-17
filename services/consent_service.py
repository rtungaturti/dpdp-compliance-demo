from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database import Consent, User, AuditLog, ConsentPurpose, ConsentStatus, AuditCategory, Severity
import uuid


class ConsentService:
    """Service for managing user consents"""
    
    @staticmethod
    def grant_consent(
        db: Session,
        user_id: str,
        purpose: ConsentPurpose,
        version: str = "1.0",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Consent:
        """Grant consent for a specific purpose"""
        # Check if consent already exists and is granted
        existing = db.query(Consent).filter(
            Consent.user_id == user_id,
            Consent.purpose == purpose,
            Consent.status == ConsentStatus.GRANTED
        ).first()
        
        if existing:
            raise ValueError(f"Consent already granted for {purpose.value}")
        
        # Create new consent
        consent = Consent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            purpose=purpose,
            status=ConsentStatus.GRANTED,
            version=version,
            granted_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(consent)
        db.commit()
        db.refresh(consent)
        
        # Log the action
        audit_log = AuditLog(
            user_id=user_id,
            action="consent_granted",
            category=AuditCategory.CONSENT,
            severity=Severity.INFO,
            resource_type="consent",
            resource_id=consent.id,
            details={"purpose": purpose.value, "version": version},
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return consent
    
    @staticmethod
    def withdraw_consent(
        db: Session,
        user_id: str,
        purpose: ConsentPurpose,
        ip_address: Optional[str] = None
    ) -> Consent:
        """Withdraw consent for a specific purpose"""
        # Essential consent cannot be withdrawn
        if purpose == ConsentPurpose.ESSENTIAL:
            raise ValueError("Essential consent cannot be withdrawn as it is required for service operation")
        
        # Find active consent
        consent = db.query(Consent).filter(
            Consent.user_id == user_id,
            Consent.purpose == purpose,
            Consent.status == ConsentStatus.GRANTED
        ).first()
        
        if not consent:
            raise ValueError(f"No active consent found for {purpose.value}")
        
        # Update consent
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.utcnow()
        
        db.commit()
        db.refresh(consent)
        
        # Log the action
        audit_log = AuditLog(
            user_id=user_id,
            action="consent_withdrawn",
            category=AuditCategory.CONSENT,
            severity=Severity.WARNING,
            resource_type="consent",
            resource_id=consent.id,
            details={"purpose": purpose.value},
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return consent
    
    @staticmethod
    def get_user_consents(db: Session, user_id: str) -> List[Consent]:
        """Get all consents for a user"""
        consents = db.query(Consent).filter(
            Consent.user_id == user_id
        ).order_by(Consent.created_at.desc()).all()
        
        return consents
    
    @staticmethod
    def check_consent_status(
        db: Session,
        user_id: str,
        purpose: ConsentPurpose
    ) -> bool:
        """Check if user has granted consent for a purpose"""
        consent = db.query(Consent).filter(
            Consent.user_id == user_id,
            Consent.purpose == purpose,
            Consent.status == ConsentStatus.GRANTED
        ).first()
        
        return consent is not None
    
    @staticmethod
    def get_consent_by_purpose(
        db: Session,
        user_id: str,
        purpose: ConsentPurpose
    ) -> Optional[Consent]:
        """Get specific consent by purpose"""
        consent = db.query(Consent).filter(
            Consent.user_id == user_id,
            Consent.purpose == purpose,
            Consent.status == ConsentStatus.GRANTED
        ).first()
        
        return consent
    
    @staticmethod
    def initialize_essential_consent(
        db: Session,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> Consent:
        """Initialize essential consent for new users"""
        return ConsentService.grant_consent(
            db=db,
            user_id=user_id,
            purpose=ConsentPurpose.ESSENTIAL,
            version="1.0",
            ip_address=ip_address
        )