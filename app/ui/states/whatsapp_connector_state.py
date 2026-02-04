"""
WhatsApp Connector Settings State Management
"""
import reflex as rx
import sqlmodel
import re
from datetime import datetime
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import WhatsAppConnectorSettings, WhatsAppEnvironmentEnum
from app.core.encryption import encrypt_value, decrypt_value
import logging

logger = logging.getLogger(__name__)


class WhatsAppConnectorState(rx.State):
    """State for WhatsApp connector settings"""
    
    # Form fields
    phone_number_id: str = ""
    business_account_id: str = ""
    webhook_verify_token: str = ""
    access_token: str = ""
    environment: str = "simulation"
    
    # Status fields
    is_connected: bool = False
    last_webhook_received: Optional[str] = None
    last_health_check: Optional[str] = None
    health_check_status: str = "Not checked"
    
    # UI state
    is_saving: bool = False
    is_testing: bool = False
    show_access_token: bool = False
    validation_errors: dict[str, str] = {}
    
    @rx.event
    async def load_settings(self):
        """Load WhatsApp connector settings from database"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        
        try:
            with rx.session() as session:
                settings = session.exec(
                    sqlmodel.select(WhatsAppConnectorSettings)
                    .where(WhatsAppConnectorSettings.tenant_id == auth_state.user.tenant_id)
                ).first()
                
                if settings:
                    self.phone_number_id = settings.phone_number_id
                    self.business_account_id = settings.business_account_id
                    self.webhook_verify_token = settings.webhook_verify_token
                    # Decrypt access token for display (masked)
                    decrypted_token = decrypt_value(settings.access_token_encrypted)
                    self.access_token = decrypted_token if decrypted_token else ""
                    self.environment = settings.environment.value
                    self.is_connected = settings.is_connected
                    self.last_webhook_received = (
                        settings.last_webhook_received.strftime("%Y-%m-%d %H:%M:%S")
                        if settings.last_webhook_received else "Never"
                    )
                    self.last_health_check = (
                        settings.last_health_check.strftime("%Y-%m-%d %H:%M:%S")
                        if settings.last_health_check else "Never"
                    )
                    self.health_check_status = settings.health_check_status or "Not checked"
        except Exception as e:
            logger.exception(f"Error loading WhatsApp settings: {e}")
            return rx.toast("Failed to load settings.", variant="error")
    
    def validate_phone_number_id(self, value: str) -> Optional[str]:
        """Validate phone number ID format"""
        if not value:
            return "Phone Number ID is required"
        # Phone Number ID should be numeric
        if not re.match(r'^\d+$', value):
            return "Phone Number ID must contain only digits"
        return None
    
    def validate_business_account_id(self, value: str) -> Optional[str]:
        """Validate business account ID format"""
        if not value:
            return "Business Account ID is required"
        # Business Account ID should be numeric
        if not re.match(r'^\d+$', value):
            return "Business Account ID must contain only digits"
        return None
    
    def validate_webhook_verify_token(self, value: str) -> Optional[str]:
        """Validate webhook verify token"""
        if not value:
            return "Webhook Verify Token is required"
        if len(value) < 8:
            return "Webhook Verify Token must be at least 8 characters"
        # Check for embedded credentials in URLs (security requirement)
        if re.search(r'https?://[^:]+:[^@]+@', value):
            return "URLs with embedded credentials are not allowed"
        return None
    
    def validate_access_token(self, value: str) -> Optional[str]:
        """Validate access token"""
        if not value:
            return "Access Token is required"
        # Check for embedded credentials in URLs (security requirement)
        if re.search(r'https?://[^:]+:[^@]+@', value):
            return "URLs with embedded credentials are not allowed"
        return None
    
    def validate_all_fields(self) -> bool:
        """Validate all form fields"""
        errors = {}
        
        error = self.validate_phone_number_id(self.phone_number_id)
        if error:
            errors["phone_number_id"] = error
        
        error = self.validate_business_account_id(self.business_account_id)
        if error:
            errors["business_account_id"] = error
        
        error = self.validate_webhook_verify_token(self.webhook_verify_token)
        if error:
            errors["webhook_verify_token"] = error
        
        error = self.validate_access_token(self.access_token)
        if error:
            errors["access_token"] = error
        
        self.validation_errors = errors
        return len(errors) == 0
    
    @rx.event
    async def save_settings(self):
        """Save WhatsApp connector settings"""
        self.is_saving = True
        
        # Validate all fields
        if not self.validate_all_fields():
            self.is_saving = False
            return rx.toast("Please fix validation errors", variant="error")
        
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            self.is_saving = False
            return rx.toast("User not authenticated", variant="error")
        
        try:
            with rx.session() as session:
                # Check if settings exist
                existing = session.exec(
                    sqlmodel.select(WhatsAppConnectorSettings)
                    .where(WhatsAppConnectorSettings.tenant_id == auth_state.user.tenant_id)
                ).first()
                
                # Encrypt access token
                encrypted_token = encrypt_value(self.access_token)
                
                if existing:
                    # Update existing settings
                    existing.phone_number_id = self.phone_number_id
                    existing.business_account_id = self.business_account_id
                    existing.webhook_verify_token = self.webhook_verify_token
                    existing.access_token_encrypted = encrypted_token
                    existing.environment = WhatsAppEnvironmentEnum(self.environment)
                    existing.updated_at = datetime.now()
                    session.add(existing)
                else:
                    # Create new settings
                    new_settings = WhatsAppConnectorSettings(
                        tenant_id=auth_state.user.tenant_id,
                        phone_number_id=self.phone_number_id,
                        business_account_id=self.business_account_id,
                        webhook_verify_token=self.webhook_verify_token,
                        access_token_encrypted=encrypted_token,
                        environment=WhatsAppEnvironmentEnum(self.environment),
                    )
                    session.add(new_settings)
                
                session.commit()
                self.is_saving = False
                return rx.toast("Settings saved successfully", variant="success")
        except Exception as e:
            logger.exception(f"Error saving WhatsApp settings: {e}")
            self.is_saving = False
            return rx.toast("Failed to save settings", variant="error")
    
    @rx.event
    async def test_connection(self):
        """Test WhatsApp API connection"""
        self.is_testing = True
        
        # Validate all fields first
        if not self.validate_all_fields():
            self.is_testing = False
            return rx.toast("Please fix validation errors before testing", variant="error")
        
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            self.is_testing = False
            return rx.toast("User not authenticated", variant="error")
        
        try:
            # In a real implementation, this would call the WhatsApp API
            # For now, we'll simulate a successful connection test
            import asyncio
            await asyncio.sleep(1)  # Simulate API call
            
            # Update health check status
            with rx.session() as session:
                settings = session.exec(
                    sqlmodel.select(WhatsAppConnectorSettings)
                    .where(WhatsAppConnectorSettings.tenant_id == auth_state.user.tenant_id)
                ).first()
                
                if settings:
                    settings.is_connected = True
                    settings.last_health_check = datetime.now()
                    settings.health_check_status = "Connection successful (stub)"
                    session.add(settings)
                    session.commit()
                    
                    self.is_connected = True
                    self.last_health_check = settings.last_health_check.strftime("%Y-%m-%d %H:%M:%S")
                    self.health_check_status = settings.health_check_status
            
            self.is_testing = False
            return rx.toast("Connection test successful!", variant="success")
        except Exception as e:
            logger.exception(f"Error testing WhatsApp connection: {e}")
            self.is_testing = False
            return rx.toast("Connection test failed", variant="error")
    
    @rx.event
    def toggle_access_token_visibility(self):
        """Toggle access token visibility"""
        self.show_access_token = not self.show_access_token
    
    @rx.event
    def set_phone_number_id(self, value: str):
        """Set phone number ID and validate"""
        self.phone_number_id = value
        error = self.validate_phone_number_id(value)
        if error:
            self.validation_errors["phone_number_id"] = error
        elif "phone_number_id" in self.validation_errors:
            del self.validation_errors["phone_number_id"]
    
    @rx.event
    def set_business_account_id(self, value: str):
        """Set business account ID and validate"""
        self.business_account_id = value
        error = self.validate_business_account_id(value)
        if error:
            self.validation_errors["business_account_id"] = error
        elif "business_account_id" in self.validation_errors:
            del self.validation_errors["business_account_id"]
    
    @rx.event
    def set_webhook_verify_token(self, value: str):
        """Set webhook verify token and validate"""
        self.webhook_verify_token = value
        error = self.validate_webhook_verify_token(value)
        if error:
            self.validation_errors["webhook_verify_token"] = error
        elif "webhook_verify_token" in self.validation_errors:
            del self.validation_errors["webhook_verify_token"]
    
    @rx.event
    def set_access_token(self, value: str):
        """Set access token and validate"""
        self.access_token = value
        error = self.validate_access_token(value)
        if error:
            self.validation_errors["access_token"] = error
        elif "access_token" in self.validation_errors:
            del self.validation_errors["access_token"]
    
    @rx.event
    def set_environment(self, value: str):
        """Set environment"""
        self.environment = value
