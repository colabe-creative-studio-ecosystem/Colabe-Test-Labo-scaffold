# WhatsApp Multi-Tenant Integration

This implementation adds support for multi-tenant WhatsApp account mapping.

## Models

### WhatsAppAccount
Represents a WhatsApp Business Account linked to a workspace (tenant).

**Fields:**
- `id`: Primary key
- `workspace_id`: Foreign key to tenant (workspace)
- `provider`: Provider name (default: "meta")
- `phone_number_id`: WhatsApp phone number ID (indexed for fast lookups)
- `business_account_id`: WhatsApp Business Account ID
- `display_phone_number`: Display phone number (e.g., "+1234567890")
- `status`: Account status ("active" or "disabled")
- `created_at`: Timestamp of creation

### WhatsAppSecret
Stores encrypted secrets for WhatsApp integration per workspace.

**Fields:**
- `id`: Primary key
- `workspace_id`: Foreign key to tenant (workspace)
- `key_name`: Name/identifier of the secret
- `secret_encrypted`: Encrypted secret value
- `created_at`: Timestamp of creation

**Important:** Secrets are stored encrypted and should never be logged.

## Helper Functions

### `resolve_workspace_by_phone_number_id(phone_number_id: str) -> Optional[int]`

Located in `app/core/whatsapp_utils.py`

Resolves a workspace (tenant) ID from a WhatsApp phone number ID. This is primarily used by webhooks to identify which workspace a WhatsApp message belongs to.

**Usage:**
```python
from app.core.whatsapp_utils import resolve_workspace_by_phone_number_id

# In a webhook handler
phone_number_id = webhook_data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
workspace_id = resolve_workspace_by_phone_number_id(phone_number_id)

if workspace_id:
    # Process message for this workspace
    pass
```

## Database Migration

The migration file `51ffe7340c60_add_whatsapp_models.py` creates:
- `whatsappaccount` table
- `whatsappsecret` table
- Index on `phone_number_id` for efficient webhook lookups

To apply the migration:
```bash
alembic upgrade head
```

## Multi-Tenancy Support

- Each workspace (tenant) can have multiple WhatsApp accounts
- The `phone_number_id` index ensures fast webhook routing
- Secrets are stored per workspace for isolation
