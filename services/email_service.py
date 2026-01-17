import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from loguru import logger


class EmailService:
    """Service for sending email notifications"""
    
    @staticmethod
    async def send_email(
        to: str,
        subject: str,
        body: str,
        html_body: str = None
    ):
        """Send email via SMTP"""
        try:
            message = MIMEMultipart('alternative')
            message['From'] = settings.FROM_EMAIL
            message['To'] = to
            message['Subject'] = subject
            
            # Attach plain text version
            message.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"Email sent to {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str):
        """Send welcome email to new users"""
        subject = f"Welcome to {settings.ORGANIZATION_NAME}"
        body = f"""
Hello {user_name},

Welcome to our DPDP Act 2023 compliant platform!

Your Rights:
- Right to access your data
- Right to correction
- Right to data portability
- Right to erasure
- Right to grievance redressal

For any concerns, contact our Data Protection Officer at {settings.DPO_EMAIL}

Best regards,
{settings.ORGANIZATION_NAME}
DPDP Compliance Team
        """
        
        return await EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    async def send_grievance_confirmation(
        user_email: str,
        user_name: str,
        ticket_number: str,
        subject: str
    ):
        """Send grievance submission confirmation"""
        email_subject = f"Grievance Submitted - {ticket_number}"
        body = f"""
Hello {user_name},

Your grievance has been submitted successfully.

Ticket Number: {ticket_number}
Subject: {subject}

We will respond within 7 days as per DPDP Act requirements.

You can track your grievance status in your dashboard.

Best regards,
{settings.DPO_NAME}
{settings.ORGANIZATION_NAME}
        """
        
        return await EmailService.send_email(user_email, email_subject, body)
    
    @staticmethod
    async def send_deletion_notice(
        user_email: str,
        user_name: str,
        scheduled_date: str
    ):
        """Send account deletion notice"""
        subject = "Account Deletion Scheduled"
        body = f"""
Hello {user_name},

Your account deletion request has been received and processed.

Scheduled Deletion Date: {scheduled_date}

You can cancel this request anytime before the scheduled date by logging into your account.

If you have any questions, contact us at {settings.DPO_EMAIL}

Best regards,
{settings.ORGANIZATION_NAME}
DPDP Compliance Team
        """
        
        return await EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    async def send_breach_notification(
        user_email: str,
        user_name: str,
        breach_details: str
    ):
        """Send data breach notification (DPDP Act requirement)"""
        subject = "URGENT: Data Breach Notification"
        body = f"""
Hello {user_name},

We are writing to inform you of a potential data breach as required under DPDP Act 2023.

Breach Details:
{breach_details}

Actions Taken:
- Incident investigation initiated
- Security measures strengthened
- Data Protection Board notified
- Affected systems isolated

We Recommend:
- Change your password immediately
- Monitor your accounts for suspicious activity
- Enable two-factor authentication
- Review recent account activity

For questions or concerns, contact:
Data Protection Officer: {settings.DPO_EMAIL}
Phone: Available in your dashboard

We sincerely apologize for any inconvenience and take data security very seriously.

Best regards,
{settings.DPO_NAME}
{settings.ORGANIZATION_NAME}
        """
        
        return await EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    async def send_consent_withdrawal_notice(
        user_email: str,
        user_name: str,
        purpose: str
    ):
        """Send consent withdrawal confirmation"""
        subject = "Consent Withdrawal Confirmation"
        body = f"""
Hello {user_name},

This email confirms that your consent for {purpose} has been withdrawn.

Effective immediately, we will no longer use your data for this purpose.

Your consent record has been updated in our system with timestamp and version information as required by DPDP Act 2023.

You can grant consent again at any time through your dashboard.

Best regards,
{settings.ORGANIZATION_NAME}
        """
        
        return await EmailService.send_email(user_email, subject, body)