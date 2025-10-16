import { useState, useEffect } from 'react'
import './SchedulerPage.css'

function SchedulerPage() {
  const [scheduledPosts, setScheduledPosts] = useState([])
  const [viewMode, setViewMode] = useState('calendar') // 'calendar' or 'list'
  const [message, setMessage] = useState(null)
  const [currentDate, setCurrentDate] = useState(new Date())

  useEffect(() => {
    fetchScheduledPosts()
    // Poll every 10 seconds to catch new scheduled posts quickly
    const interval = setInterval(fetchScheduledPosts, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchScheduledPosts = async () => {
    try {
      const response = await fetch('/api/scheduled-posts')
      const data = await response.json()
      setScheduledPosts(data.scheduled_posts || [])
    } catch (error) {
      console.error('Failed to fetch scheduled posts:', error)
    }
  }

  const deleteScheduledPost = async (postId) => {
    try {
      const response = await fetch(`/api/scheduled-posts/${postId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Scheduled post deleted successfully' })
        fetchScheduledPosts()
        setTimeout(() => setMessage(null), 3000)
      } else {
        setMessage({ type: 'error', text: 'Failed to delete scheduled post' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    }
  }

  // Calendar helper functions
  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()
    
    return { daysInMonth, startingDayOfWeek, year, month }
  }

  const getPostsForDate = (day) => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    
    return scheduledPosts.filter(post => {
      const postDate = new Date(post.scheduled_time).toISOString().split('T')[0]
      return postDate === dateStr
    })
  }

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const renderCalendarView = () => {
    const { daysInMonth, startingDayOfWeek, year, month } = getDaysInMonth(currentDate)
    const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    const days = []

    // Add empty cells for days before the month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>)
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const postsForDay = getPostsForDate(day)
      const isToday = new Date().toDateString() === new Date(year, month, day).toDateString()
      
      days.push(
        <div key={day} className={`calendar-day ${isToday ? 'today' : ''} ${postsForDay.length > 0 ? 'has-posts' : ''}`}>
          <div className="day-number">{day}</div>
          {postsForDay.length > 0 && (
            <div className="day-posts">
              {postsForDay.map((post) => (
                <div 
                  key={post.id} 
                  className={`calendar-post-indicator ${post.status === 'posted' ? 'posted' : 'scheduled'}`} 
                  title={`${post.status === 'posted' ? 'Posted' : 'Scheduled'}: ${post.caption.substring(0, 50)}`}
                >
                  <span className="post-time">{formatTime(post.scheduled_time)}</span>
                  {post.status === 'posted' && <span className="posted-badge">Posted</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }

    return (
      <div className="calendar-container">
        <div className="calendar-header">
          <button onClick={previousMonth} className="calendar-nav-btn">‹</button>
          <h2 className="calendar-month">{monthName}</h2>
          <button onClick={nextMonth} className="calendar-nav-btn">›</button>
        </div>
        <div className="calendar-weekdays">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>
        <div className="calendar-grid">
          {days}
        </div>
      </div>
    )
  }

  const renderListView = () => {
    if (scheduledPosts.length === 0) {
      return (
        <div className="empty-state">
          <p className="empty-text">No scheduled posts</p>
          <p className="empty-hint">Schedule your first post to see it here</p>
        </div>
      )
    }

    // Sort posts by scheduled time
    const sortedPosts = [...scheduledPosts].sort((a, b) => 
      new Date(a.scheduled_time) - new Date(b.scheduled_time)
    )

    return (
      <div className="list-container">
        {sortedPosts.map((post) => {
          const platforms = Object.entries(post.platforms)
            .filter(([_, enabled]) => enabled)
            .map(([platform]) => platform)
            .join(', ')
          
          const isPosted = post.status === 'posted'
          
          return (
            <div key={post.id} className={`list-post-item ${isPosted ? 'posted' : 'scheduled'}`}>
              <div className="list-post-header">
                <div className="list-post-date">
                  <span className={`status-badge ${isPosted ? 'posted' : 'scheduled'}`}>
                    {isPosted ? 'Posted' : 'Scheduled'}
                  </span>
                  <span className="date-badge">{formatDate(post.scheduled_time)}</span>
                  <span className="time-badge">{formatTime(post.scheduled_time)}</span>
                </div>
                {!isPosted && (
                  <button 
                    onClick={() => deleteScheduledPost(post.id)}
                    className="delete-btn"
                    title="Delete scheduled post"
                  >
                    ✕
                  </button>
                )}
              </div>
              <p className="list-post-caption">
                {post.caption.length > 150 
                  ? `${post.caption.substring(0, 150)}...` 
                  : post.caption}
              </p>
              <div className="list-post-platforms">
                <span className="platforms-label">Platforms:</span>
                <span className="platforms-value">{platforms}</span>
                {isPosted && post.posted_to !== undefined && (
                  <span className="posted-count">({post.posted_to} posted{post.failed_platforms?.length > 0 ? `, ${post.failed_platforms.length} failed` : ''})</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="scheduler-page">
      <div className="scheduler-container">
        <div className="scheduler-header">
          <div className="header-content">
            <h1 className="scheduler-title">Scheduled Posts</h1>
            <p className="scheduler-subtitle">
              {scheduledPosts.length} {scheduledPosts.length === 1 ? 'post' : 'posts'} scheduled
            </p>
          </div>
          <div className="view-toggle">
            <button
              className={`toggle-btn ${viewMode === 'calendar' ? 'active' : ''}`}
              onClick={() => setViewMode('calendar')}
            >
              Calendar
            </button>
            <button
              className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
          </div>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="scheduler-content">
          {viewMode === 'calendar' ? renderCalendarView() : renderListView()}
        </div>
      </div>
    </div>
  )
}

export default SchedulerPage

