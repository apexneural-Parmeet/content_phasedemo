import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from '../components/Logo'
import { FacebookIcon, InstagramIcon, TwitterIcon, RedditIcon } from '../components/SocialIcons'
import './LandingPage.css'

function LandingPage() {
  const navigate = useNavigate()
  const [currentFeature, setCurrentFeature] = useState(0)

  const features = [
    "Schedule posts across all platforms",
    "Manage multiple social media accounts",
    "Post to Facebook, Instagram, Twitter & Reddit",
    "Calendar view for better planning",
    "AI-powered content management"
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleGetStarted = () => {
    navigate('/home')
  }

  return (
    <div className="landing-page">
      <div className="landing-container">
        {/* Hero Section - Full Screen */}
        <section className="hero-section">
          <div className="logo-animation">
            <Logo size={100} />
          </div>
          
          <h1 className="hero-title">
            Social Media
            <span className="gradient-text"> AI Manager</span>
          </h1>
          
          <p className="hero-subtitle">
            Manage all your social media platforms from one beautiful place
          </p>

          {/* Animated Features */}
          <div className="animated-feature">
            <span className="feature-icon">✨</span>
            <span className="feature-text" key={currentFeature}>
              {features[currentFeature]}
            </span>
          </div>

          {/* Platform Icons */}
          <div className="platform-showcase">
            <div className="platform-icon-wrapper facebook">
              <FacebookIcon size={28} color="#c0c0c0" />
            </div>
            <div className="platform-icon-wrapper instagram">
              <InstagramIcon size={28} color="#c0c0c0" />
            </div>
            <div className="platform-icon-wrapper twitter">
              <TwitterIcon size={28} color="#c0c0c0" />
            </div>
            <div className="platform-icon-wrapper reddit">
              <RedditIcon size={28} color="#c0c0c0" />
            </div>
          </div>

          {/* CTA Button */}
          <button className="cta-button" onClick={handleGetStarted}>
            <span className="cta-text">Let's Go</span>
            <span className="cta-arrow">→</span>
          </button>

          {/* Footer */}
          <footer className="landing-footer">
            <p>Made with ❤️ for creators and social media managers</p>
          </footer>
        </section>
      </div>
    </div>
  )
}

export default LandingPage

