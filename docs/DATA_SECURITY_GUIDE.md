# Data Security Guide

## 📁 Directory Structure

```
data/
├── credentials/          🔒 Highly sensitive (chmod 700)
│   ├── .gitkeep
│   ├── user_credentials.json      (chmod 600)
│   └── telegram_auth.json         (chmod 600)
└── storage/             📦 Application data (chmod 755)
    ├── .gitkeep
    └── scheduled_posts.json       (chmod 644)
```

## 🔐 What's Stored Where

### `data/credentials/` - Critical Security

**user_credentials.json** (600 permissions - owner read/write only)
- Facebook access tokens
- Instagram access tokens
- Twitter API keys & secrets
- Reddit credentials
- Telegram bot token

**telegram_auth.json** (600 permissions - owner read/write only)
- Telegram bot login ID
- Telegram bot password
- Logged-in user IDs

### `data/storage/` - Application Data

**scheduled_posts.json** (644 permissions - owner write, others read)
- Scheduled post queue
- Posted content history
- Platform status tracking

## 🛡️ Security Measures

### 1. Git Protection
```gitignore
# Entire data directory is ignored
data/
!data/credentials/.gitkeep
!data/storage/.gitkeep
```

### 2. File Permissions

| File | Permission | Meaning |
|------|-----------|---------|
| `data/credentials/` | 700 | Only owner can read/write/execute |
| `*.json` in credentials | 600 | Only owner can read/write |
| `data/storage/` | 755 | Owner full, others read/execute |
| `scheduled_posts.json` | 644 | Owner write, all read |

### 3. Code References

Files are loaded from centralized constants:

**app/config.py:**
```python
SCHEDULED_POSTS_FILE: Path = Path("data/storage/scheduled_posts.json")
```

**app/services/credentials_service.py:**
```python
CREDENTIALS_FILE = "data/credentials/user_credentials.json"
```

**app/services/telegram_auth.py:**
```python
AUTH_FILE = "data/credentials/telegram_auth.json"
```

## 🚨 Security Checklist

Before deploying or sharing:

- [ ] Verify `data/` is in `.gitignore`
- [ ] Check no JSON files committed to git
- [ ] Confirm file permissions are set (600/644)
- [ ] Ensure `.env` file is also protected
- [ ] Test that app works with new paths
- [ ] Backup `data/credentials/` separately

## 💾 Backup Strategy

### Manual Backup
```bash
# Create encrypted backup
tar -czf backup_$(date +%Y%m%d).tar.gz data/
gpg -c backup_$(date +%Y%m%d).tar.gz
rm backup_$(date +%Y%m%d).tar.gz
```

### Automated Backup Script
```bash
# scripts/backup_data.sh
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r data/ "$BACKUP_DIR/"
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
echo "✅ Backup: $BACKUP_DIR.tar.gz"
```

## 🔄 Recovery

If files are lost, they will be recreated on startup:

1. **user_credentials.json** - Empty `{}`, fill via `/connections` page
2. **telegram_auth.json** - Default credentials from `.env`
3. **scheduled_posts.json** - Empty `[]`

## ⚠️ Never Do This

❌ Don't commit `data/` directory  
❌ Don't share JSON files directly  
❌ Don't store credentials in code  
❌ Don't use weak file permissions  
❌ Don't backup to public cloud unencrypted  

## ✅ Best Practices

✅ Use environment variables for initial setup  
✅ Rotate credentials regularly  
✅ Keep backups encrypted  
✅ Monitor file access logs  
✅ Use the `/connections` page for credential management  

## 🔍 Verify Security

Run this check:
```bash
# Check permissions
ls -la data/credentials/
ls -la data/storage/

# Check git status
git status data/  # Should show "Untracked files"

# Verify not in repo
git ls-files data/  # Should be empty
```

## 📞 Emergency Procedures

### If Credentials Compromised

1. **Immediately revoke** all tokens from platform dashboards
2. Generate new tokens
3. Update via `/connections` page
4. Check logs for unauthorized access
5. Consider changing passwords

### If Files Lost

1. Check backups
2. Regenerate tokens from platforms
3. Update via UI
4. Resume normal operation

---

**Last Updated:** October 15, 2025  
**Security Level:** 🔒 High  
**Status:** ✅ Active Protection

