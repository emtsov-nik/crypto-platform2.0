# Security Best Practices

Comprehensive security guide for the Crypto Trading Platform.

## Table of Contents

- [Security Overview](#security-overview)
- [API Key Security](#api-key-security)
- [Application Security](#application-security)
- [Database Security](#database-security)
- [Network Security](#network-security)
- [Telegram Bot Security](#telegram-bot-security)
- [Operational Security](#operational-security)
- [Incident Response](#incident-response)
- [Security Checklist](#security-checklist)

## Security Overview

### Security Principles

1. **Defense in Depth:** Multiple layers of security
2. **Least Privilege:** Minimum necessary permissions
3. **Fail Secure:** Safe defaults, secure failure modes
4. **Keep it Simple:** Complexity is the enemy of security
5. **Regular Updates:** Keep software and dependencies updated

### Threat Model

**What we're protecting:**
- Trading capital and positions
- API keys and credentials
- User data and trading history
- System integrity

**Threats:**
- Unauthorized access to trading bot
- API key theft or compromise
- SQL injection and XSS attacks
- Man-in-the-middle attacks
- DDoS attacks
- Insider threats

## API Key Security

### Binance API Key Configuration

**1. Create Restricted API Keys:**

```
✅ Enable:
- Enable Reading
- Enable Spot & Margin Trading

❌ Disable (CRITICAL):
- Enable Withdrawals
- Enable Futures
- Enable Sub-Account Transfer
```

**Why:** Even if API keys are compromised, attackers cannot withdraw funds.

**2. IP Whitelist:**

```bash
# Find your server IP
curl ifconfig.me

# Add to Binance API restrictions:
# Settings → API Management → Edit → IP Access Restriction → Restrict access to trusted IPs
```

**3. Secure Storage:**

```bash
# Never commit to git
echo ".env" >> .gitignore

# Secure permissions
chmod 600 .env

# Use environment variables, not hardcoded values
# ❌ BAD
api_key = "abc123..."

# ✅ GOOD
api_key = os.getenv('BINANCE_API_KEY')
```

**4. Key Rotation:**

```bash
# Rotate API keys every 90 days
# 1. Create new API key
# 2. Update .env file
# 3. Restart services
# 4. Delete old API key after verification
```

### Secret Management

**Using Docker Secrets:**

```yaml
# docker-compose.yml
services:
  backend:
    secrets:
      - binance_api_key
      - binance_api_secret

secrets:
  binance_api_key:
    file: ./secrets/binance_api_key.txt
  binance_api_secret:
    file: ./secrets/binance_api_secret.txt
```

**Using HashiCorp Vault:**

```python
import hvac

# Connect to Vault
client = hvac.Client(url='http://vault:8200', token=os.getenv('VAULT_TOKEN'))

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='trading/binance')
api_key = secret['data']['data']['api_key']
```

## Application Security

### Authentication & Authorization

**1. Implement JWT Authentication:**

```python
# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Use in endpoints
@app.get("/api/strategies")
def get_strategies(user_id: str = Depends(verify_token)):
    # Only authenticated users can access
    pass
```

**2. Rate Limiting:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/market/ohlcv")
@limiter.limit("100/minute")
def get_ohlcv(request: Request):
    # Limited to 100 requests per minute per IP
    pass
```

**3. Input Validation:**

```python
from pydantic import BaseModel, Field, validator

class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    params: dict

    @validator('name')
    def validate_name(cls, v):
        # Prevent SQL injection in name
        if any(char in v for char in ['\'', '"', ';', '--']):
            raise ValueError('Invalid characters in name')
        return v

    @validator('params')
    def validate_params(cls, v):
        # Validate parameter ranges
        if 'tp_percent' in v:
            if not 0 < v['tp_percent'] < 100:
                raise ValueError('TP percent must be between 0 and 100')
        return v
```

**4. CORS Configuration:**

```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ BAD: Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dangerous!
    allow_credentials=True,
)

# ✅ GOOD: Specific origins
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### SQL Injection Prevention

**Use ORM (SQLAlchemy):**

```python
# ❌ BAD: Raw SQL with string formatting
query = f"SELECT * FROM strategies WHERE name = '{user_input}'"
db.execute(query)

# ✅ GOOD: ORM with parameterized queries
strategies = db.query(Strategy).filter(Strategy.name == user_input).all()

# ✅ GOOD: If using raw SQL, use parameters
query = text("SELECT * FROM strategies WHERE name = :name")
db.execute(query, {"name": user_input})
```

### XSS Prevention

**Frontend Sanitization:**

```typescript
import DOMPurify from 'dompurify'

// Sanitize user input before rendering
const sanitizedInput = DOMPurify.sanitize(userInput)

// Use textContent instead of innerHTML when possible
element.textContent = userInput  // Safe
element.innerHTML = userInput    // Potentially unsafe
```

### Secure Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com", "www.your-domain.com"])

# Secure session
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SECRET_KEY'),
    session_cookie="session",
    max_age=3600,
    same_site="strict",
    https_only=True  # Only in production with HTTPS
)
```

## Database Security

### Connection Security

**1. Use SSL Connections:**

```python
# config.py
DATABASE_URL = os.getenv('DATABASE_URL')

# For production, use SSL
if os.getenv('ENVIRONMENT') == 'production':
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL)
```

**2. Connection Pooling:**

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

### Database Access Control

```sql
-- Create read-only user for reporting
CREATE USER readonly_user WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE trading_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Restrict trading user permissions
REVOKE ALL ON SCHEMA public FROM trading_user;
GRANT CONNECT ON DATABASE trading_db TO trading_user;
GRANT USAGE ON SCHEMA public TO trading_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trading_user;

-- Do NOT grant DROP, TRUNCATE, or ALTER
```

### Encryption at Rest

```sql
-- Enable encryption for sensitive columns
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt API keys in database
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    encrypted_key BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert encrypted key
INSERT INTO api_keys (user_id, encrypted_key)
VALUES (1, pgp_sym_encrypt('actual_api_key', 'encryption_password'));

-- Retrieve and decrypt
SELECT pgp_sym_decrypt(encrypted_key, 'encryption_password') AS api_key
FROM api_keys WHERE user_id = 1;
```

### Backup Encryption

```bash
# Encrypt backups
pg_dump -U trading_user trading_db | \
  gpg --symmetric --cipher-algo AES256 > backup.sql.gpg

# Decrypt and restore
gpg --decrypt backup.sql.gpg | psql -U trading_user trading_db
```

## Network Security

### Firewall Configuration

```bash
# Install UFW (Ubuntu)
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow only specific IPs for database (if external)
sudo ufw allow from YOUR_IP to any port 5432

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Reverse Proxy with Nginx

```nginx
# Security-focused nginx configuration
http {
    # Hide nginx version
    server_tokens off;

    # Limit request size
    client_max_body_size 10M;

    # Timeouts
    client_body_timeout 10s;
    client_header_timeout 10s;
    keepalive_timeout 5s 5s;
    send_timeout 10s;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration (see Deployment Guide)

        # API rate limiting
        location /api {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend:8000;

            # Security headers
            add_header X-Content-Type-Options nosniff;
            add_header X-Frame-Options DENY;
            add_header X-XSS-Protection "1; mode=block";
        }

        # Stricter limit for auth endpoints
        location /api/auth {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend:8000;
        }
    }
}
```

### DDoS Protection

**1. CloudFlare Integration:**
- Enable CloudFlare proxy
- Set security level to "High"
- Enable rate limiting rules
- Use WAF (Web Application Firewall)

**2. Fail2Ban:**

```bash
# Install fail2ban
sudo apt install fail2ban

# Configure for nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 600
bantime = 3600

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400
```

## Telegram Bot Security

### User Authentication

```python
# telegram_bot/config.py
import os

# Whitelist of allowed user IDs
ALLOWED_USER_IDS = [
    int(uid) for uid in os.getenv('TELEGRAM_ALLOWED_USER_IDS', '').split(',')
    if uid.strip()
]

REQUIRE_AUTH = os.getenv('TELEGRAM_REQUIRE_AUTH', 'true').lower() == 'true'

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    if not REQUIRE_AUTH:
        return True
    return user_id in ALLOWED_USER_IDS
```

**Usage:**

```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        logger.warning(f"Unauthorized access attempt by user {user_id}")
        await update.message.reply_text(
            "❌ Access Denied\n\n"
            "You are not authorized to use this bot.\n"
            f"Your Telegram ID: {user_id}"
        )
        return

    # Proceed with command
    await update.message.reply_text("✅ Welcome!")
```

### Secure Bot Token

```bash
# Get bot token from @BotFather
# Store securely in .env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# ❌ Never commit token to git
# ❌ Never share token publicly
# ❌ Never hardcode in source code

# ✅ Use environment variables
# ✅ Rotate token if compromised
# ✅ Use webhook instead of polling in production (optional)
```

### Command Confirmation

```python
# Require confirmation for critical actions
async def emergency_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Emergency stop with confirmation."""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        return

    # Send confirmation button
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Confirm Emergency Stop", callback_data="confirm_emergency"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_emergency")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚠️ **EMERGENCY STOP**\n\n"
        "This will immediately:\n"
        "- Close all open positions\n"
        "- Stop the trading bot\n"
        "- Set global emergency stop flag\n\n"
        "Are you sure?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
```

## Operational Security

### Access Control

**1. SSH Key Authentication:**

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

**2. Sudo Access:**

```bash
# Create non-root user
sudo adduser trading

# Add to sudo group
sudo usermod -aG sudo trading

# Require password for sudo
# Edit /etc/sudoers
trading ALL=(ALL) ALL
```

**3. File Permissions:**

```bash
# Secure sensitive files
chmod 600 .env
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Application files
chown -R trading:trading /opt/trading-platform
chmod 755 /opt/trading-platform
```

### Logging and Monitoring

**1. Security Event Logging:**

```python
import logging

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

handler = logging.FileHandler('/var/log/trading/security.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)

# Log security events
def log_security_event(event_type: str, user_id: int, details: str):
    security_logger.warning(f"{event_type} | User: {user_id} | {details}")

# Example usage
log_security_event("UNAUTHORIZED_ACCESS", user_id, "Attempted to access /api/trading/start")
log_security_event("EMERGENCY_STOP", user_id, "Emergency stop triggered")
log_security_event("API_KEY_ROTATION", user_id, "API key rotated")
```

**2. Intrusion Detection:**

```bash
# Install AIDE (Advanced Intrusion Detection Environment)
sudo apt install aide

# Initialize database
sudo aideinit

# Check for changes
sudo aide --check
```

### Regular Security Updates

```bash
#!/bin/bash
# update-system.sh

# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Docker images
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d

# Check for security advisories
npm audit
pip list --outdated
```

**Automate with cron:**

```bash
# Weekly security updates (Sunday 3 AM)
0 3 * * 0 /opt/scripts/update-system.sh >> /var/log/updates.log 2>&1
```

## Incident Response

### Preparation

**1. Create Incident Response Plan:**

```markdown
# Incident Response Plan

## Team Contacts
- Admin: +1-555-0001
- DevOps: +1-555-0002
- Security: +1-555-0003

## Severity Levels
1. Critical: System compromise, fund loss
2. High: Unauthorized access, data breach
3. Medium: Service disruption
4. Low: Minor issues

## Response Procedures
1. Detect and alert
2. Assess severity
3. Contain threat
4. Investigate
5. Remediate
6. Document
7. Review and improve
```

**2. Emergency Procedures:**

```python
# emergency_procedures.py

async def execute_emergency_shutdown():
    """Execute emergency shutdown procedure."""
    logger.critical("EMERGENCY SHUTDOWN INITIATED")

    try:
        # 1. Stop all trading bots
        await trading_service.stop_all_bots()

        # 2. Close all positions
        await trading_service.close_all_positions()

        # 3. Set global emergency flag
        await redis.set('emergency_stop', '1')

        # 4. Notify all admins
        await telegram_bot.notify_admins(
            "🚨 EMERGENCY SHUTDOWN EXECUTED\n"
            "All trading stopped. All positions closed."
        )

        # 5. Lock API endpoints
        await lock_trading_endpoints()

        # 6. Create incident log
        await create_incident_log("emergency_shutdown")

        logger.critical("EMERGENCY SHUTDOWN COMPLETE")

    except Exception as e:
        logger.critical(f"EMERGENCY SHUTDOWN FAILED: {e}")
        raise
```

### Detection

**Monitor for:**
- Unusual API activity
- Failed authentication attempts
- Abnormal trading patterns
- System errors and crashes
- Database anomalies

### Response Actions

**If API Key Compromised:**

1. **Immediate:**
   ```bash
   # Trigger emergency stop
   curl -X POST http://localhost:8000/api/trading/emergency-stop

   # Or via Telegram
   /emergency
   ```

2. **Within 5 minutes:**
   - Delete compromised API key from Binance
   - Change all passwords
   - Review recent trades

3. **Within 1 hour:**
   - Create new API key with IP restrictions
   - Update .env and restart services
   - Review access logs
   - Document incident

**If System Compromised:**

1. **Immediate:**
   - Disconnect from internet
   - Execute emergency shutdown
   - Preserve evidence (logs, memory dumps)

2. **Investigation:**
   - Review all logs
   - Check for unauthorized access
   - Identify attack vector
   - Assess damage

3. **Recovery:**
   - Patch vulnerabilities
   - Restore from clean backup
   - Rotate all credentials
   - Monitor closely

## Security Checklist

### Pre-Deployment

- [ ] Strong SECRET_KEY generated (32+ characters)
- [ ] All default passwords changed
- [ ] Binance API key IP restricted
- [ ] Withdrawal permissions disabled
- [ ] DEBUG=false in production
- [ ] HTTPS/SSL configured
- [ ] Firewall rules configured
- [ ] Database connection encrypted
- [ ] Sensitive data encrypted at rest
- [ ] Backup encryption enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection protection verified
- [ ] XSS protection implemented

### Regular Maintenance

- [ ] Update all dependencies monthly
- [ ] Rotate API keys every 90 days
- [ ] Review access logs weekly
- [ ] Test backups monthly
- [ ] Security audit quarterly
- [ ] Update incident response plan
- [ ] Review and test emergency procedures
- [ ] Check for security advisories

### Monitoring

- [ ] Failed login attempts logged
- [ ] API rate limit violations alerted
- [ ] Unusual trading patterns detected
- [ ] System errors monitored
- [ ] Disk space monitored
- [ ] CPU/memory usage monitored
- [ ] Database performance monitored

### Emergency Contacts

```
Support Email: security@your-domain.com
Emergency Phone: +1-555-SECURITY
Telegram: @your_admin_username

Binance Support: support@binance.com
Database Provider: db-support@provider.com
Hosting Provider: hosting-support@provider.com
```

---

**Always remember:** Security is not a one-time task, but an ongoing process. Stay vigilant, keep learning, and prioritize security in every decision.

**Previous:** [Deployment Guide](DEPLOYMENT.md) | **Back to:** [README](../README.md)
