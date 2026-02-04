# WhatsApp Template Messages Feature

This document describes the WhatsApp Template Messages feature implementation for the Colabe Test Labo platform.

## Overview

The WhatsApp Template Messages feature allows businesses to use approved WhatsApp message templates for outbound communication. This includes creating, managing, and using templates with dynamic variable substitution.

## Database Models

### WhatsAppTemplate

Stores WhatsApp message templates with their metadata and configuration.

**Fields:**
- `id` (Integer, Primary Key): Unique identifier
- `workspace_id` (Integer, Foreign Key -> tenant.id): Associated workspace/tenant
- `name` (String): Template name
- `language` (String, default='en'): Template language code
- `category` (TemplateCategoryEnum): Template category
  - `utility`: Utility messages (default)
  - `marketing`: Marketing messages
  - `authentication`: Authentication messages
- `body` (String): Template message body with variable placeholders
- `variables_json` (String, default='[]'): JSON array of variable names extracted from body
- `status` (TemplateStatusEnum): Template approval status
  - `draft`: Draft template (default)
  - `pending_approval`: Awaiting approval
  - `approved`: Approved for use
  - `rejected`: Rejected
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Example:**
```python
template = WhatsAppTemplate(
    workspace_id=1,
    name="Welcome Message",
    language="en",
    category=TemplateCategoryEnum.UTILITY,
    body="Hello {{customer_name}}, welcome to {{company_name}}! Your account is ready.",
    variables_json='["customer_name", "company_name"]',
    status=TemplateStatusEnum.APPROVED
)
```

### ActionPlan

Defines automated actions that can be triggered, including sending WhatsApp templates.

**Fields:**
- `id` (Integer, Primary Key): Unique identifier
- `project_id` (Integer, Foreign Key -> project.id): Associated project
- `name` (String): Action plan name
- `kind` (ActionKindEnum): Action type
  - `send_template`: Send WhatsApp template (ACTION_SEND_TEMPLATE)
  - `notify`: Send notification
  - `alert`: Send alert
- `template_id` (Integer, Foreign Key -> whatsapptemplate.id, Optional): Associated template
- `config_json` (String, default='{}'): JSON configuration including variable mappings
- `created_at` (DateTime): Creation timestamp

**Example:**
```python
action = ActionPlan(
    project_id=1,
    name="Send Welcome Message",
    kind=ActionKindEnum.ACTION_SEND_TEMPLATE,
    template_id=1,
    config_json='{"variables": {"customer_name": "John", "company_name": "Acme"}, "type": "whatsapp_template"}'
)
```

## State Management

### WhatsAppState

Manages WhatsApp template CRUD operations and variable handling.

**Key Methods:**
- `load_templates()`: Load templates for current workspace
- `create_template()`: Create new template with variable extraction
- `update_template()`: Update existing template
- `delete_template(template_id)`: Delete template
- `_extract_variables(body)`: Extract variables from template body (format: `{{variable_name}}`)
- `get_preview_text()`: Get template with variables replaced

### ActionPlanState

Manages action plans with template selection and variable composition.

**Key Methods:**
- `load_action_plans(project_id)`: Load action plans for project
- `load_templates_for_picker()`: Load approved templates for selection
- `select_template(template_id)`: Select template and initialize variables
- `set_variable_value(var_name, value)`: Set variable value
- `create_action_plan(project_id)`: Create action plan with configured template
- `get_template_preview()`: Preview template with variable substitution

## UI Components

### WhatsApp Templates Page (`/whatsapp-templates`)

Main page for managing WhatsApp templates.

**Features:**
- List all templates with status badges and categories
- Create new templates with:
  - Name
  - Body (supports `{{variable}}` syntax)
  - Language
  - Category
- Edit existing templates
- Delete templates
- Status management (draft, pending_approval, approved, rejected)
- Automatic variable extraction from template body

**Navigation:**
Added to sidebar as "WhatsApp Templates" with message-circle icon.

### Template Picker Component

Modal component for selecting templates when creating action plans.

**Features:**
- Display approved templates only
- Show template preview
- Select template for action configuration

**Usage:**
```python
from app.ui.components.template_picker import (
    template_picker_button,
    template_picker_modal,
    variable_composer_modal
)

# In your page
template_picker_button()
template_picker_modal()
variable_composer_modal()
```

### Variable Composer

Modal for configuring template variables when creating action plans.

**Features:**
- Action name input
- Dynamic variable input fields based on selected template
- Real-time preview with variable substitution
- Variable validation

## Variable Syntax

Templates support variable placeholders using double curly braces:

**Format:** `{{variable_name}}`

**Example:**
```
Hello {{customer_name}},

Your order {{order_id}} has been confirmed!
Total: ${{order_total}}

Thank you for choosing {{company_name}}.
```

**Extracted Variables:**
- `customer_name`
- `order_id`
- `order_total`
- `company_name`

## Variable Safety

The system ensures safe variable handling:

