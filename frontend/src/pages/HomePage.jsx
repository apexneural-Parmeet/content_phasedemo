import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { FacebookIcon, InstagramIcon, TwitterIcon, RedditIcon } from '../components/SocialIcons'
import { useGeneratedContent } from '../context/GeneratedContentContext'
import downloadImg from '../assets/rename.jpg'
import './HomePage.css'

function HomePage() {
  const location = useLocation()
  const { generatedData } = useGeneratedContent()
  
  const [caption, setCaption] = useState(location.state?.prefillCaption || '')
  const [photo, setPhoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [selected, setSelected] = useState({
    facebook: true,
    instagram: true,
    twitter: true,
    reddit: true
  })
  const [platformStatus, setPlatformStatus] = useState({
    facebook: { connected: false, loading: true },
    instagram: { connected: false, loading: true },
    twitter: { connected: false, loading: true },
    reddit: { connected: false, loading: true }
  })
  const [scheduleEnabled, setScheduleEnabled] = useState(false)
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledHour, setScheduledHour] = useState('')
  const [scheduledMinute, setScheduledMinute] = useState('')

  useEffect(() => {
    checkPlatformConnections()
  }, [])

  // Handle prefilled image from generator
  useEffect(() => {
    if (location.state?.prefillImage) {
      const imagePath = location.state.prefillImage
      setPreview(`http://localhost:8000${imagePath}`)
      
      // Fetch the image and convert it to a File object
      fetch(`http://localhost:8000${imagePath}`)
        .then(res => res.blob())
        .then(blob => {
          const filename = imagePath.split('/').pop()
          const file = new File([blob], filename, { type: 'image/png' })
          setPhoto(file)
        })
        .catch(err => console.error('Failed to load image:', err))
    }
  }, [location.state])

  // Show info if there's generated content available
  useEffect(() => {
    if (generatedData && !location.state?.prefillCaption) {
      setMessage({ 
        type: 'info', 
        text: '💡 You have generated content. Go to Generate page to review and publish it!' 
      })
      setTimeout(() => setMessage(null), 5000)
    }
  }, [generatedData, location.state])

  const checkPlatformConnections = async () => {
    try {
      const response = await fetch('/api/verify-token')
      const data = await response.json()
      
      setPlatformStatus({
        facebook: { connected: data.facebook?.valid || false, loading: false },
        instagram: { connected: data.instagram?.valid || false, loading: false },
        twitter: { connected: data.twitter?.valid || false, loading: false },
        reddit: { connected: data.reddit?.valid || false, loading: false }
      })
    } catch (error) {
      setPlatformStatus({
        facebook: { connected: false, loading: false },
        instagram: { connected: false, loading: false },
        twitter: { connected: false, loading: false },
        reddit: { connected: false, loading: false }
      })
    }
  }

  const togglePlatform = (key) => {
    setSelected((s) => ({ ...s, [key]: !s[key] }))
  }

  const handlePhotoChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setPhoto(file)
      
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleRemoveImage = () => {
    setPhoto(null)
    setPreview(null)
    document.getElementById('photo-input').value = ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!photo) {
      setMessage({ type: 'error', text: '❌ Please select a photo' })
      return
    }

    if (scheduleEnabled && (!scheduledDate || !scheduledHour || !scheduledMinute)) {
      setMessage({ type: 'error', text: '❌ Please select date, hour, and minute for scheduling' })
      return
    }

    setIsLoading(true)
    setMessage(null)

    const formData = new FormData()
    formData.append('photo', photo)
    formData.append('caption', caption)
    formData.append('platforms', JSON.stringify(selected))

    if (scheduleEnabled && scheduledDate && scheduledHour && scheduledMinute) {
      const scheduledDateTime = `${scheduledDate}T${scheduledHour}:${scheduledMinute}:00`
      formData.append('scheduled_time', scheduledDateTime)
    }

    try {
      const response = await fetch('/api/post', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: `🎉 ${data.message}` })
        setCaption('')
        setPhoto(null)
        setPreview(null)
        setScheduledDate('')
        setScheduledHour('')
        setScheduledMinute('')
        setScheduleEnabled(false)
        document.getElementById('photo-input').value = ''
        
        setTimeout(() => setMessage(null), 5000)
      } else {
        setMessage({ type: 'error', text: `❌ ${data.detail || 'Failed to post'}` })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `❌ Network error: ${error.message}` })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="card">
          <div className="platform-select">
            <label className="platform-select-item">
              <input type="checkbox" checked={selected.facebook} onChange={() => togglePlatform('facebook')} />
              <span>Facebook</span>
            </label>
            <label className="platform-select-item">
              <input type="checkbox" checked={selected.instagram} onChange={() => togglePlatform('instagram')} />
              <span>Instagram</span>
            </label>
            <label className="platform-select-item">
              <input type="checkbox" checked={selected.twitter} onChange={() => togglePlatform('twitter')} />
              <span>Twitter</span>
            </label>
            <label className="platform-select-item">
              <input type="checkbox" checked={selected.reddit} onChange={() => togglePlatform('reddit')} />
              <span>Reddit</span>
            </label>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="caption">Content</label>
              <textarea
                id="caption"
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                rows="4"
                placeholder="Write what your heart says..."
                required
              />
              <span className="char-count">{caption.length} character{caption.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="form-group">
              <label htmlFor="photo-input">Photo</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="photo-input"
                  accept="image/jpeg,image/png,image/gif,image/jpg"
                  onChange={handlePhotoChange}
                  required
                />
                <div className="file-input-display">
                  <img src={downloadImg} alt="upload" className="file-icon-img" />
                  <span className="file-text">
                    {photo ? photo.name : 'Drop your Image here '}
                  </span>
                </div>
              </div>
              <small className="help-text">Supported formats: JPEG, PNG, GIF (Max 10MB)</small>
            </div>

            {preview && (
              <div className="image-preview">
                <img src={preview} alt="Preview" />
                <button type="button" onClick={handleRemoveImage} className="remove-btn">
                  ✕
                </button>
              </div>
            )}

            <div className="scheduler-section">
              <div className="scheduler-toggle">
                <label className="toggle-label">
                  <input 
                    type="checkbox" 
                    checked={scheduleEnabled} 
                    onChange={(e) => setScheduleEnabled(e.target.checked)}
                    className="toggle-checkbox"
                  />
                  <span className="toggle-switch"></span>
                  <span className="toggle-text">
                    {scheduleEnabled ? '📅 Schedule Post' : '⚡ Post Now'}
                  </span>
                </label>
              </div>

              {scheduleEnabled && (
                <div className="schedule-inputs">
                  <div className="schedule-row">
                    <div className="schedule-field">
                      <label htmlFor="scheduled-date">📆 Date</label>
                      <input
                        type="date"
                        id="scheduled-date"
                        value={scheduledDate}
                        onChange={(e) => setScheduledDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        required={scheduleEnabled}
                        className="date-input"
                      />
                    </div>
                    <div className="schedule-field">
                      <label htmlFor="scheduled-hour">🕐 Hour (24h)</label>
                      <select
                        id="scheduled-hour"
                        value={scheduledHour}
                        onChange={(e) => setScheduledHour(e.target.value)}
                        required={scheduleEnabled}
                        className="time-select"
                      >
                        <option value="">Hour</option>
                        <option value="00">00</option>
                        <option value="01">01</option>
                        <option value="02">02</option>
                        <option value="03">03</option>
                        <option value="04">04</option>
                        <option value="05">05</option>
                        <option value="06">06</option>
                        <option value="07">07</option>
                        <option value="08">08</option>
                        <option value="09">09</option>
                        <option value="10">10</option>
                        <option value="11">11</option>
                        <option value="12">12</option>
                        <option value="13">13</option>
                        <option value="14">14</option>
                        <option value="15">15</option>
                        <option value="16">16</option>
                        <option value="17">17</option>
                        <option value="18">18</option>
                        <option value="19">19</option>
                        <option value="20">20</option>
                        <option value="21">21</option>
                        <option value="22">22</option>
                        <option value="23">23</option>
                      </select>
                    </div>
                    <div className="schedule-field">
                      <label htmlFor="scheduled-minute">⏱️ Minute</label>
                      <select
                        id="scheduled-minute"
                        value={scheduledMinute}
                        onChange={(e) => setScheduledMinute(e.target.value)}
                        required={scheduleEnabled}
                        className="time-select"
                      >
                        <option value="">Min</option>
                        {Array.from({ length: 60 }, (_, i) => {
                          const min = i.toString().padStart(2, '0')
                          return <option key={min} value={min}>{min}</option>
                        })}
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
              {isLoading ? (
                <span className="btn-loading">
                  <span className="spinner"></span> {scheduleEnabled ? 'Scheduling...' : 'Posting to all platforms...'}
                </span>
              ) : (
                <span className="btn-text">
                  {scheduleEnabled ? '📅 Schedule Post' : '🚀 Post to All Platforms'}
                </span>
              )}
            </button>
          </form>

          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}
        </div>

        <footer className="footer">
          <p>© 2025 Social Hub. Made with ❤️ for creators</p>
        </footer>
      </div>
    </div>
  )
}

export default HomePage

