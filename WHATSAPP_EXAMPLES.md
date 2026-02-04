# WhatsApp Template Examples

This document provides practical examples of using WhatsApp templates in the Colabe Test Labo platform.

## Example Templates

### 1. Welcome Message

**Name:** Welcome Message  
**Category:** Utility  
**Language:** en  
**Status:** Approved

**Body:**
```
Hello {{customer_name}},

Welcome to {{company_name}}! We're excited to have you on board.

Your account has been successfully created and you can start exploring our features right away.

If you need any assistance, feel free to reach out to our support team.

Best regards,
The {{company_name}} Team
```

**Variables:**
- `customer_name`: Customer's first name
- `company_name`: Company name

---

### 2. Test Run Completion

**Name:** Test Run Completed  
**Category:** Utility  
**Language:** en  
**Status:** Approved

**Body:**
```
Test Run Update 🧪

Project: {{project_name}}
Run ID: {{run_id}}
Status: {{status}}

Tests Passed: {{tests_passed}}/{{tests_total}}
Coverage: {{coverage_percent}}%

View details: {{dashboard_url}}
```

**Variables:**
- `project_name`: Name of the project
- `run_id`: Test run identifier
- `status`: Run status (passed/failed)
- `tests_passed`: Number of tests passed
- `tests_total`: Total number of tests
- `coverage_percent`: Code coverage percentage
- `dashboard_url`: Link to dashboard

---

### 3. Security Alert

**Name:** Critical Security Finding  
**Category:** Utility  
**Language:** en  
**Status:** Approved

**Body:**
```
⚠️ Security Alert

A critical security finding was detected in {{project_name}}.

Severity: {{severity}}
Scanner: {{scanner_name}}
File: {{file_path}}
Line: {{line_number}}

Description: {{description}}

Please review and address this finding immediately.

View: {{finding_url}}
```

**Variables:**
- `project_name`: Project name
- `severity`: Finding severity (CRITICAL/HIGH/MEDIUM/LOW)
- `scanner_name`: Security scanner used
- `file_path`: Path to affected file
- `line_number`: Line number of issue
- `description`: Finding description
- `finding_url`: Link to finding details

---

### 4. Deployment Notification

**Name:** Deployment Success  
**Category:** Utility  
**Language:** en  
**Status:** Approved

**Body:**
```
✅ Deployment Successful

Environment: {{environment}}
Version: {{version}}
Deployed by: {{deployer_name}}
Time: {{deployment_time}}

Changes:
{{change_summary}}

Dashboard: {{dashboard_url}}
```

**Variables:**
- `environment`: Deployment environment (production/staging/dev)
- `version`: Deployed version number
- `deployer_name`: Name of person who deployed
- `deployment_time`: Timestamp of deployment
- `change_summary`: Summary of changes
- `dashboard_url`: Link to dashboard

---

### 5. Order Confirmation (Marketing)

**Name:** Order Confirmation  
**Category:** Marketing  
**Language:** en  
**Status:** Approved

**Body:**
```
Thank you for your order, {{customer_name}}! 🎉

Order #{{order_id}}
Total: ${{order_total}}

Items:
{{item_list}}

Estimated delivery: {{delivery_date}}

Track your order: {{tracking_url}}

Questions? Reply to this message or visit {{support_url}}
```

**Variables:**
- `customer_name`: Customer name
- `order_id`: Order number
- `order_total`: Total amount
- `item_list`: List of ordered items
- `delivery_date`: Expected delivery date
- `tracking_url`: Order tracking URL
- `support_url`: Support page URL

---

### 6. Authentication Code

**Name:** Verification Code  
**Category:** Authentication  
**Language:** en  
**Status:** Approved

**Body:**
```
Your {{company_name}} verification code is:

{{verification_code}}

This code will expire in {{expiry_minutes}} minutes.

If you didn't request this code, please ignore this message.

Never share this code with anyone.
```

**Variables:**
- `company_name`: Company name
- `verification_code`: 6-digit code
- `expiry_minutes`: Code expiry time in minutes

---

## Action Plan Configuration Examples

### Example 1: Welcome New Users

**Action Plan Configuration:**
```json
{
  "project_id": 1,
  "name": "Send Welcome Message",
  "kind": "send_template",
  "template_id": 1,
  "config_json": {
    "variables": {
      "customer_name": "{{user.first_name}}",
      "company_name": "Colabe Test Labo"
    },
    "type": "whatsapp_template"
  }
}
```

**Trigger:** User registration complete  
**Result:** New user receives welcome message with their name

---

### Example 2: Test Completion Alert

**Action Plan Configuration:**
```json
{
  "project_id": 2,
  "name": "Notify Test Completion",
  "kind": "send_template",
  "template_id": 2,
  "config_json": {
    "variables": {
      "project_name": "{{project.name}}",
      "run_id": "{{run.id}}",
      "status": "{{run.status}}",
      "tests_passed": "{{run.tests_passed}}",
      "tests_total": "{{run.tests_total}}",
      "coverage_percent": "{{run.coverage_percent}}",
      "dashboard_url": "https://app.example.com/runs/{{run.id}}"
    },
    "type": "whatsapp_template"
  }
}
```

**Trigger:** Test run completion  
**Result:** Team receives test results summary

---

### Example 3: Security Finding Alert

**Action Plan Configuration:**
```json
{
  "project_id": 3,
  "name": "Alert Critical Security Finding",
  "kind": "send_template",
  "template_id": 3,
  "config_json": {
    "variables": {
      "project_name": "{{project.name}}",
      "severity": "{{finding.severity}}",
      "scanner_name": "{{finding.scanner}}",
      "file_path": "{{finding.file_path}}",
      "line_number": "{{finding.line_number}}",
      "description": "{{finding.description}}",
      "finding_url": "https://app.example.com/security/{{finding.id}}"
    },
    "type": "whatsapp_template",
    "filter": {
      "severity": ["CRITICAL", "HIGH"]
    }
  }
}
```

**Trigger:** Critical or high severity security finding  
**Result:** Security team receives immediate alert

---

## Best Practices

### 1. Template Design

- **Keep it concise**: WhatsApp messages should be brief and to the point
- **Clear CTAs**: Include clear calls-to-action with links
- **Personalization**: Use variables to personalize messages
- **Formatting**: Use line breaks and emojis appropriately
- **Language**: Use simple, friendly language

### 2. Variable Naming

- Use descriptive names: `customer_name` not `cn`
- Use snake_case: `order_total` not `orderTotal`
- Keep them consistent across templates
- Document what each variable represents

### 3. Variable Values

- Always provide fallback values
- Validate data before sending
- Format numbers and dates consistently
- Escape special characters if needed
- Keep values concise

### 4. Template Categories

- **Utility**: Transactional messages (confirmations, notifications)
- **Marketing**: Promotional messages (offers, announcements)
- **Authentication**: Security codes and verifications

### 5. Status Management

- **Draft**: Template in development, not approved
- **Pending Approval**: Submitted for review
- **Approved**: Ready for use in production
- **Rejected**: Needs revision

### 6. Testing

Before approving a template:
1. Test with various variable values
2. Check on different devices
3. Verify character limits
4. Test special characters and emojis
5. Review with compliance team

### 7. Compliance

- Follow WhatsApp Business Policy
- Include opt-out instructions where required
- Respect user preferences
- Maintain audit trail of all messages
- Follow regional regulations (GDPR, CCPA, etc.)

## Variable Data Sources

When implementing the sending logic, variables can be sourced from:

### Database Models
```python
# User data
customer_name = user.username
customer_email = user.email

# Project data
project_name = project.name
project_id = project.id

# Run data
run_id = run.id
status = run.status
tests_passed = calculate_passed_tests(run)
```

### Calculated Values
```python
# Coverage calculation
coverage_percent = (run.covered_lines / run.total_lines) * 100

# Status formatting
status_display = "✅ Passed" if run.status == "passed" else "❌ Failed"

# Date formatting
deployment_time = run.created_at.strftime("%Y-%m-%d %H:%M UTC")
```

### External APIs
```python
# Order information from e-commerce API
order_data = fetch_order(order_id)
order_total = order_data['total']
item_list = format_items(order_data['items'])

# Tracking URL from shipping API
tracking_url = get_tracking_url(shipment_id)
```

## Rate Limiting

Consider implementing rate limits:

- **Per User**: 10 messages per hour
- **Per Project**: 100 messages per hour
- **Per Template**: 1000 messages per day
- **Global**: 10,000 messages per day

## Error Handling

Handle common errors gracefully:

1. **Missing Variables**: Use placeholder values
2. **Invalid Template**: Fall back to simple notification
3. **API Failures**: Retry with exponential backoff
4. **Rate Limits**: Queue messages for later delivery
5. **Invalid Recipients**: Log and skip

## Monitoring

Track important metrics:

- Template usage count
- Delivery success rate
- Average delivery time
- Error rates by template
- User engagement (replies, clicks)

## Migration Guide

To migrate existing notifications to WhatsApp templates:

1. Identify notification types
2. Create corresponding templates
3. Map existing variables to template variables
4. Test thoroughly in staging
5. Roll out gradually to production
6. Monitor and optimize

## Support

For help with templates:
- Review this documentation
- Check template validation errors
- Test in preview mode first
- Contact support team for approval process
