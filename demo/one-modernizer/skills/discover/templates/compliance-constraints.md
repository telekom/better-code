# Compliance & Regulatory Constraints

## Applicable Frameworks

| Framework                    | Scope             | Audit Frequency      | Last Audit | Findings       |
| ---------------------------- | ----------------- | -------------------- | ---------- | -------------- |
| {{SOX/PCI/GDPR/HIPAA/Basel}} | {{which modules}} | {{annual/quarterly}} | {{date}}   | {{open items}} |

## Data Classification

| Classification | Definition              | Handling Requirements                 | Modules Containing |
| -------------- | ----------------------- | ------------------------------------- | ------------------ |
| Restricted     | {{PII, financial, etc}} | {{encryption, access control, audit}} | {{list}}           |
| Confidential   | {{internal business}}   | {{access control}}                    | {{list}}           |
| Internal       | {{general business}}    | {{standard}}                          | {{list}}           |
| Public         | {{non-sensitive}}       | {{none special}}                      | {{list}}           |

## Audit Trail Requirements

| What Must Be Logged | Retention Period | Format/Location | Regulatory Basis  |
| ------------------- | ---------------- | --------------- | ----------------- |
| {{event type}}      | {{years}}        | {{where/how}}   | {{SOX Section X}} |

## Data Retention Rules

| Data Category | Retention Period | Archival Method | Deletion Requirement |
| ------------- | ---------------- | --------------- | -------------------- |
| {{category}}  | {{years}}        | {{method}}      | {{hard/soft delete}} |

## Access Control Requirements

| System/Module | Access Model | Approval Process | Recertification |
| ------------- | ------------ | ---------------- | --------------- |
| {{name}}      | {{RBAC/ACL}} | {{who approves}} | {{frequency}}   |

## Change Management Constraints

- Freeze windows: {{dates/events}}
- Required approvals for production changes: {{list}}
- Change lead time requirements: {{days}}
- Rollback requirements: {{what must be reversible}}

## Migration-Specific Constraints

- [ ] Data must not leave {{region/jurisdiction}} during migration
- [ ] System availability must remain above {{%}} during cutover
- [ ] All audit trails must be preserved and accessible post-migration
- [ ] Encryption at rest must be maintained throughout migration
- [ ] {{Other constraints discovered during SME interviews}}
