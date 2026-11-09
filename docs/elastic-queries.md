# Kibana Discover KQL examples

These searches apply to **synthetic documents** indexed into `tradelink-security-lab`. Create a data view for the index, select `@timestamp`, and set the date filter to include **2026-10-19**.

### Failed logins

```text
event.action: "login_failure" and user.name: "supplier_alpha"
```

### Denied order requests

```text
event.action: "order_view" and http.response.status_code: 403
```

### Bulk exports

```text
event.action: "data_export" and export.record_count >= 500
```

### Unapproved role changes

```text
event.action: "role_change" and iam.approved: false
```

These KQL statements **filter logs**; they are not installed alerting rules.
