from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database import User, AuditLog, AuditCategory, Severity
from config import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: str, email: str, role: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        to_encode = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def register_user(
        db: Session,
        name: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> User:
        """Register a new user"""
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone,
            address=address,
            password_hash=AuthService.hash_password(password)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log registration
        audit_log = AuditLog(
            user_id=user.id,
            action="user_registered",
            category=AuditCategory.AUTHENTICATION,
            severity=Severity.INFO,
            resource_type="user",
            resource_id=user.id,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[User]:
        """Authenticate user and return user object"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        if not AuthService.verify_password(password, user.password_hash):
            # Log failed login attempt
            audit_log = AuditLog(
                user_id=user.id,
                action="failed_login_attempt",
                category=AuditCategory.SECURITY_EVENT,
                severity=Severity.WARNING,
                ip_address=ip_address
            )
            db.add(audit_log)
            db.commit()
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # Log successful login
        audit_log = AuditLog(
            user_id=user.id,
            action="user_login",
            category=AuditCategory.AUTHENTICATION,
            severity=Severity.INFO,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = AuthService.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user if user and user.is_active else None
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit