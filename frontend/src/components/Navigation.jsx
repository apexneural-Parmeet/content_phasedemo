import { useState, useEffect, useRef } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Logo from './Logo'
import { FacebookIcon, InstagramIcon, TwitterIcon, RedditIcon } from './SocialIcons'
import './Navigation.css'

function Navigation() {
  const location = useLocation()
  const navigate = useNavigate()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef(null)
  const [platformStatus, setPlatformStatus] = useState({
    facebook: { connected: false, loading: true },
    instagram: { connected: false, loading: true },
    twitter: { connected: false, loading: true },
    reddit: { connected: false, loading: true }
  })

  useEffect(() => {
    checkPlatformConnections()
  }, [])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const checkPlatformConnections = async () => {
    try {
      const response = await fetch('/api/credentials/status')
      const data = await response.json()
      
      if (data.success && data.status) {
        setPlatformStatus({
          facebook: { connected: data.status.facebook?.connected || false, loading: false },
          instagram: { connected: data.status.instagram?.connected || false, loading: false },
          twitter: { connected: data.status.twitter?.connected || false, loading: false },
          reddit: { connected: data.status.reddit?.connected || false, loading: false }
        })
      } else {
        throw new Error('Failed to fetch status')
      }
    } catch (error) {
      setPlatformStatus({
        facebook: { connected: false, loading: false },
        instagram: { connected: false, loading: false },
        twitter: { connected: false, loading: false },
        reddit: { connected: false, loading: false }
      })
    }
  }

  return (
    <nav className="navigation">
      <div className="nav-container">
        {/* Logo Section - YouTube Style */}
        <div className="nav-left">
          <Link to="/" className="logo-link">
            <Logo size={32} />
            <span className="brand-name">Social Hub</span>
          </Link>
          
          {/* Platform Status Icons */}
          <div className="nav-platform-status">
            <div className={`platform-dot ${platformStatus.facebook.connected ? 'connected' : 'disconnected'}`} title={platformStatus.facebook.connected ? 'Facebook Connected' : 'Facebook Disconnected'}>
              <FacebookIcon size={16} />
            </div>
            <div className={`platform-dot ${platformStatus.instagram.connected ? 'connected' : 'disconnected'}`} title={platformStatus.instagram.connected ? 'Instagram Connected' : 'Instagram Disconnected'}>
              <InstagramIcon size={16} />
            </div>
            <div className={`platform-dot ${platformStatus.twitter.connected ? 'connected' : 'disconnected'}`} title={platformStatus.twitter.connected ? 'Twitter Connected' : 'Twitter Disconnected'}>
              <TwitterIcon size={16} />
            </div>
            <div className={`platform-dot ${platformStatus.reddit.connected ? 'connected' : 'disconnected'}`} title={platformStatus.reddit.connected ? 'Reddit Connected' : 'Reddit Disconnected'}>
              <RedditIcon size={16} />
            </div>
          </div>
        </div>

        {/* Right Section - Navigation Links + User Menu */}
        <div className="nav-right">
          <Link 
            to="/generate" 
            className={`nav-link ${location.pathname === '/generate' ? 'active' : ''}`}
          >
            <span>Generate</span>
          </Link>
          <Link 
            to="/home" 
            className={`nav-link ${location.pathname === '/home' ? 'active' : ''}`}
          >
            <span>Create</span>
          </Link>
          <Link 
            to="/scheduler" 
            className={`nav-link ${location.pathname === '/scheduler' ? 'active' : ''}`}
          >
            <span>Schedule</span>
          </Link>
          <Link 
            to="/connections" 
            className={`nav-link ${location.pathname === '/connections' ? 'active' : ''}`}
          >
            <span>Connections</span>
          </Link>
          
          <div className="user-section" ref={dropdownRef}>
            <div 
              className="user-avatar" 
              onClick={() => setShowDropdown(!showDropdown)}
            >
              👤
            </div>
            
            {/* Dropdown Menu */}
            {showDropdown && (
              <div className="dropdown-menu">
                <div className="dropdown-header">
                  Quick Actions
                </div>
                <Link 
                  to="/generate" 
                  className="dropdown-item"
                  onClick={() => setShowDropdown(false)}
                >
                  <span className="dropdown-icon">🤖</span>
                  Generate Content
                </Link>
                <Link 
                  to="/home" 
                  className="dropdown-item"
                  onClick={() => setShowDropdown(false)}
                >
                  <span className="dropdown-icon">✏️</span>
                  Create Post
                </Link>
                <Link 
                  to="/scheduler" 
                  className="dropdown-item"
                  onClick={() => setShowDropdown(false)}
                >
                  <span className="dropdown-icon">📅</span>
                  View Schedule
                </Link>
                <Link 
                  to="/connections" 
                  className="dropdown-item"
                  onClick={() => setShowDropdown(false)}
                >
                  <span className="dropdown-icon">🔗</span>
                  Platform Connections
                </Link>
                <div className="dropdown-divider"></div>
                <div className="dropdown-item info">
                  Platform Status
                </div>
                <div className="dropdown-platforms">
                  <div className="dropdown-platform">
                    <FacebookIcon size={14} />
                    <span>{platformStatus.facebook.connected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                  <div className="dropdown-platform">
                    <InstagramIcon size={14} />
                    <span>{platformStatus.instagram.connected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                  <div className="dropdown-platform">
                    <TwitterIcon size={14} />
                    <span>{platformStatus.twitter.connected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                  <div className="dropdown-platform">
                    <RedditIcon size={14} />
                    <span>{platformStatus.reddit.connected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation

