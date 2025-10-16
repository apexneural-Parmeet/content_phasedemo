import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import './App.css'
import Navigation from './components/Navigation'
import LandingPage from './pages/LandingPage'
import GeneratorPage from './pages/GeneratorPage'
import HomePage from './pages/HomePage'
import SchedulerPage from './pages/SchedulerPage'
import ConnectionsPage from './pages/ConnectionsPage'
import { GeneratedContentProvider } from './context/GeneratedContentContext'

function AppContent() {
  const location = useLocation()
  const showNavigation = location.pathname !== '/'

  return (
    <div className="app-container">
      {showNavigation && <Navigation />}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/generate" element={<GeneratorPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/scheduler" element={<SchedulerPage />} />
        <Route path="/connections" element={<ConnectionsPage />} />
      </Routes>
    </div>
  )
}

function App() {
  return (
    <Router>
      <GeneratedContentProvider>
        <AppContent />
      </GeneratedContentProvider>
    </Router>
  )
}

export default App
