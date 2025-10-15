# Security Best Practices

## Overview

While Fortes Education includes built-in guardrails, following security best practices is essential for production deployments.

## API Key Security

### Do NOT

❌ Commit API keys to version control
❌ Share `.env` files publicly
❌ Hard-code keys in source code
❌ Log API keys in application logs
❌ Use development keys in production

### DO

✅ Store keys in environment variables
✅ Use separate keys for dev/staging/prod
✅ Rotate keys regularly (every 90 days)
✅ Use key management services (AWS Secrets Manager, Azure Key Vault)
✅ Restrict API key permissions to minimum required

### Example Secure Configuration

```bash
# Bad - hardcoded
OPENAI_API_KEY=sk-abc123...

# Good - reference to secret manager
OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id prod/openai-key --query SecretString --output text)
```

## Network Security

### TLS/HTTPS

Always use HTTPS in production:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

### Firewall Rules

Restrict access to backend services:

```bash
# Allow only frontend to access backend
ufw allow from 10.0.1.0/24 to any port 8000

# Block direct external access to vector store
ufw deny 8000
```

## Authentication and Authorization

### Current State

Fortes Education currently operates without authentication for assessment purposes.

### Production Recommendations

For production deployment, implement:

1. **API Key Authentication**
```python
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if not validate_api_key(api_key):
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)
```

2. **JWT Tokens**
```python
from jose import jwt

def create_access_token(user_id: str):
    return jwt.encode({"sub": user_id}, SECRET_KEY, algorithm="HS256")
```

3. **Rate Limiting**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint():
    pass
```

## Data Protection

### PII Handling

The system redacts PII automatically, but also:

1. **Minimize Collection**: Don't request unnecessary personal data
2. **Encrypt at Rest**: Encrypt database files
3. **Secure Backups**: Encrypt backup files
4. **Audit Logs**: Log PII access for compliance

### Document Security

Protect uploaded documents:

```python
# Scan uploads for malware
import hashlib

def scan_upload(file_data: bytes):
    # Integrate with antivirus API
    # Check file hash against threat database
    pass

# Validate file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.md', '.txt'}

def validate_file_type(filename: str):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
```

## Injection Prevention

### SQL Injection

Always use parameterized queries:

```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Command Injection

Never execute shell commands with user input:

```python
# Bad
os.system(f"cat {filename}")

# Good
from pathlib import Path
Path(filename).read_text()
```

### Prompt Injection

Use the built-in guardrails:

```python
from app.services.guardrails import guardrails_service

result = guardrails_service.process_query(user_query)
if result["injection_detected"]:
    return {"error": "Invalid query"}
```

## Monitoring and Logging

### Security Logging

Log security-relevant events:

```python
import logging

security_logger = logging.getLogger("security")

# Log authentication attempts
security_logger.info(f"Login attempt: user={username}, ip={ip_address}")

# Log authorization failures
security_logger.warning(f"Unauthorized access attempt: user={user_id}, resource={resource}")

# Log guardrail activations
security_logger.warning(f"Prompt injection detected: query={query[:50]}")
```

### Log Protection

Sanitize logs to prevent information leakage:

```python
def sanitize_log(message: str) -> str:
    # Remove API keys
    message = re.sub(r'sk-[a-zA-Z0-9]{48}', 'sk-***', message)
    # Remove emails
    message = re.sub(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '***@***.***', message, flags=re.IGNORECASE)
    return message
```

## Dependency Security

### Regular Updates

Keep dependencies current:

```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Dependency Scanning

Add to CI/CD:

```yaml
# .github/workflows/security.yml
- name: Run security scan
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## Production Deployment Checklist

- [ ] All API keys stored securely (not in code)
- [ ] HTTPS/TLS enabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] PII redaction enabled and tested
- [ ] Input validation on all endpoints
- [ ] SQL injection protection verified
- [ ] Firewall rules configured
- [ ] Security logging enabled
- [ ] Dependencies scanned for vulnerabilities
- [ ] Backup encryption enabled
- [ ] Incident response plan documented
- [ ] Security audit completed

## Incident Response

### Detection

Monitor for:
- Unusual query patterns
- High error rates
- Guardrail activation spikes
- Unauthorized access attempts

### Response Steps

1. **Identify**: Confirm security incident
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat
4. **Recover**: Restore normal operations
5. **Learn**: Document and improve

### Contact

For security issues:
- Email: security@fortes-eduction.example
- Report vulnerabilities responsibly
- Do not publicly disclose until patched

