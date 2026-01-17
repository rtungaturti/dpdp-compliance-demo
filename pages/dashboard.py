from nicegui import ui
from database import get_db, ConsentPurpose, GrievanceCategory
from services.user_service import UserService
from services.consent_service import ConsentService
from services.grievance_service import GrievanceService
import json


def dashboard_page(current_user):
    """User dashboard with DPDP rights"""
    
    with ui.header().classes('bg-blue-900 text-white p-4'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('DPDP Compliance Demo - Dashboard').classes('text-2xl font-bold')
            ui.button('Logout', on_click=lambda: ui.navigate.to('/logout')).props('flat')
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-6'):
        ui.label(f'Welcome, {current_user["name"]}!').classes('text-3xl font-bold')
        
        # Get user data from database
        db = next(get_db())
        user = UserService.get_user_profile(db, current_user['id'])
        user_consents = ConsentService.get_user_consents(db, current_user['id'])
        user_grievances = GrievanceService.get_user_grievances(db, current_user['id'])
        
        with ui.row().classes('w-full gap-6'):
            # Personal Data Card
            with ui.card().classes('flex-1 p-6'):
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label('My Personal Data').classes('text-xl font-bold')
                    ui.icon('edit', size='sm', color='primary').classes('cursor-pointer').on('click', lambda: edit_profile_dialog(user))
                
                with ui.column().classes('gap-2'):
                    ui.label(f'Name: {user.name}').classes('text-base')
                    ui.label(f'Email: {user.email}').classes('text-base')
                    ui.label(f'Phone: {user.phone or "Not provided"}').classes('text-base')
                    ui.label(f'Address: {user.address or "Not provided"}').classes('text-base')
                
                with ui.row().classes('gap-3 mt-4'):
                    ui.button('Download Data', icon='download', on_click=lambda: download_data(current_user['id'])).props('color=green')
                    ui.button('Delete Account', icon='delete', on_click=lambda: delete_account_dialog(current_user['id'])).props('color=red')
            
            # Consent Management Card
            with ui.card().classes('flex-1 p-6'):
                ui.label('Consent Management').classes('text-xl font-bold mb-4')
                
                consent_dict = {c.purpose.value: c for c in user_consents if c.status.value == 'granted'}
                
                def toggle_consent(purpose):
                    try:
                        db = next(get_db())
                        if purpose in consent_dict:
                            if purpose != 'essential':
                                ConsentService.withdraw_consent(db, current_user['id'], ConsentPurpose(purpose))
                                ui.notify(f'{purpose.title()} consent withdrawn', type='warning')
                                ui.navigate.reload()
                        else:
                            ConsentService.grant_consent(db, current_user['id'], ConsentPurpose(purpose))
                            ui.notify(f'{purpose.title()} consent granted', type='positive')
                            ui.navigate.reload()
                    except Exception as e:
                        ui.notify(str(e), type='negative')
                
                with ui.column().classes('gap-3'):
                    ui.checkbox('Essential Cookies', value=True).props('disable')
                    
                    analytics_check = ui.checkbox('Analytics', value='analytics' in consent_dict)
                    analytics_check.on('update:model-value', lambda: toggle_consent('analytics'))
                    
                    marketing_check = ui.checkbox('Marketing', value='marketing' in consent_dict)
                    marketing_check.on('update:model-value', lambda: toggle_consent('marketing'))
        
        # Grievance Section
        with ui.card().classes('w-full p-6'):
            ui.label('Submit Grievance').classes('text-xl font-bold mb-4')
            
            subject = ui.input('Subject', placeholder='Brief description of your concern').classes('w-full')
            description = ui.textarea('Description', placeholder='Detailed explanation...').classes('w-full').props('rows=4')
            category = ui.select(
                options=[c.value for c in GrievanceCategory],
                label='Category',
                value=GrievanceCategory.OTHER.value
            ).classes('w-full')
            
            def submit_grievance():
                try:
                    db = next(get_db())
                    grievance = GrievanceService.submit_grievance(
                        db=db,
                        user_id=current_user['id'],
                        subject=subject.value,
                        description=description.value,
                        category=GrievanceCategory(category.value)
                    )
                    ui.notify(f'Grievance submitted: {grievance.ticket_number}', type='positive')
                    subject.value = ''
                    description.value = ''
                    ui.navigate.reload()
                except Exception as e:
                    ui.notify(str(e), type='negative')
            
            ui.button('Submit Grievance', on_click=submit_grievance, icon='send').props('color=primary')
        
        # My Grievances
        if user_grievances:
            with ui.card().classes('w-full p-6'):
                ui.label('My Grievances').classes('text-xl font-bold mb-4')
                
                for g in user_grievances:
                    with ui.card().classes('w-full p-4 border-l-4 border-blue-500 mb-3'):
                        with ui.row().classes('w-full justify-between items-start'):
                            with ui.column():
                                ui.label(f'{g.ticket_number}: {g.subject}').classes('font-bold')
                                ui.label(g.description).classes('text-sm text-gray-600')
                                ui.label(f'Status: {g.status.value} | SLA: {g.sla_deadline.strftime("%Y-%m-%d")}').classes('text-xs text-gray-500 mt-2')
                            
                            ui.badge(g.status.value, color='orange' if g.status.value == 'pending' else 'green')
                        
                        if g.status.value in ['pending', 'in_progress']:
                            ui.button('Escalate to DPB', on_click=lambda gid=g.id: escalate_grievance(gid)).props('size=sm flat')


def edit_profile_dialog(user):
    """Dialog to edit user profile"""
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label('Edit Profile').classes('text-xl font-bold mb-4')
        
        name_input = ui.input('Name', value=user.name).classes('w-full')
        phone_input = ui.input('Phone', value=user.phone or '').classes('w-full')
        address_input = ui.textarea('Address', value=user.address or '').classes('w-full')
        
        def save_profile():
            try:
                db = next(get_db())
                UserService.update_user_profile(
                    db=db,
                    user_id=user.id,
                    name=name_input.value,
                    phone=phone_input.value,
                    address=address_input.value
                )
                ui.notify('Profile updated successfully', type='positive')
                dialog.close()
                ui.navigate.reload()
            except Exception as e:
                ui.notify(str(e), type='negative')
        
        with ui.row().classes('gap-3 mt-4'):
            ui.button('Save', on_click=save_profile).props('color=primary')
            ui.button('Cancel', on_click=dialog.close).props('flat')
    
    dialog.open()


def download_data(user_id):
    """Download user data (Right to Portability)"""
    try:
        db = next(get_db())
        data = UserService.export_user_data(db, user_id)
        
        # In NiceGUI, we can trigger download by creating a link
        json_str = json.dumps(data, indent=2)
        ui.download(json_str.encode(), 'my-personal-data.json')
        ui.notify('Data downloaded successfully', type='positive')
    except Exception as e:
        ui.notify(str(e), type='negative')


def delete_account_dialog(user_id):
    """Dialog to confirm account deletion"""
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label('Delete Account').classes('text-xl font-bold mb-4 text-red-600')
        ui.label('Are you sure you want to delete your account? This action will schedule your account for deletion in 30 days as per DPDP Act.').classes('mb-4')
        
        def confirm_delete():
            try:
                db = next(get_db())
                user = UserService.request_deletion(db, user_id)
                ui.notify(f'Account scheduled for deletion on {user.scheduled_deletion_at.strftime("%Y-%m-%d")}', type='warning')
                dialog.close()
                ui.navigate.reload()
            except Exception as e:
                ui.notify(str(e), type='negative')
        
        with ui.row().classes('gap-3 mt-4'):
            ui.button('Yes, Delete', on_click=confirm_delete).props('color=red')
            ui.button('Cancel', on_click=dialog.close).props('flat')
    
    dialog.open()


def escalate_grievance(grievance_id):
    """Escalate grievance to Data Protection Board"""
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label('Escalate to Data Protection Board').classes('text-xl font-bold mb-4')
        
        reason = ui.textarea('Reason for Escalation', placeholder='Explain why you are escalating...').classes('w-full')
        
        def do_escalate():
            try:
                db = next(get_db())
                current_user = None  # Get from session
                GrievanceService.escalate_grievance(
                    db=db,
                    grievance_id=grievance_id,
                    user_id=current_user['id'],
                    reason=reason.value
                )
                ui.notify('Grievance escalated to Data Protection Board', type='warning')
                dialog.close()
                ui.navigate.reload()
            except Exception as e:
                ui.notify(str(e), type='negative')
        
        with ui.row().classes('gap-3 mt-4'):
            ui.button('Escalate', on_click=do_escalate).props('color=orange')
            ui.button('Cancel', on_click=dialog.close).props('flat')
    
    dialog.open()