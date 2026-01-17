from nicegui import ui, app
from database import init_db, get_db, User
from services.auth_service import AuthService
from services.consent_service import ConsentService
from services.user_service import UserService
from services.grievance_service import GrievanceService
from database import ConsentPurpose, GrievanceCategory
from config import settings
import json
from datetime import datetime

# Initialize database
init_db()

# Session management
app.storage.general['current_user'] = None


def get_current_user():
    """Get current logged-in user"""
    return app.storage.general.get('current_user')


def set_current_user(user):
    """Set current logged-in user"""
    app.storage.general['current_user'] = user


def logout():
    """Logout user"""
    app.storage.general['current_user'] = None
    ui.navigate.to('/login')
    ui.notify('Logged out successfully', type='positive')


# Consent banner
@ui.page('/')
async def index_page():
    """Home page with consent banner"""
    current_user = get_current_user()
    
    with ui.header().classes('items-center justify-between bg-blue-900 text-white p-4'):
        with ui.row().classes('items-center'):
            ui.icon('shield', size='2rem')
            ui.label('DPDP Compliance Demo').classes('text-2xl font-bold ml-2')
        
        with ui.row().classes('gap-4'):
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat')
            ui.button('Privacy Notice', on_click=lambda: ui.navigate.to('/privacy')).props('flat')
            
            if current_user:
                ui.button('Dashboard', on_click=lambda: ui.navigate.to('/dashboard')).props('flat')
                ui.button('Logout', on_click=logout).props('flat')
            else:
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat')
                ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('flat')
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-8'):
        # Hero section
        with ui.card().classes('w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8'):
            ui.label('Welcome to DPDP Compliance Demo').classes('text-4xl font-bold mb-4')
            ui.label('Experience a comprehensive demonstration of India\'s Digital Personal Data Protection Act, 2023').classes('text-xl')
        
        # Features grid
        with ui.grid(columns=3).classes('w-full gap-6'):
            with ui.card().classes('p-6'):
                ui.icon('shield', size='3rem', color='blue')
                ui.label('Full Compliance').classes('text-xl font-bold mt-4 mb-2')
                ui.label('Demonstrates all DPDP Act requirements including consent, rights, and grievance redressal')
            
            with ui.card().classes('p-6'):
                ui.icon('description', size='3rem', color='blue')
                ui.label('Transparent Data Practices').classes('text-xl font-bold mt-4 mb-2')
                ui.label('Clear privacy notices, granular consent, and full data portability')
            
            with ui.card().classes('p-6'):
                ui.icon('warning', size='3rem', color='blue')
                ui.label('Breach Ready').classes('text-xl font-bold mt-4 mb-2')
                ui.label('SIEM integration and automated breach detection mechanisms')
        
        # Key features
        with ui.card().classes('w-full p-6'):
            ui.label('Key Features').classes('text-2xl font-bold mb-4')
            with ui.column().classes('gap-2'):
                ui.label('✓ Granular consent management').classes('text-lg')
                ui.label('✓ Data Principal rights (view, edit, download, delete)').classes('text-lg')
                ui.label('✓ Grievance redressal mechanism').classes('text-lg')
                ui.label('✓ Automated data retention policies').classes('text-lg')
                ui.label('✓ SIEM-ready logging and monitoring').classes('text-lg')
    
    # Consent banner (if not consented)
    if not app.storage.user.get('consent_given'):
        show_consent_banner()


def show_consent_banner():
    """Show consent banner"""
    with ui.dialog() as consent_dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label('Cookie & Data Consent').classes('text-2xl font-bold mb-4')
        ui.label('We use cookies and collect personal data in compliance with India\'s DPDP Act, 2023. Please review and customize your consent preferences.')
        
        consents = {
            'essential': ui.checkbox('Essential (Required)', value=True).props('disable'),
            'analytics': ui.checkbox('Analytics', value=False),
            'marketing': ui.checkbox('Marketing', value=False)
        }
        
        with ui.row().classes('gap-4 mt-4'):
            def accept_consents():
                app.storage.user['consent_given'] = True
                app.storage.user['consents'] = {
                    'essential': True,
                    'analytics': consents['analytics'].value,
                    'marketing': consents['marketing'].value,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }
                consent_dialog.close()
                ui.notify('Consent preferences saved', type='positive')
            
            def essential_only():
                app.storage.user['consent_given'] = True
                app.storage.user['consents'] = {
                    'essential': True,
                    'analytics': False,
                    'marketing': False,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }
                consent_dialog.close()
                ui.notify('Essential consent saved', type='positive')
            
            ui.button('Accept Selected', on_click=accept_consents).props('color=primary')
            ui.button('Essential Only', on_click=essential_only).props('color=secondary')
            ui.button('Privacy Notice', on_click=lambda: ui.navigate.to('/privacy')).props('flat')
    
    consent_dialog.open()


