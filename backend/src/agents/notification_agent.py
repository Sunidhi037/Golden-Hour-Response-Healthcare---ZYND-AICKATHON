from src.services.notification_service import notification_service

class NotificationAgent:
    """Agent responsible for alerting relevant parties."""

    async def send_emergency_alert(self, emergency_data: dict, hospital_data: dict):
        """
        Sends formatted email alerts to the hospital and user.
        """
        # 1. Alert Hospital
        hospital_subject = f"URGENT: Incoming Emergency - {emergency_data.get('severity', 'UNKNOWN')}"
        hospital_body = f"""
        EMERGENCY ALERT
        --------------------------------
        Severity: {emergency_data.get('severity')}
        Type: {emergency_data.get('description')}
        Patient Location: {emergency_data.get('address', 'GPS Coords Only')}
        
        ETA: {hospital_data['route_info']['duration_min']} minutes
        Distance: {hospital_data['route_info']['distance_km']} km
        """
        
        # In a real app, you'd send this to hospital_data['email']
        # For now, we send to the configured user email for testing
        await notification_service.send_email(
            recipient_email=emergency_data.get('contact_email'), 
            subject=hospital_subject, 
            body=hospital_body
        )
        
        return {"status": "alerts_sent"}

notification_agent = NotificationAgent()
