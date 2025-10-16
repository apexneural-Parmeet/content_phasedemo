import { useState, useEffect } from 'react'
import './ConnectionsPage.css'

const ConnectionsPage = () => {
  const [activeTab, setActiveTab] = useState('facebook')
  const [connectionStatus, setConnectionStatus] = useState({})
  const [message, setMessage] = useState({ type: '', text: '' })
  const [loading, setLoading] = useState(false)
  const [isEditing, setIsEditing] = useState({})

  // Platform credentials state
  const [credentials, setCredentials] = useState({
    facebook: { access_token: '' },
    instagram: { access_token: '', account_id: '' },
    twitter: { 
      api_key: '', 
      api_secret: '', 
      access_token: '', 
      access_token_secret: '',
      bearer_token: ''
    },
    reddit: { 
      client_id: '', 
      client_secret: '', 
      username: '', 
      password: '',
      user_agent: 'SocialHub Bot v1.0'
    },
    telegram: { bot_token: '', channel_id: '' }
  })

  // Platform configurations
  const platforms = [
    { 
      id: 'facebook', 
      name: 'Facebook', 
      icon: '📘',
      fields: [
        { name: 'access_token', label: 'Page Access Token', type: 'password', required: true }
      ]
    },
    { 
      id: 'instagram', 
      name: 'Instagram', 
      icon: '📷',
      fields: [
        { name: 'access_token', label: 'Access Token', type: 'password', required: true },
        { name: 'account_id', label: 'Account ID', type: 'text', required: true }
      ]
    },
    { 
      id: 'twitter', 
      name: 'Twitter/X', 
      icon: '🐦',
      fields: [
        { name: 'api_key', label: 'API Key', type: 'password', required: true },
        { name: 'api_secret', label: 'API Secret', type: 'password', required: true },
        { name: 'access_token', label: 'Access Token', type: 'password', required: true },
        { name: 'access_token_secret', label: 'Access Token Secret', type: 'password', required: true },
        { name: 'bearer_token', label: 'Bearer Token (Optional)', type: 'password', required: false }
      ]
    },
    { 
      id: 'reddit', 
      name: 'Reddit', 
      icon: '🔴',
      fields: [
        { name: 'client_id', label: 'Client ID', type: 'password', required: true },
        { name: 'client_secret', label: 'Client Secret', type: 'password', required: true },
        { name: 'username', label: 'Username', type: 'text', required: true },
        { name: 'password', label: 'Password', type: 'password', required: true },
        { name: 'user_agent', label: 'User Agent', type: 'text', required: false }
      ]
    },
    { 
      id: 'telegram', 
      name: 'Telegram', 
      icon: '✈️',
      fields: [
        { name: 'bot_token', label: 'Bot Token', type: 'password', required: true },
        { name: 'channel_id', label: 'Channel ID', type: 'text', required: true }
      ]
    }
  ]

  useEffect(() => {
    fetchConnectionStatus()
    fetchAllCredentials()
  }, [])

  const fetchConnectionStatus = async () => {
    try {
      const response = await fetch('/api/credentials/status')
      const data = await response.json()
      if (data.success) {
        setConnectionStatus(data.status)
      }
    } catch (error) {
      console.error('Error fetching connection status:', error)
    }
  }

  const fetchAllCredentials = async () => {
    for (const platform of platforms) {
      try {
        const response = await fetch(`/api/credentials/${platform.id}`)
        const data = await response.json()
        if (data.success && data.credentials) {
          setCredentials(prev => ({
            ...prev,
            [platform.id]: { ...prev[platform.id], ...data.credentials }
          }))
        }
      } catch (error) {
        console.error(`Error fetching ${platform.id} credentials:`, error)
      }
    }
  }

  const handleInputChange = (platform, field, value) => {
    setCredentials(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        [field]: value
      }
    }))
  }

  const handleSaveCredentials = async (platform) => {
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await fetch(`/api/credentials/${platform}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials[platform])
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setMessage({ type: 'success', text: `${platforms.find(p => p.id === platform).name} credentials saved and active!` })
        setIsEditing({ ...isEditing, [platform]: false })
        await fetchConnectionStatus()
        await fetchAllCredentials()
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to save credentials' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error saving credentials. Please try again.' })
    } finally {
      setLoading(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 5000)
    }
  }

  const handleDeleteCredentials = async (platform) => {
    if (!confirm(`Are you sure you want to delete ${platforms.find(p => p.id === platform).name} credentials?`)) {
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await fetch(`/api/credentials/${platform}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setMessage({ type: 'success', text: `${platforms.find(p => p.id === platform).name} credentials removed successfully!` })
        
        // Reset form fields and editing state
        const platformConfig = platforms.find(p => p.id === platform)
        const resetCreds = {}
        platformConfig.fields.forEach(field => {
          resetCreds[field.name] = field.name === 'user_agent' ? 'SocialHub Bot v1.0' : ''
        })
        
        setCredentials(prev => ({
          ...prev,
          [platform]: resetCreds
        }))
        
        setIsEditing({ ...isEditing, [platform]: false })
        await fetchConnectionStatus()
      } else {
        setMessage({ type: 'error', text: data.message || 'Failed to delete credentials' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error deleting credentials. Please try again.' })
    } finally {
      setLoading(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 5000)
    }
  }

  const handleTestConnection = async (platform) => {
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await fetch(`/api/credentials/test/${platform}`, {
        method: 'POST'
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setMessage({ type: 'success', text: `${platforms.find(p => p.id === platform).name} connection verified!` })
      } else {
        setMessage({ type: 'error', text: data.detail || 'Connection test failed' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error testing connection. Please try again.' })
    } finally {
      setLoading(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    }
  }

  const currentPlatform = platforms.find(p => p.id === activeTab)

  return (
    <div className="connections-page">
      <div className="connections-container">
        <div className="connections-header">
          <h1>Platform Connections</h1>
          <p>Manage your credentials - The system automatically uses these tokens for all posts</p>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="connections-content">
          {/* Platform Tabs */}
          <div className="platform-tabs">
            {platforms.map(platform => (
              <button
                key={platform.id}
                className={`platform-tab ${activeTab === platform.id ? 'active' : ''} ${connectionStatus[platform.id]?.connected ? 'connected' : ''}`}
                onClick={() => setActiveTab(platform.id)}
              >
                <span className="platform-icon">{platform.icon}</span>
                <span className="platform-name">{platform.name}</span>
                {connectionStatus[platform.id]?.connected && (
                  <span className="connection-indicator">●</span>
                )}
              </button>
            ))}
          </div>

          {/* Credential Form */}
          <div className="credential-form-container">
            {currentPlatform && (
              <div className="credential-form">
                <div className="form-header">
                  <h2>
                    <span className="form-icon">{currentPlatform.icon}</span>
                    {currentPlatform.name} Configuration
                  </h2>
                  {connectionStatus[activeTab]?.connected && (
                    <span className="status-badge connected">Active & Connected</span>
                  )}
                  {!connectionStatus[activeTab]?.connected && (
                    <span className="status-badge disconnected">Not Configured</span>
                  )}
                </div>

                {connectionStatus[activeTab]?.connected && !isEditing[activeTab] && (
                  <div className="active-credentials-info">
                    <div className="info-banner">
                      <span className="info-icon">✅</span>
                      <div className="info-text">
                        <strong>Credentials Active</strong>
                        <p>The system is using saved credentials for {currentPlatform.name}. All posts will automatically use these tokens.</p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="form-fields">
                  {currentPlatform.fields.map(field => (
                    <div key={field.name} className="form-group">
                      <label htmlFor={field.name}>
                        {field.label}
                        {field.required && <span className="required">*</span>}
                      </label>
                      <input
                        type={field.type}
                        id={field.name}
                        value={credentials[activeTab][field.name] || ''}
                        onChange={(e) => handleInputChange(activeTab, field.name, e.target.value)}
                        placeholder={connectionStatus[activeTab]?.connected && !isEditing[activeTab] ? '••••••••' : `Enter ${field.label.toLowerCase()}`}
                        disabled={loading || (connectionStatus[activeTab]?.connected && !isEditing[activeTab])}
                        readOnly={connectionStatus[activeTab]?.connected && !isEditing[activeTab]}
                      />
                    </div>
                  ))}
                </div>

                <div className="form-actions">
                  {!connectionStatus[activeTab]?.connected && (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleSaveCredentials(activeTab)}
                      disabled={loading}
                    >
                      {loading ? 'Saving...' : 'Save & Activate Credentials'}
                    </button>
                  )}
                  
                  {connectionStatus[activeTab]?.connected && !isEditing[activeTab] && (
                    <>
                      <button
                        className="btn btn-secondary"
                        onClick={() => setIsEditing({ ...isEditing, [activeTab]: true })}
                        disabled={loading}
                      >
                        Edit Credentials
                      </button>
                      <button
                        className="btn btn-secondary"
                        onClick={() => handleTestConnection(activeTab)}
                        disabled={loading}
                      >
                        Test Connection
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDeleteCredentials(activeTab)}
                        disabled={loading}
                      >
                        Remove
                      </button>
                    </>
                  )}

                  {connectionStatus[activeTab]?.connected && isEditing[activeTab] && (
                    <>
                      <button
                        className="btn btn-primary"
                        onClick={() => handleSaveCredentials(activeTab)}
                        disabled={loading}
                      >
                        {loading ? 'Updating...' : 'Update Credentials'}
                      </button>
                      <button
                        className="btn btn-secondary"
                        onClick={() => {
                          setIsEditing({ ...isEditing, [activeTab]: false })
                          fetchAllCredentials()
                        }}
                        disabled={loading}
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>

                <div className="form-help">
                  <h4>How to get credentials:</h4>
                  {activeTab === 'facebook' && (
                    <ul>
                      <li>Go to <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer">Facebook Developers</a></li>
                      <li>Create an app and get your Page Access Token</li>
                      <li>Page ID will be automatically retrieved from the token</li>
                    </ul>
                  )}
                  {activeTab === 'instagram' && (
                    <ul>
                      <li>Instagram requires a Facebook Business account</li>
                      <li>Get Access Token from <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer">Facebook Developers</a></li>
                      <li>Find your Instagram Account ID in your Instagram Business settings</li>
                    </ul>
                  )}
                  {activeTab === 'twitter' && (
                    <ul>
                      <li>Go to <a href="https://developer.twitter.com" target="_blank" rel="noopener noreferrer">Twitter Developer Portal</a></li>
                      <li>Create a project and app</li>
                      <li>Generate API Keys and Access Tokens</li>
                    </ul>
                  )}
                  {activeTab === 'reddit' && (
                    <ul>
                      <li>Go to <a href="https://www.reddit.com/prefs/apps" target="_blank" rel="noopener noreferrer">Reddit App Preferences</a></li>
                      <li>Create a "script" type application</li>
                      <li>Use your Reddit account credentials</li>
                    </ul>
                  )}
                  {activeTab === 'telegram' && (
                    <ul>
                      <li>Message <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer">@BotFather</a> on Telegram</li>
                      <li>Create a new bot with /newbot command</li>
                      <li>Get your Channel ID (start with @ or numeric ID)</li>
                    </ul>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConnectionsPage

