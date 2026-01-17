from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Float, Text, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import uuid
import enum
from config import get_database_url

# Database setup
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class UserRole(str, enum.Enum):
    PRINCIPAL = "principal"
    DPO = "dpo"
    ADMIN = "admin"


class ConsentPurpose(str, enum.Enum):
    ESSENTIAL = "essential"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    DATA_PROCESSING = "data_processing"


class ConsentStatus(str, enum.Enum):
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"


class GrievanceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class GrievanceCategory(str, enum.Enum):
    DATA_ACCESS = "data_access"
    DATA_CORRECTION = "data_correction"
    DATA_DELETION = "data_deletion"
    CONSENT_WITHDRAWAL = "consent_withdrawal"
    DATA_BREACH = "data_breach"
    OTHER = "other"


class AuditCategory(str, enum.Enum):
    AUTHENTICATION = "authentication"
    CONSENT = "consent"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    GRIEVANCE = "grievance"
    ADMIN_ACTION = "admin_action"
    SECURITY_EVENT = "security_event"
    BREACH_DETECTION = "breach_detection"


class Severity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PRINCIPAL, nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    deletion_requested_at = Column(DateTime, nullable=True)
    scheduled_deletion_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    grievances = relationship("Grievance", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Consent(Base):
    __tablename__ = "consents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    purpose = Column(Enum(ConsentPurpose), nullable=False)
    status = Column(Enum(ConsentStatus), default=ConsentStatus.GRANTED, nullable=False)
    version = Column(String(10), default="1.0")
    granted_at = Column(DateTime, default=datetime.utcnow)
    withdrawn_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="consents")


class Grievance(Base):
    __tablename__ = "grievances"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(GrievanceCategory), default=GrievanceCategory.OTHER)
    status = Column(Enum(GrievanceStatus), default=GrievanceStatus.PENDING, nullable=False)
    priority = Column(String(20), default="medium")
    assigned_to = Column(String(36), nullable=True)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    sla_deadline = Column(DateTime, nullable=False)
    escalated_at = Column(DateTime, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="grievances")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_number:
            date_str = datetime.utcnow().strftime("%Y%m%d")
            random_num = str(uuid.uuid4().int)[:4]
            self.ticket_number = f"GRV-{date_str}-{random_num}"
        if not self.sla_deadline:
            self.sla_deadline = datetime.utcnow() + timedelta(days=7)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    category = Column(Enum(AuditCategory), nullable=False)
    severity = Column(Enum(Severity), default=Severity.INFO)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    siem_sent = Column(Boolean, default=False)
    siem_sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class DataRetention(Base):
    __tablename__ = "data_retention_policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_type = Column(String(100), unique=True, nullable=False)
    retention_period_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    legal_basis = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()