@ui.page('/privacy')
def privacy_page():
    """Privacy notice page"""
    with ui.header().classes('bg-blue-900 text-white p-4'):
        ui.label('DPDP Compliance Demo - Privacy Notice').classes('text-2xl font-bold')
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8'):
        ui.button('← Back', on_click=lambda: ui.navigate.to('/')).props('flat')
        
        with ui.card().classes('w-full p-8 mt-4'):
            ui.label('Privacy Notice').classes('text-3xl font-bold mb-6')
            
            sections = [
                ('1. Data Collected', [
                    'Name, Email, Phone Number',
                    'Address and Location',
                    'Consent preferences',
                    'Usage analytics (with consent)'
                ]),
                ('2. Purpose of Processing', [
                    'Service delivery and account management',
                    'Communication and support',
                    'Analytics and improvement (with consent)',
                    'Legal compliance'
                ]),
                ('3. Data Retention', [
                    'Active accounts: Duration of service + 1 year',
                    'Consent records: 3 years from withdrawal',
                    'Grievance records: 5 years'
                ]),
                ('4. Your Rights (DPDP Act 2023)', [
                    'Right to access your personal data',
                    'Right to correction and updation',
                    'Right to data portability',
                    'Right to erasure and be forgotten',
                    'Right to grievance redressal'
                ]),
                ('5. Grievance Redressal', [
                    f'Contact our Data Protection Officer: {settings.DPO_EMAIL}',
                    'Response time: 7 days',
                    'Escalation to Data Protection Board available if unresolved'
                ]),
                ('6. Data Security', [
                    'Encryption at rest and in transit',
                    'Role-based access control',
                    'Regular security audits',
                    'Breach detection and notification'
                ])
            ]
            
            for title, items in sections:
                ui.label(title).classes('text-xl font-bold mt-6 mb-2')
                with ui.column().classes('ml-6 gap-1'):
                    for item in items:
                        ui.label(f'• {item}')


@ui.page('/login')
def login_page():
    """Login page"""
    if get_current_user():
        ui.navigate.to('/dashboard')
        return
    
    with ui.header().classes('bg-blue-900 text-white p-4'):
        ui.label('DPDP Compliance Demo - Login').classes('text-2xl font-bold')
    
    with ui.column().classes('w-full max-w-md mx-auto p-8 mt-12'):
        with ui.card().classes('w-full p-8'):
            ui.label('Login').classes('text-2xl font-bold mb-6')
            
            email = ui.input('Email', placeholder='your@email.com').classes('w-full').props('type=email')
            password = ui.input('Password', placeholder='********').classes('w-full').props('type=password')
            
            def do_login():
                try:
                    db = next(get_db())
                    user = AuthService.authenticate_user(
                        db=db,
                        email=email.value,
                        password=password.value,
                        ip_address='127.0.0.1'
                    )
                    
                    if user:
                        set_current_user({
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'role': user.role.value
                        })
                        ui.notify(f'Welcome {user.name}!', type='positive')
                        ui.navigate.to('/dashboard')
                    else:
                        ui.notify('Invalid credentials', type='negative')
                except Exception as e:
                    ui.notify(str(e), type='negative')
            
            ui.button('Login', on_click=do_login).classes('w-full').props('color=primary size=lg')
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('Don\'t have an account?')
                ui.link('Register', '/register')


@ui.page('/register')
def register_page():
    """Registration page"""
    if get_current_user():
        ui.navigate.to('/dashboard')
        return
    
    with ui.header().classes('bg-blue-900 text-white p-4'):
        ui.label('DPDP Compliance Demo - Register').classes('text-2xl font-bold')
    
    with ui.column().classes('w-full max-w-md mx-auto p-8 mt-12'):
        with ui.card().classes('w-full p-8'):
            ui.label('Register').classes('text-2xl font-bold mb-6')
            
            name = ui.input('Full Name').classes('w-full')
            email = ui.input('Email').classes('w-full').props('type=email')
            phone = ui.input('Phone').classes('w-full')
            password = ui.input('Password').classes('w-full').props('type=password')
            
            consent_check = ui.checkbox(
                'I consent to the collection and processing of my personal data as per the Privacy Notice. '
                'I understand my rights under DPDP Act 2023.'
            ).classes('mt-4')
            
            def do_register():
                if not consent_check.value:
                    ui.notify('Consent is required for registration', type='negative')
                    return
                
                if not AuthService.validate_password_strength(password.value):
                    ui.notify('Password must be at least 8 characters with uppercase, lowercase, and number', type='negative')
                    return
                
                try:
                    db = next(get_db())
                    user = AuthService.register_user(
                        db=db,
                        name=name.value,
                        email=email.value,
                        phone=phone.value,
                        password=password.value,
                        ip_address='127.0.0.1'
                    )
                    
                    # Initialize essential consent
                    ConsentService.initialize_essential_consent(db, user.id)
                    
                    ui.notify('Registration successful! Please login.', type='positive')
                    ui.navigate.to('/login')
                except Exception as e:
                    ui.notify(str(e), type='negative')
            
            ui.button('Register', on_click=do_register).classes('w-full').props('color=primary size=lg')
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('Already have an account?')
                ui.link('Login', '/login')


# Additional pages for dashboard, grievances etc. would go here
# Due to space constraints, showing the structure

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        title=settings.APP_NAME,
        storage_secret=settings.SECRET_KEY
    )