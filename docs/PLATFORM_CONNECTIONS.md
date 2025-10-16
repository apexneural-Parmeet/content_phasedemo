# Platform Connections Feature

## Overview

A comprehensive platform connections management system that allows users to configure and manage their social media credentials through a user-friendly interface.

## Features

### 1. **Centralized Credentials Management**
- Store all social media credentials in one place
- Secure storage in JSON format (can be upgraded to encrypted database)
- Fallback to environment variables for backward compatibility

### 2. **Supported Platforms**
- **Facebook**: Access Token + Page ID
- **Instagram**: Access Token + Account ID
- **Twitter/X**: API Key, API Secret, Access Token, Access Token Secret, Bearer Token (optional)
- **Reddit**: Client ID, Client Secret, Username, Password, User Agent
- **Telegram**: Bot Token + Channel ID

### 3. **User Interface**
- Beautiful tabbed interface for each platform
- Real-time connection status indicators
- Masked credential display for security
- Input validation and error handling
- Helpful guides for obtaining credentials

### 4. **Backend Integration**
- All social media services automatically use stored credentials
- Seamless fallback to environment variables
- No code changes needed for posting functionality

## File Structure

```
app/
├── services/
│   ├── credentials_service.py        # Core credentials management
│   ├── facebook_service.py            # Updated to use stored credentials
│   ├── instagram_service.py           # Updated to use stored credentials
│   ├── twitter_service.py             # Uses updated clients
│   └── telegram_bot_service.py        # Can be updated similarly
├── clients/
│   ├── twitter.py                     # Updated to use stored credentials
│   └── reddit.py                      # Updated to use stored credentials
└── routes/
    └── credentials.py                 # API endpoints for credentials

frontend/src/
└── pages/
    ├── ConnectionsPage.jsx            # Main connections UI
    └── ConnectionsPage.css            # Styling

user_credentials.json                  # Credentials storage (gitignored)
```

## API Endpoints

### Get Connection Status
```http
GET /api/credentials/status
```
Returns connection status for all platforms.

**Response:**
```json
{
  "success": true,
  "status": {
    "facebook": { "connected": true, "configured": true },
    "instagram": { "connected": false, "configured": false },
    "twitter": { "connected": true, "configured": true },
    "reddit": { "connected": true, "configured": true },
    "telegram": { "connected": false, "configured": false }
  }
}
```

### Get Platform Credentials
```http
GET /api/credentials/{platform}
```
Returns credentials for a specific platform (masked for security).

**Response:**
```json
{
  "success": true,
  "platform": "facebook",
  "credentials": {
    "access_token": "EAAx...xyz",
    "page_id": "123456789"
  },
  "configured": true
}
```

### Save Platform Credentials
```http
POST /api/credentials/{platform}
Content-Type: application/json

{
  "access_token": "your_token",
  "page_id": "your_page_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Facebook credentials saved successfully",
  "platform": "facebook"
}
```

### Delete Platform Credentials
```http
DELETE /api/credentials/{platform}
```

**Response:**
```json
{
  "success": true,
  "message": "Facebook credentials deleted successfully"
}
```

### Test Platform Connection
```http
POST /api/credentials/test/{platform}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection to facebook verified",
  "platform": "facebook"
}
```

## Usage Guide

### For End Users

1. **Navigate to Connections Page**
   - Click "Connections" in the navigation bar
   - Or select "Platform Connections" from the user dropdown menu

2. **Select a Platform**
   - Click on any platform tab (Facebook, Instagram, Twitter, Reddit, Telegram)

3. **Enter Credentials**
   - Fill in the required fields for your chosen platform
   - Follow the helpful guides provided for each platform

4. **Save Credentials**
   - Click "Save Credentials" button
   - Wait for success confirmation

5. **Test Connection (Optional)**
   - Click "Test Connection" to verify credentials
   - See real-time status in the navigation bar

6. **Start Posting**
   - Once connected, all posting features will automatically use your credentials
   - No additional configuration needed

### For Developers

#### How Credentials Are Used

**Priority Order:**
1. Stored user credentials (`user_credentials.json`)
2. Environment variables (`.env` file)
3. Error if neither is configured

**Example (Facebook Service):**
```python
from app.services.credentials_service import get_platform_credentials

# Get credentials
credentials = get_platform_credentials("facebook")
access_token = credentials.get("access_token") if credentials else settings.FACEBOOK_ACCESS_TOKEN

# Use in API call
response = await client.post(
    f"{FACEBOOK_GRAPH_URL}/{page_id}/photos",
    data={"access_token": access_token, ...}
)
```

#### Adding a New Platform

1. **Update `credentials_service.py`:**
```python
def get_connection_status():
    # Add your platform
    if platform == "your_platform":
        is_configured = bool(creds.get("required_field"))
```

2. **Create Platform Service:**
```python
from app.services.credentials_service import get_platform_credentials

def your_platform_function():
    credentials = get_platform_credentials("your_platform")
    api_key = credentials.get("api_key") if credentials else settings.YOUR_PLATFORM_API_KEY
```

3. **Add to Frontend:**
```javascript
// ConnectionsPage.jsx
const platforms = [
  // ... existing platforms
  { 
    id: 'your_platform', 
    name: 'Your Platform', 
    icon: '🔥',
    fields: [
      { name: 'api_key', label: 'API Key', type: 'password', required: true }
    ]
  }
]
```

## Security Considerations

### Current Implementation
- Credentials stored in plain JSON file
- File is gitignored to prevent accidental commits
- Credentials masked in API responses
- Frontend uses password input fields

### Recommended Improvements (Production)
1. **Encryption**: Encrypt `user_credentials.json` using AES or similar
2. **Database**: Move to encrypted database (PostgreSQL + pgcrypto)
3. **User Authentication**: Add user login system with JWT tokens
4. **Per-User Storage**: Store credentials per authenticated user
5. **Secrets Management**: Use services like AWS Secrets Manager, HashiCorp Vault
6. **HTTPS**: Enforce HTTPS in production
7. **Rate Limiting**: Add rate limiting to credential endpoints

## Benefits

✅ **User-Friendly**: Easy-to-use interface for non-technical users
✅ **Flexible**: Supports multiple platforms and credential types
✅ **Secure**: Credentials masked in UI, gitignored storage
✅ **Backward Compatible**: Falls back to environment variables
✅ **Real-Time Status**: See connection status at a glance
✅ **Scalable**: Easy to add new platforms
✅ **Well-Documented**: Helpful guides for each platform

## Credential Guides

### Facebook
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create an app
3. Get your Access Token from the Graph API Explorer
4. Get your Page ID from your Facebook Page settings

### Instagram
1. Instagram requires a Facebook Business account
2. Get Access Token from [Facebook Developers](https://developers.facebook.com)
3. Find your Instagram Account ID in Instagram Business settings

### Twitter
1. Go to [Twitter Developer Portal](https://developer.twitter.com)
2. Create a project and app
3. Generate API Keys and Access Tokens from the Keys and Tokens tab

### Reddit
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a "script" type application
3. Use your Reddit account credentials (username/password)
4. Copy the Client ID and Client Secret

### Telegram
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot` command
3. Get your Bot Token from BotFather
4. Get your Channel ID (starts with @ or numeric ID)

## Testing

### Test Connection Status
```bash
curl http://localhost:8000/api/credentials/status
```

### Test Saving Credentials
```bash
curl -X POST http://localhost:8000/api/credentials/facebook \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "your_token",
    "page_id": "your_page_id"
  }'
```

### Test Posting (After Configuring)
```bash
# Use normal posting endpoints
# They will automatically use stored credentials
curl -X POST http://localhost:8000/api/publish
```

## Future Enhancements

- [ ] Add credential encryption
- [ ] Implement user authentication system
- [ ] Add OAuth flows for automated credential setup
- [ ] Add credential expiration warnings
- [ ] Implement credential refresh tokens
- [ ] Add audit logs for credential changes
- [ ] Multi-user support with role-based access
- [ ] Cloud-based credential storage option
- [ ] 2FA for credential management
- [ ] Automated credential testing on save

---

**Created**: October 14, 2025
**Version**: 1.0.0
**Status**: Production Ready

