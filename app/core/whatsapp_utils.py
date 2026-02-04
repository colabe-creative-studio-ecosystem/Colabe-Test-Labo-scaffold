"""
Utility functions for WhatsApp integration.
"""

import reflex as rx
from typing import Optional
from app.core.models import WhatsAppAccount


def resolve_workspace_by_phone_number_id(phone_number_id: str) -> Optional[int]:
    """
    Resolve workspace (tenant) ID from WhatsApp phone number ID.
    
    Used by webhooks to identify which workspace a WhatsApp message belongs to.
    
    Args:
        phone_number_id: The WhatsApp phone number ID from the webhook
        
    Returns:
        The workspace (tenant) ID if found, None otherwise
    """
    with rx.session() as session:
        account = session.query(WhatsAppAccount).filter(
            WhatsAppAccount.phone_number_id == phone_number_id
        ).first()
        
        if account:
            return account.workspace_id
        
        return None