1. **Extraction**: Variables are automatically extracted from template body using regex pattern `\{\{(\w+)\}\}`
2. **Validation**: Only alphanumeric variable names are supported
3. **Storage**: Variables are stored as JSON array in `variables_json` field
4. **Substitution**: Variables are replaced with user-provided values or placeholder `[variable_name]`
5. **Preview**: Real-time preview shows the final message before sending

## Database Migration

The feature includes automatic table creation in `db_init.py`:

```python
# Creates whatsapptemplate table
CREATE TABLE IF NOT EXISTS whatsapptemplate (
    id INTEGER PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    language VARCHAR NOT NULL DEFAULT 'en',
    category VARCHAR NOT NULL DEFAULT 'utility',
    body VARCHAR NOT NULL,
    variables_json VARCHAR NOT NULL DEFAULT '[]',
    status VARCHAR NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES tenant(id)
)

# Creates actionplan table
CREATE TABLE IF NOT EXISTS actionplan (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    kind VARCHAR NOT NULL,
    template_id INTEGER,
    config_json VARCHAR NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id),
    FOREIGN KEY (template_id) REFERENCES whatsapptemplate(id)
)
```

## Workflow

### Creating a Template

1. Navigate to **WhatsApp Templates** page
2. Click **Create Template**
3. Enter template details:
   - Name (e.g., "Welcome Message")
   - Body with variables (e.g., "Hello {{name}}, welcome!")
   - Language (e.g., "en")
   - Category (utility/marketing/authentication)
4. Variables are automatically extracted
5. Template is created with "draft" status
6. Update status to "approved" when ready for use

### Using a Template in Action Plan

1. In a project, open action plan configuration
2. Click **Add WhatsApp Action**
3. Select an approved template from the picker
4. Fill in variable values in the composer
5. Preview the final message
6. Save the action plan

### Sending a Template (Future Implementation)

When an action plan is triggered:
1. Load the action plan with template
2. Resolve variables from context (e.g., customer data, order info)
3. Compose final message
4. Send via WhatsApp API
5. Log the event

## API Integration Points

Future integration with WhatsApp Business API:

1. **Template Submission**: Submit templates for WhatsApp approval
2. **Status Sync**: Sync approval status from WhatsApp
3. **Message Sending**: Send template messages via API
4. **Delivery Status**: Track message delivery and read status
5. **Webhooks**: Receive status updates from WhatsApp

## Security Considerations

1. **Variable Sanitization**: All variable values should be sanitized before sending
2. **Template Approval**: Only approved templates can be used
3. **Rate Limiting**: Implement rate limiting for message sending
4. **Audit Logging**: Log all template usage and message sends
5. **Permission Control**: Check user permissions for template management

## Future Enhancements

1. **Rich Media Support**: Add support for images, videos, buttons
2. **Template Analytics**: Track template performance metrics
3. **A/B Testing**: Test different template variations
4. **Scheduled Sends**: Schedule template messages for future delivery
5. **Bulk Sending**: Send templates to multiple recipients
6. **Dynamic Variable Sources**: Connect variables to data sources (DB, API, etc.)
7. **Template Versioning**: Maintain template version history
8. **Multi-language Support**: Better language management for templates
9. **Template Categories**: More granular template categorization
10. **Compliance Tools**: Ensure regulatory compliance for different regions

## Testing

To test the feature:

1. **Database Setup**: Ensure database migrations run successfully
2. **Template CRUD**: Create, read, update, delete templates
3. **Variable Extraction**: Test with various variable patterns
4. **Action Plans**: Create action plans with templates
5. **Preview**: Verify variable substitution in preview
6. **UI**: Test all UI interactions (modals, forms, buttons)
7. **Validation**: Test input validation and error handling

## Troubleshooting

**Issue**: Templates not appearing in picker
- **Solution**: Ensure template status is "approved"

**Issue**: Variables not extracted
- **Solution**: Use correct syntax: `{{variable_name}}` (alphanumeric only)

**Issue**: Database tables not created
- **Solution**: Restart the application to run `initialize_db()`

**Issue**: Preview not updating
- **Solution**: Check that all variables have values in the composer

## Dependencies

- `reflex`: Web framework
- `sqlmodel`: ORM for database
- `json`: Variable serialization
- `re`: Regular expression for variable extraction

## Files Modified/Created

1. `app/core/models.py`: Added WhatsAppTemplate and ActionPlan models
2. `app/core/db_init.py`: Added table creation logic
3. `app/ui/states/whatsapp_state.py`: Template management state
4. `app/ui/states/action_plan_state.py`: Action plan state
5. `app/ui/pages/whatsapp_templates.py`: Template management UI
6. `app/ui/components/template_picker.py`: Template picker and composer components
7. `app/ui/components/sidebar.py`: Added navigation link
8. `app/app.py`: Added route for templates page

## Support

For issues or questions about this feature, please refer to:
- Code documentation in source files
- Database schema documentation
- API documentation (when available)
