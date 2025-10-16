import { createContext, useContext, useState, useEffect } from 'react'

const GeneratedContentContext = createContext()

export function GeneratedContentProvider({ children }) {
  const [generatedData, setGeneratedData] = useState(() => {
    // Load from localStorage on init
    const saved = localStorage.getItem('generatedContent')
    return saved ? JSON.parse(saved) : null
  })

  // Save to localStorage whenever it changes
  useEffect(() => {
    if (generatedData) {
      localStorage.setItem('generatedContent', JSON.stringify(generatedData))
    } else {
      localStorage.removeItem('generatedContent')
    }
  }, [generatedData])

  const saveGeneratedContent = (content, image, topic, tone, imageStyle = 'realistic') => {
    setGeneratedData({
      content,
      image,
      topic,
      tone,
      imageStyle,
      timestamp: new Date().toISOString()
    })
  }

  const clearGeneratedContent = () => {
    setGeneratedData(null)
    localStorage.removeItem('generatedContent')
  }

  return (
    <GeneratedContentContext.Provider value={{ 
      generatedData, 
      saveGeneratedContent, 
      clearGeneratedContent 
    }}>
      {children}
    </GeneratedContentContext.Provider>
  )
}

export function useGeneratedContent() {
  const context = useContext(GeneratedContentContext)
  if (!context) {
    throw new Error('useGeneratedContent must be used within GeneratedContentProvider')
  }
  return context
}

