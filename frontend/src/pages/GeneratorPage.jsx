import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FacebookIcon, InstagramIcon, TwitterIcon, RedditIcon } from '../components/SocialIcons'
import { useGeneratedContent } from '../context/GeneratedContentContext'
import './GeneratorPage.css'

function GeneratorPage() {
  const navigate = useNavigate()
  const { generatedData, saveGeneratedContent } = useGeneratedContent()
  
  const [prompt, setPrompt] = useState('')
  const [tone, setTone] = useState('casual')
  const [imageStyle, setImageStyle] = useState('realistic')
  const [imageProvider, setImageProvider] = useState('nano-banana')  // Default to Nano Banana for speed
  const [usePromptEnhancer, setUsePromptEnhancer] = useState(false)  // Disabled by default
  const [isGenerating, setIsGenerating] = useState(false)
  const [enhancedPrompts, setEnhancedPrompts] = useState(null)
  const [generatedContent, setGeneratedContent] = useState(null)
  const [editedContent, setEditedContent] = useState({})
  const [approvalStatus, setApprovalStatus] = useState({})
  const [generatedImage, setGeneratedImage] = useState(null)
  const [imageApprovalStatus, setImageApprovalStatus] = useState(null)
  const [isRegeneratingImage, setIsRegeneratingImage] = useState(false)
  const [showProviderModal, setShowProviderModal] = useState(false)
  const [message, setMessage] = useState(null)
  const [regeneratingPlatform, setRegeneratingPlatform] = useState(null)
  const [originalTopic, setOriginalTopic] = useState('')
  const [originalTone, setOriginalTone] = useState('casual')
  const [isPublishing, setIsPublishing] = useState(false)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledHour, setScheduledHour] = useState('')
  const [scheduledMinute, setScheduledMinute] = useState('')

  // Restore from context on mount
  useEffect(() => {
    if (generatedData) {
      setGeneratedContent(generatedData.content)
      setEditedContent(generatedData.content)
      setGeneratedImage(generatedData.image)
      setOriginalTopic(generatedData.topic)
      setOriginalTone(generatedData.tone)
      if (generatedData.imageStyle) {
        setImageStyle(generatedData.imageStyle)
      }
    }
  }, [])

  const tones = [
    { value: 'casual', label: 'Casual', description: 'Friendly and relaxed' },
    { value: 'professional', label: 'Professional', description: 'Business-like and formal' },
    { value: 'corporate', label: 'Corporate Minimal', description: 'Clean & minimal text' },
    { value: 'funny', label: 'Funny', description: 'Humorous and hilarious' },
    { value: 'inspirational', label: 'Inspirational', description: 'Motivational and uplifting' },
    { value: 'educational', label: 'Educational', description: 'Informative and teaching' },
    { value: 'storytelling', label: 'Storytelling', description: 'Narrative and engaging' },
    { value: 'promotional', label: 'Promotional', description: 'Sales-focused' }
  ]

  const imageStyles = [
    { value: 'realistic', label: 'Realistic', description: 'Photo-realistic' },
    { value: 'minimal', label: 'Minimal Clean', description: 'Ultra-clean & simple' },
    { value: 'anime', label: 'Anime', description: 'Japanese anime style' },
    { value: '2d', label: '2D Art', description: 'Flat illustration' },
    { value: 'comics', label: 'Comic Book', description: 'Comic art style' },
    { value: 'sketch', label: 'Sketch', description: 'Hand-drawn' },
    { value: 'vintage', label: 'Vintage', description: 'Retro look' },
    { value: 'disney', label: 'Disney', description: 'Disney animation' }
  ]

  const handleGenerate = async (e) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      setMessage({ type: 'error', text: 'Please enter a topic or prompt' })
      return
    }

    setIsGenerating(true)
    setMessage(null)

    try {
      const response = await fetch('/api/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: prompt,
          tone: tone,
          image_style: imageStyle,
          generate_image: true,
          use_prompt_enhancer: usePromptEnhancer,
          image_provider: imageProvider
        })
      })

      const data = await response.json()

      if (response.ok) {
        setGeneratedContent(data.platforms)
        setEditedContent(data.platforms)
        setGeneratedImage(data.image)
        setImageApprovalStatus(null)
        setOriginalTopic(prompt)
        setOriginalTone(tone)
        setApprovalStatus({})
        setEnhancedPrompts(data.enhanced_prompts)  // Store enhanced prompts if available
        
        // Save to context for persistence
        saveGeneratedContent(data.platforms, data.image, prompt, tone, imageStyle)
        
        const enhancedMsg = data.enhanced_prompts?.enhanced 
          ? 'Prompt enhanced & content generated!' 
          : 'Content and image generated!';
        setMessage({ type: 'success', text: enhancedMsg })
        setTimeout(() => setMessage(null), 3000)
      } else {
        setMessage({ type: 'error', text: `${data.detail || 'Failed to generate content'}` })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleEditContent = (platform, newContent) => {
    setEditedContent(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        content: newContent
      }
    }))
  }

  const handleApprove = (platform) => {
    setApprovalStatus(prev => ({ ...prev, [platform]: 'approved' }))
    setMessage({ type: 'success', text: `${platformNames[platform]} content approved!` })
    setTimeout(() => setMessage(null), 2000)
  }

  const handleReject = (platform) => {
    setApprovalStatus(prev => ({ ...prev, [platform]: 'rejected' }))
    setMessage({ type: 'error', text: `${platformNames[platform]} content rejected` })
    setTimeout(() => setMessage(null), 2000)
  }

  const handleRegenerate = async (platform) => {
    setRegeneratingPlatform(platform)
    setApprovalStatus(prev => ({ ...prev, [platform]: null }))

    try {
      const response = await fetch('/api/regenerate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: originalTopic,
          platform: platform,
          tone: originalTone,
          previous_content: editedContent[platform]?.content || ''
        })
      })

      const data = await response.json()

      if (response.ok) {
        setEditedContent(prev => ({
          ...prev,
          [platform]: {
            content: data.content,
            success: true,
            character_count: data.character_count
          }
        }))
        setMessage({ type: 'success', text: `New ${platformNames[platform]} content generated!` })
        setTimeout(() => setMessage(null), 2000)
      } else {
        setMessage({ type: 'error', text: `Failed to regenerate` })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setRegeneratingPlatform(null)
    }
  }

  const handleApproveImage = () => {
    setImageApprovalStatus('approved')
    setMessage({ type: 'success', text: 'Image approved!' })
    setTimeout(() => setMessage(null), 2000)
  }

  const handleRejectImage = () => {
    setImageApprovalStatus('rejected')
    setMessage({ type: 'error', text: 'Image rejected' })
    setTimeout(() => setMessage(null), 2000)
  }

  const handleRegenerateImage = async () => {
    // Show provider selection modal
    setShowProviderModal(true)
  }

  const handleRegenerateWithProvider = async (selectedProvider) => {
    setShowProviderModal(false)
    setIsRegeneratingImage(true)
    setImageApprovalStatus(null)

    try {
      const response = await fetch('/api/regenerate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: originalTopic,
          tone: originalTone,
          image_style: imageStyle,
          image_provider: selectedProvider
        })
      })

      const data = await response.json()

      if (response.ok) {
        setGeneratedImage(data)
        setImageProvider(selectedProvider)  // Update current provider
        const providerName = selectedProvider === 'nano-banana' ? 'Nano Banana' : 'DALL-E 3'
        setMessage({ type: 'success', text: `New image generated with ${providerName}!` })
        setTimeout(() => setMessage(null), 2000)
      } else {
        setMessage({ type: 'error', text: 'Failed to regenerate image' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setIsRegeneratingImage(false)
    }
  }

  const handlePublishToAll = async (scheduled = false) => {
    // Get all approved platforms
    const approvedPlatforms = Object.keys(approvalStatus).filter(
      platform => approvalStatus[platform] === 'approved'
    )

    if (approvedPlatforms.length === 0) {
      setMessage({ type: 'error', text: 'Please approve at least one platform' })
      return
    }

    if (!imageApprovalStatus && generatedImage?.success) {
      setMessage({ type: 'error', text: 'Please approve the image first' })
      return
    }

    // Validate schedule if scheduling
    if (scheduled && (!scheduledDate || !scheduledHour || !scheduledMinute)) {
      setMessage({ type: 'error', text: 'Please select date, hour, and minute for scheduling' })
      return
    }

    setIsPublishing(true)
    setMessage(null)

    try {
      // Download the AI-generated image
      const imageResponse = await fetch(`http://localhost:8000${generatedImage.web_path}`)
      if (!imageResponse.ok) {
        throw new Error('Failed to download AI-generated image')
      }
      const imageBlob = await imageResponse.blob()
      const imageFile = new File([imageBlob], generatedImage.filename, { type: 'image/png' })

      let successCount = 0
      let failedPlatforms = []

      // Post to each approved platform
      for (const platform of approvedPlatforms) {
        try {
          const formData = new FormData()
          formData.append('photo', imageFile)
          formData.append('caption', editedContent[platform]?.content || '')
          
          // Create platform selection (only this platform)
          const platformSelection = {
            facebook: platform === 'facebook',
            instagram: platform === 'instagram',
            twitter: platform === 'twitter',
            reddit: platform === 'reddit'
          }
          formData.append('platforms', JSON.stringify(platformSelection))

          // Add schedule time if scheduling
          if (scheduled) {
            const scheduledDateTime = `${scheduledDate}T${scheduledHour}:${scheduledMinute}:00`
            formData.append('scheduled_time', scheduledDateTime)
          }

          const response = await fetch('http://localhost:8000/api/post', {
            method: 'POST',
            body: formData
          })

          if (response.ok) {
            successCount++
            console.log(`✅ Successfully posted to ${platform}`)
          } else {
            const error = await response.json()
            failedPlatforms.push(platform)
            console.error(`Failed to post to ${platform}:`, error)
          }
        } catch (err) {
          failedPlatforms.push(platform)
          console.error(`Error posting to ${platform}:`, err)
        }
      }

      // Show result message
      if (successCount > 0) {
        if (scheduled) {
          setMessage({ 
            type: 'success', 
            text: `Scheduled to ${successCount} platform${successCount > 1 ? 's' : ''}!${failedPlatforms.length > 0 ? ` Failed: ${failedPlatforms.join(', ')}` : ''}` 
          })
          setShowScheduleModal(false)
        } else {
          setMessage({ 
            type: 'success', 
            text: `Posted to ${successCount} platform${successCount > 1 ? 's' : ''}!${failedPlatforms.length > 0 ? ` Failed: ${failedPlatforms.join(', ')}` : ''}` 
          })
        }
      } else {
        setMessage({ 
          type: 'error', 
          text: `Failed to post to all platforms. Check console for details.` 
        })
      }
      
      setTimeout(() => setMessage(null), 5000)
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
      console.error('Publish error:', error)
    } finally {
      setIsPublishing(false)
    }
  }

  const handleUseContent = (platform) => {
    if (!approvalStatus[platform]) {
      setMessage({ type: 'error', text: 'Please approve the content first' })
      return
    }

    if (!imageApprovalStatus && generatedImage?.success) {
      setMessage({ type: 'error', text: 'Please approve the image first' })
      return
    }
    
    // Navigate to create page with pre-filled content and image
    const content = editedContent[platform]?.content || ''
    const imagePath = generatedImage?.web_path || null
    navigate('/home', { 
      state: { 
        prefillCaption: content,
        prefillImage: imagePath
      } 
    })
  }

  const platformIcons = {
    facebook: <FacebookIcon size={24} />,
    instagram: <InstagramIcon size={24} />,
    twitter: <TwitterIcon size={24} />,
    reddit: <RedditIcon size={24} />
  }

  const platformNames = {
    facebook: 'Facebook',
    instagram: 'Instagram',
    twitter: 'Twitter',
    reddit: 'Reddit'
  }

  const platformColors = {
    facebook: '#1877F2',
    instagram: '#E4405F',
    twitter: '#1DA1F2',
    reddit: '#FF4500'
  }

  return (
    <div className="generator-page">
      <div className="generator-container">
        {/* Header */}
        <div className="generator-header">
          <h1 className="generator-title">AI Content Generator</h1>
          <p className="generator-subtitle">Generate engaging content for all platforms at once</p>
        </div>

        {/* Input Section */}
        <div className="generator-input-card">
          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label htmlFor="prompt">What do you want to post about?</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Example: A new product launch, a motivational quote, a behind-the-scenes moment..."
                rows="3"
                required
                className="prompt-input"
              />
            </div>

            <div className="form-group">
              <label>Content Tone & Personality</label>
              <div className="tone-grid">
                {tones.map(t => (
                  <div
                    key={t.value}
                    className={`tone-card ${tone === t.value ? 'selected' : ''}`}
                    onClick={() => setTone(t.value)}
                  >
                    <div className="card-label">{t.label}</div>
                    <div className="card-description">{t.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Image Style</label>
              <div className="style-grid">
                {imageStyles.map(s => (
                  <div
                    key={s.value}
                    className={`style-card ${imageStyle === s.value ? 'selected' : ''}`}
                    onClick={() => setImageStyle(s.value)}
                  >
                    <div className="card-label">{s.label}</div>
                    <div className="card-description">{s.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Image Generator</label>
              <div className="provider-grid">
                <div
                  className={`provider-card ${imageProvider === 'nano-banana' ? 'selected' : ''}`}
                  onClick={() => setImageProvider('nano-banana')}
                >
                  <div className="provider-icon">🍌</div>
                  <div className="provider-info">
                    <div className="provider-name">Nano Banana</div>
                    <div className="provider-speed">Ultra Fast • 2-3s</div>
                    <div className="provider-desc">Fal.ai - Best for quick iterations</div>
                  </div>
                </div>
                
                <div
                  className={`provider-card ${imageProvider === 'dalle' ? 'selected' : ''}`}
                  onClick={() => setImageProvider('dalle')}
                >
                  <div className="provider-icon">🎨</div>
                  <div className="provider-info">
                    <div className="provider-name">DALL-E 3</div>
                    <div className="provider-speed">Standard • 15-20s</div>
                    <div className="provider-desc">OpenAI - Premium quality</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-group enhancer-toggle">
              <label className="enhancer-label">
                <input
                  type="checkbox"
                  checked={usePromptEnhancer}
                  onChange={(e) => setUsePromptEnhancer(e.target.checked)}
                  className="enhancer-checkbox"
                />
                <span className="enhancer-text">
                  AI Prompt Enhancer (Optional)
                  <small className="enhancer-description">
                    Automatically improve your prompt - works best with simple topics
                  </small>
                </span>
              </label>
            </div>

            <button type="submit" className="generate-btn" disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                'Generate Content'
              )}
            </button>
          </form>

          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}
        </div>

        {/* Enhanced Prompts Display */}
        {enhancedPrompts && enhancedPrompts.enhanced && (
          <div className="enhanced-prompts-card">
            <div className="enhanced-header">
              <h3>AI-Enhanced Prompts Used</h3>
              <button 
                onClick={() => setEnhancedPrompts(null)} 
                className="close-enhanced"
              >
                ✕
              </button>
            </div>
            <div className="enhanced-content">
              <div className="enhanced-item">
                <label>Content Prompt:</label>
                <p>{enhancedPrompts.content_prompt}</p>
              </div>
              <div className="enhanced-item">
                <label>Image Prompt:</label>
                <p>{enhancedPrompts.image_prompt}</p>
              </div>
              <div className="enhanced-original">
                <small>Original: "{enhancedPrompts.original_prompt}"</small>
              </div>
            </div>
          </div>
        )}

        {/* Generated Image Preview */}
        {generatedImage && generatedImage.success && (
          <div className="image-preview-section">
            <div className="image-section-header">
              <div>
                <h2 className="preview-title">AI-Generated Image</h2>
                <p className="preview-subtitle">Review and approve the generated image</p>
              </div>
              
              {/* Image Approval Buttons */}
              <div className="image-actions">
                {imageApprovalStatus && (
                  <div className={`approval-badge ${imageApprovalStatus}`}>
                    {imageApprovalStatus === 'approved' && 'Image Approved'}
                    {imageApprovalStatus === 'rejected' && 'Image Rejected'}
                  </div>
                )}
                <div className="action-buttons">
                  <button
                    onClick={handleApproveImage}
                    className={`action-btn approve ${imageApprovalStatus === 'approved' ? 'active' : ''}`}
                    title="Approve image"
                    disabled={imageApprovalStatus === 'approved'}
                  >
                    ✓
                  </button>
                  <button
                    onClick={handleRejectImage}
                    className={`action-btn reject ${imageApprovalStatus === 'rejected' ? 'active' : ''}`}
                    title="Reject image"
                  >
                    ✗
                  </button>
                  <button
                    onClick={handleRegenerateImage}
                    className="action-btn regenerate"
                    title="Regenerate new image"
                    disabled={isRegeneratingImage}
                  >
                    {isRegeneratingImage ? '⏳' : '🔄'}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="ai-image-container">
              <img 
                src={`http://localhost:8000${generatedImage.web_path}`} 
                alt="AI Generated" 
                className="ai-generated-image"
              />
            </div>
          </div>
        )}

        {/* Generated Content Preview */}
        {generatedContent && (
          <div className="content-preview-section">
            <h2 className="preview-title">Generated Content - Review & Approve</h2>
            <p className="preview-subtitle">Review each platform's content and approve, reject, or regenerate</p>

            <div className="platforms-grid">
              {Object.entries(generatedContent).map(([platform, data]) => (
                <div key={platform} className="platform-content-card">
                  <div className="platform-card-header" style={{ borderLeftColor: platformColors[platform] }}>
                    <div className="platform-info">
                      {platformIcons[platform]}
                      <span className="platform-title">{platformNames[platform]}</span>
                    </div>
                    <span className="char-count-badge">
                      {editedContent[platform]?.content?.length || 0} chars
                    </span>
                  </div>

                  <div className="platform-card-body">
                    <textarea
                      value={editedContent[platform]?.content || ''}
                      onChange={(e) => handleEditContent(platform, e.target.value)}
                      rows="6"
                      className="content-editor"
                      placeholder={`Content for ${platformNames[platform]}...`}
                    />
                  </div>

                  <div className="platform-card-footer">
                    {/* Approval Status */}
                    {approvalStatus[platform] && (
                      <div className={`approval-badge ${approvalStatus[platform]}`}>
                        {approvalStatus[platform] === 'approved' && 'Approved'}
                        {approvalStatus[platform] === 'rejected' && 'Rejected'}
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="action-buttons">
                      <button
                        onClick={() => handleApprove(platform)}
                        className={`action-btn approve ${approvalStatus[platform] === 'approved' ? 'active' : ''}`}
                        title="Approve content"
                        disabled={approvalStatus[platform] === 'approved'}
                      >
                        ✓
                      </button>
                      <button
                        onClick={() => handleReject(platform)}
                        className={`action-btn reject ${approvalStatus[platform] === 'rejected' ? 'active' : ''}`}
                        title="Reject content"
                      >
                        ✗
                      </button>
                      <button
                        onClick={() => handleRegenerate(platform)}
                        className="action-btn regenerate"
                        title="Regenerate new content"
                        disabled={regeneratingPlatform === platform}
                      >
                        {regeneratingPlatform === platform ? '⏳' : '🔄'}
                      </button>
                    </div>

                    {/* Use Button - Only shows when approved */}
                    {approvalStatus[platform] === 'approved' && (
                      <button
                        onClick={() => handleUseContent(platform)}
                        className="use-content-btn"
                      >
                        Use in Create Page →
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Publish to All Section */}
            <div className="publish-all-section">
              <div className="publish-all-header">
                <div className="approved-count">
                  {Object.values(approvalStatus).filter(s => s === 'approved').length} platforms approved
                </div>
                <div className="publish-buttons">
                  <button
                    onClick={() => handlePublishToAll(false)}
                    className="publish-all-btn post-now"
                    disabled={isPublishing || Object.values(approvalStatus).filter(s => s === 'approved').length === 0 || !imageApprovalStatus}
                  >
                    {isPublishing ? (
                      <>
                        <span className="spinner"></span>
                        Publishing...
                      </>
                    ) : (
                      'Publish to All Approved'
                    )}
                  </button>
                  <button
                    onClick={() => setShowScheduleModal(true)}
                    className="publish-all-btn schedule"
                    disabled={isPublishing || Object.values(approvalStatus).filter(s => s === 'approved').length === 0 || !imageApprovalStatus}
                  >
                    Schedule All Approved
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Modal */}
        {showScheduleModal && (
          <div className="modal-overlay" onClick={() => setShowScheduleModal(false)}>
            <div className="schedule-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Schedule Posts</h3>
                <button onClick={() => setShowScheduleModal(false)} className="modal-close">✕</button>
              </div>
              <div className="modal-body">
                <p className="modal-subtitle">
                  Schedule {Object.values(approvalStatus).filter(s => s === 'approved').length} approved posts
                </p>
                <div className="schedule-inputs-modal">
                  <div className="schedule-field">
                    <label>Date</label>
                    <input
                      type="date"
                      value={scheduledDate}
                      onChange={(e) => setScheduledDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className="date-input"
                    />
                  </div>
                  <div className="schedule-field">
                    <label>Hour (24h)</label>
                    <select
                      value={scheduledHour}
                      onChange={(e) => setScheduledHour(e.target.value)}
                      className="time-select"
                    >
                      <option value="">Hour</option>
                      {Array.from({ length: 24 }, (_, i) => {
                        const hour = i.toString().padStart(2, '0')
                        return <option key={hour} value={hour}>{hour}</option>
                      })}
                    </select>
                  </div>
                  <div className="schedule-field">
                    <label>Minute</label>
                    <select
                      value={scheduledMinute}
                      onChange={(e) => setScheduledMinute(e.target.value)}
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
              <div className="modal-footer">
                <button onClick={() => setShowScheduleModal(false)} className="modal-btn cancel">
                  Cancel
                </button>
                <button 
                  onClick={() => handlePublishToAll(true)} 
                  className="modal-btn confirm"
                  disabled={isPublishing}
                >
                  {isPublishing ? 'Scheduling...' : 'Schedule Posts'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tips Section */}
        {!generatedContent && (
          <div className="tips-section">
            <h3 className="tips-title">Tips for Better Results</h3>
            <ul className="tips-list">
              <li>Be specific about your topic</li>
              <li>Mention key details you want included</li>
              <li>Try different tones to see what works best</li>
              <li>Edit generated content to add your personal touch</li>
            </ul>
          </div>
        )}

        {/* Provider Selection Modal for Regeneration */}
        {showProviderModal && (
          <div className="modal-overlay" onClick={() => setShowProviderModal(false)}>
            <div className="provider-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Choose Image Generator</h3>
                <button className="modal-close" onClick={() => setShowProviderModal(false)}>✕</button>
              </div>
              <div className="modal-content">
                <p className="modal-subtitle">Select which AI to regenerate the image:</p>
                <div className="modal-provider-grid">
                  <div
                    className="modal-provider-card"
                    onClick={() => handleRegenerateWithProvider('nano-banana')}
                  >
                    <div className="modal-provider-icon">🍌</div>
                    <div className="modal-provider-info">
                      <div className="modal-provider-name">Nano Banana</div>
                      <div className="modal-provider-speed">Ultra Fast • 2-3s</div>
                      <div className="modal-provider-desc">Fal.ai - Best for quick iterations</div>
                    </div>
                  </div>
                  
                  <div
                    className="modal-provider-card"
                    onClick={() => handleRegenerateWithProvider('dalle')}
                  >
                    <div className="modal-provider-icon">🎨</div>
                    <div className="modal-provider-info">
                      <div className="modal-provider-name">DALL-E 3</div>
                      <div className="modal-provider-speed">Standard • 15-20s</div>
                      <div className="modal-provider-desc">OpenAI - Premium quality</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default GeneratorPage

