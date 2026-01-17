# DPDP Compliance Demo - Python Edition

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![NiceGUI](https://img.shields.io/badge/NiceGUI-1.4+-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue)
![DPDP](https://img.shields.io/badge/DPDP-Act%202023-orange)

A comprehensive Python implementation of India's **Digital Personal Data Protection (DPDP) Act, 2023** compliance platform using NiceGUI, SQLAlchemy, and PostgreSQL.

## 🎯 Why Python/NiceGUI?

### Advantages
- ✅ **Pure Python** - No JavaScript needed
- ✅ **Rapid Development** - Build UIs with Python syntax
- ✅ **Type Safety** - Pydantic validation throughout
- ✅ **Easy Deployment** - Single application, no build step
- ✅ **Real-time Updates** - WebSocket-based reactivity
- ✅ **Better for Data Science** - Python ecosystem integration

### Technology Stack

```
┌─────────────────────────────────────┐
│         NiceGUI (FastAPI)           │  ← Web Framework
├─────────────────────────────────────┤
│    SQLAlchemy ORM + PostgreSQL      │  ← Database Layer
├─────────────────────────────────────┤
│  Services (Auth, Consent, User...)  │  ← Business Logic
├─────────────────────────────────────┤
│   Email + SIEM Integration          │  ← External Services
└─────────────────────────────────────┘
```

## 🌟 Features

### DPDP Act 2023 Compliance

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Consent Management | Granular, versioned consents | ✅ |
| Privacy Notice | Comprehensive privacy page | ✅ |
| Right to Access | View personal data | ✅ |
| Right to Correction | Edit profile data | ✅ |
| Right to Portability | Download JSON export | ✅ |
| Right to Erasure | 30-day deletion window | ✅ |
| Grievance Redressal | 7-day SLA tracking | ✅ |
| Data Retention | Policy-based retention | ✅ |
| Audit Logging | Complete activity trail | ✅ |
| Breach Notification | Automated alerts | ✅ |

### Technical Features

- 🔐 **Security**: JWT auth, bcrypt hashing, SQL injection prevention
- 📧 **Email**: Automated notifications via SMTP
- 📊 **Analytics**: SIEM integration for monitoring
- 🎨 **UI**: Modern, responsive NiceGUI interface
- 📝 **Logging**: Structured logging with Loguru
- ✅ **Validation**: Pydantic schemas for data integrity
- 🗄️ **Database**: PostgreSQL with SQLAlchemy ORM

## 📦 Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/dpdp-python.git
cd dpdp-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python -c "from database import init_db; init_db()"

# Run application
python main.py
```

Visit `http://localhost:8080`

## 🏗️ Architecture

### Directory Structure

```
dpdp-compliance-python/
│
├── main.py                     # Application entry point
├── config.py                   # Configuration management
├── database.py                 # Models and DB setup
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
│
├── services/                   # Business logic layer
│   ├── auth_service.py         # Authentication & authorization
│   ├── consent_service.py      # Consent management
│   ├── user_service.py         # User data (DPDP rights)
│   ├── grievance_service.py    # Grievance handling
│   ├── email_service.py        # Email notifications
│   └── siem_service.py         # SIEM integration
│
├── pages/                      # UI pages
│   └── dashboard.py            # User dashboard
│
├── logs/                       # Application logs
│   ├── app.log                 # General logs
│   └── error.log               # Error logs
│
└── tests/                      # Test suite
    ├── test_auth.py
    ├── test_consent.py
    └── test_user.py
```

### Database Models

#### User Model
```python
class User(Base):
    id: UUID
    name: str
    email: str (unique)
    phone: str (optional)
    address: str (optional)
    password_hash: str
    role: Enum(principal, dpo, admin)
    is_active: bool
    deletion_requested_at: datetime
    scheduled_deletion_at: datetime
```

#### Consent Model
```python
class Consent(Base):
    id: UUID
    user_id: UUID (FK)
    purpose: Enum(essential, analytics, marketing)
    status: Enum(granted, withdrawn)
    version: str
    granted_at: datetime
    withdrawn_at: datetime
```

#### Grievance Model
```python
class Grievance(Base):
    id: UUID
    user_id: UUID (FK)
    ticket_number: str (unique)
    subject: str
    description: str
    status: Enum(pending, in_progress, resolved, escalated)
    sla_deadline: datetime
    resolution: str
```

#### AuditLog Model
```python
class AuditLog(Base):
    id: UUID
    user_id: UUID (FK)
    action: str
    category: Enum(auth, consent, data_access, ...)
    severity: Enum(info, warning, error, critical)
    details: JSON
    ip_address: str
    is_anomaly: bool
```

## 🔌 Services API

### AuthService

```python
# Register user
user = AuthService.register_user(
    db, name, email, password, phone, address
)

# Authenticate
user = AuthService.authenticate_user(
    db, email, password, ip_address
)

# Create token
token = AuthService.create_access_token(
    user_id, email, role
)

# Verify token
payload = AuthService.verify_token(token)
```

### ConsentService

```python
# Grant consent
consent = ConsentService.grant_consent(
    db, user_id, ConsentPurpose.ANALYTICS
)

# Withdraw consent
consent = ConsentService.withdraw_consent(
    db, user_id, ConsentPurpose.MARKETING
)

# Check status
is_granted = ConsentService.check_consent_status(
    db, user_id, ConsentPurpose.ANALYTICS
)
```

### UserService (DPDP Rights)

```python
# Right to Access
user = UserService.get_user_profile(db, user_id)

# Right to Correction
user = UserService.update_user_profile(
    db, user_id, name="New Name", phone="123"
)

# Right to Portability
data = UserService.export_user_data(db, user_id)

# Right to Erasure
user = UserService.request_deletion(db, user_id)
```

### GrievanceService

```python
# Submit grievance
grievance = GrievanceService.submit_grievance(
    db, user_id, subject, description, category
)

# Escalate to DPB
grievance = GrievanceService.escalate_grievance(
    db, grievance_id, user_id, reason
)

# Update status (Admin/DPO)
grievance = GrievanceService.update_grievance_status(
    db, grievance_id, status, resolution
)
```

## 🎨 NiceGUI UI Examples

### Creating a Page

```python
@ui.page('/dashboard')
def dashboard():
    with ui.header():
        ui.label('Dashboard').classes('text-2xl')
    
    with ui.card():
        ui.label('My Data')
        ui.button('Download', on_click=download_data)
```

### Dynamic Updates

```python
# Reactive checkbox
consent_check = ui.checkbox('Analytics')

def toggle_consent():
    if consent_check.value:
        grant_consent('analytics')
    else:
        withdraw_consent('analytics')

consent_check.on('update:model-value', toggle_consent)
```

### Dialogs

```python
with ui.dialog() as dialog, ui.card():
    ui.label('Confirm Action')
    ui.button('OK', on_click=dialog.close)

dialog.open()
```

## 📧 Email Notifications

### Send Welcome Email

```python
await EmailService.send_welcome_email(
    user_email="user@example.com",
    user_name="John Doe"
)
```

### Send Grievance Confirmation

```python
await EmailService.send_grievance_confirmation(
    user_email="user@example.com",
    user_name="John Doe",
    ticket_number="GRV-20260117-1234",
    subject="Data Access Request"
)
```

### Send Breach Notification

```python
await EmailService.send_breach_notification(
    user_email="user@example.com",
    user_name="John Doe",
    breach_details="Unauthorized access detected..."
)
```

## 📊 SIEM Integration

### Log Security Events

```python
# Authentication failure
await SIEMService.log_authentication_failure(
    user_id, email, ip_address, reason
)

# Data access
await SIEMService.log_data_access(
    user_id, "user", user_id, ip_address
)

# Anomaly detection
await SIEMService.log_anomaly_detected(
    user_id, "unusual_access", 0.8, details
)

# Breach detection
await SIEMService.log_breach_detected(
    "unauthorized_access", 100, details
)
```

### Anomaly Detection

```python
result = SIEMService.detect_anomaly(
    user_id, action="data_export", ip_address
)

# Returns:
{
    "unusual_access_time": False,
    "suspicious_ip_change": False,
    "anomaly_score": 0.3
}
```

## 🧪 Testing

### Unit Tests

```python
# test_auth.py
def test_register_user():
    db = next(get_db())
    user = AuthService.register_user(
        db, "Test", "test@test.com", "Pass123"
    )
    assert user.email == "test@test.com"

def test_password_validation():
    assert AuthService.validate_password_strength("Weak") == False
    assert AuthService.validate_password_strength("Strong123") == True
```

### Integration Tests

```python
# test_workflow.py
async def test_full_user_journey():
    # Register
    user = register_user(...)
    
    # Grant consent
    consent = grant_consent(user.id, "analytics")
    
    # Submit grievance
    grievance = submit_grievance(user.id, ...)
    
    # Export data
    data = export_data(user.id)
    
    assert data["consents"][0]["purpose"] == "analytics"
```

### Run Tests

```bash
pytest
pytest -v  # Verbose
pytest --cov  # With coverage
```

## 📈 Performance

### Database Optimization

```python
# Indexed fields for fast queries
- user.email (unique index)
- consent.user_id + purpose
- grievance.ticket_number
- audit_log.created_at
```

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

## 🔒 Security Best Practices

1. **Password Security**
   - bcrypt hashing with 12 rounds
   - Minimum 8 characters with complexity rules

2. **Authentication**
   - JWT with expiration
   - Secure token storage
   - Session management

3. **Database**
   - Parameterized queries (SQLAlchemy)
   - No raw SQL execution
   - Input validation

4. **API**
   - Rate limiting (planned)
   - CORS configuration
   - HTTPS enforcement

## 📊 Monitoring & Logs

### View Logs

```bash
tail -f logs/app.log
tail -f logs/error.log
```

### Log Levels

```python
from loguru import logger

logger.info("User logged in")
logger.warning("Failed login attempt")
logger.error("Database connection failed")
logger.critical("Data breach detected")
```

### Configure Logging

```python
# config.py
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 🚀 Deployment

See [DEPLOYMENT_PYTHON.md](./DEPLOYMENT_PYTHON.md) for complete guide.

### Quick Deploy to Render

1. Push code to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service on Render
4. Set environment variables
5. Deploy!

Your app will be live at: `https://your-app.onrender.com`

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- NiceGUI framework
- SQLAlchemy ORM
- DPDP Act 2023 legislation
- Python community

## 📞 Support

- **Issues**: [GitHub Issues]
- **Email**: dpo@dpdpdemo.com
- **Docs**: See project wiki

---

**Built with ❤️ and Python for DPDP Act 2023 Compliance**

*Last Updated: January 2026*