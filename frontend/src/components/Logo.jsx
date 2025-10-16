import React from 'react'

// Simple animated triangle logo inspired by the provided image
// Uses stroke-dash animations and glow for a subtle "shiny" effect
export default function Logo({ size = 56 }) {
  return (
    <div className="logo-container" aria-label="App logo">
      <svg
        className="logo"
        width={size}
        height={size}
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
      >
        <defs>
          {/* moving gradient for shine */}
          <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#c0c0c0" stopOpacity="0" />
            <stop offset="50%" stopColor="#c0c0c0" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#c0c0c0" stopOpacity="0" />
          </linearGradient>
          <mask id="shineMask">
            <rect x="0" y="0" width="100" height="100" fill="url(#shine)" className="logo-shine" />
          </mask>
        </defs>

        {/* Outer triangle */}
        <path
          d="M50 6 L94 86 H6 Z"
          fill="none"
          stroke="#c0c0c0"
          strokeWidth="3"
          className="logo-stroke"
        />
        {/* Middle triangle */}
        <path
          d="M50 18 L83 76 H17 Z"
          fill="none"
          stroke="#c0c0c0"
          strokeWidth="3"
          className="logo-stroke"
        />
        {/* Inner filled triangle */}
        <path d="M50 34 L71 70 H29 Z" fill="#c0c0c0" mask="url(#shineMask)" />
      </svg>
    </div>
  )
}


