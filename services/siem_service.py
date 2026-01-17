import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from config import settings
from loguru import logger


class SIEMService:
    """Service for SIEM integration and security event monitoring"""
    
    # Event types
    AUTHENTICATION_FAILURE = "authentication.failure"
    AUTHENTICATION_SUCCESS = "authentication.success"
    CONSENT_GRANTED = "consent.granted"
    CONSENT_WITHDRAWN = "consent.withdrawn"
    DATA_ACCESS = "data.access"
    DATA_MODIFICATION = "data.modification"
    DATA_DELETION_REQUEST = "data.deletion.request"
    DATA_EXPORT = "data.export"
    GRIEVANCE_SUBMITTED = "grievance.submitted"
    GRIEVANCE_ESCALATED = "grievance.escalated"
    ANOMALY_DETECTED = "security.anomaly"
    BREACH_DETECTED = "security.breach"
    UNAUTHORIZED_ACCESS = "security.unauthorized_access"
    
    @staticmethod
    async def send_to_siem(event: Dict[str, Any]) -> bool:
        """Send security event to SIEM platform"""
        if not settings.SIEM_WEBHOOK_URL:
            logger.warning("SIEM webhook not configured, skipping SIEM send")
            return False
        
        try:
            # Prepare SIEM event
            siem_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "dpdp-compliance-demo",
                "application": settings.APP_NAME,
                **event
            }
            
            # Send to SIEM
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SIEM_WEBHOOK_URL,
                    json=siem_event,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.SIEM_API_KEY}"
                    },
                    timeout=10.0
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Event sent to SIEM: {event.get('eventType')}")
                    return True
                else:
                    logger.error(f"SIEM webhook failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"SIEM integration error: {e}")
            return False
    
    @staticmethod
    async def log_authentication_failure(
        user_id: Optional[str],
        email: str,
        ip_address: str,
        reason: str
    ):
        """Log authentication failure"""
        return await SIEMService.send_to_siem({
            "eventType": SIEMService.AUTHENTICATION_FAILURE,
            "severity": "medium",
            "userId": user_id,
            "email": email,
            "ipAddress": ip_address,
            "reason": reason,
            "category": "authentication"
        })
    
    @staticmethod
    async def log_data_access(
        user_id: str,
        resource_type: str,
        resource_id: str,
        ip_address: str
    ):
        """Log data access event"""
        return await SIEMService.send_to_siem({
            "eventType": SIEMService.DATA_ACCESS,
            "severity": "low",
            "userId": user_id,
            "resourceType": resource_type,
            "resourceId": resource_id,
            "ipAddress": ip_address,
            "category": "data_access"
        })
    
    @staticmethod
    async def log_anomaly_detected(
        user_id: str,
        anomaly_type: str,
        anomaly_score: float,
        details: Dict[str, Any]
    ):
        """Log security anomaly detection"""
        return await SIEMService.send_to_siem({
            "eventType": SIEMService.ANOMALY_DETECTED,
            "severity": "high",
            "userId": user_id,
            "anomalyType": anomaly_type,
            "anomalyScore": anomaly_score,
            "details": details,
            "category": "security",
            "requiresInvestigation": True
        })
    
    @staticmethod
    async def log_breach_detected(
        breach_type: str,
        affected_user_count: int,
        details: Dict[str, Any]
    ):
        """Log data breach detection"""
        return await SIEMService.send_to_siem({
            "eventType": SIEMService.BREACH_DETECTED,
            "severity": "critical",
            "breachType": breach_type,
            "affectedUsers": affected_user_count,
            "details": details,
            "category": "security",
            "requiresImmediateAction": True,
            "notifyDPB": True  # Data Protection Board
        })
    
    @staticmethod
    async def log_consent_change(
        user_id: str,
        purpose: str,
        action: str,  # "granted" or "withdrawn"
        ip_address: str
    ):
        """Log consent grant or withdrawal"""
        event_type = SIEMService.CONSENT_GRANTED if action == "granted" else SIEMService.CONSENT_WITHDRAWN
        severity = "info" if action == "granted" else "warning"
        
        return await SIEMService.send_to_siem({
            "eventType": event_type,
            "severity": severity,
            "userId": user_id,
            "purpose": purpose,
            "action": action,
            "ipAddress": ip_address,
            "category": "consent"
        })
    
    @staticmethod
    async def log_grievance_event(
        user_id: str,
        grievance_id: str,
        ticket_number: str,
        action: str,  # "submitted" or "escalated"
        ip_address: str
    ):
        """Log grievance submission or escalation"""
        event_type = SIEMService.GRIEVANCE_SUBMITTED if action == "submitted" else SIEMService.GRIEVANCE_ESCALATED
        severity = "info" if action == "submitted" else "warning"
        
        return await SIEMService.send_to_siem({
            "eventType": event_type,
            "severity": severity,
            "userId": user_id,
            "grievanceId": grievance_id,
            "ticketNumber": ticket_number,
            "action": action,
            "ipAddress": ip_address,
            "category": "grievance"
        })
    
    @staticmethod
    def detect_anomaly(
        user_id: str,
        action: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Simple anomaly detection based on rules
        In production, this would use ML models or complex rule engines
        """
        anomaly_checks = {
            "suspicious_ip_change": False,
            "unusual_access_time": False,
            "rapid_requests": False,
            "anomaly_score": 0.0
        }
        
        # Check for unusual access time (example: outside 6 AM - 10 PM)
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:
            anomaly_checks["unusual_access_time"] = True
            anomaly_checks["anomaly_score"] += 0.3
        
        # Check for multiple sensitive actions
        if action in ["data_export", "deletion_requested", "consent_withdrawn"]:
            anomaly_checks["anomaly_score"] += 0.2
        
        # If anomaly score is high, it's suspicious
        if anomaly_checks["anomaly_score"] > 0.5:
            logger.warning(f"Anomaly detected for user {user_id}: score {anomaly_checks['anomaly_score']}")
        
        return anomaly_checks
    
    @staticmethod
    async def check_and_log_anomaly(
        user_id: str,
        action: str,
        ip_address: str
    ):
        """Check for anomalies and log if detected"""
        anomaly_result = SIEMService.detect_anomaly(user_id, action, ip_address)
        
        if anomaly_result["anomaly_score"] > 0.5:
            await SIEMService.log_anomaly_detected(
                user_id=user_id,
                anomaly_type="unusual_access_pattern",
                anomaly_score=anomaly_result["anomaly_score"],
                details={
                    "action": action,
                    "ipAddress": ip_address,
                    "checks": anomaly_result
                }
            )
        
        return anomaly_result