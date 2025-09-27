import React from 'react'
import { motion } from 'framer-motion'
import './ChatBubble.css'

const ChatBubble = ({ message, onOptionClick }) => {
  const isUser = message.sender === 'user'
  const isAgent = message.sender === 'agent'
  
  const getActionIcon = (action) => {
    switch (action) {
      case 'retention':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2"/>
          </svg>
        )
      case 'upsell':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M7 17L17 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M7 7H17V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )
      case 'escalate':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2"/>
          </svg>
        )
      default:
        return null
    }
  }

  const getActionColor = (action) => {
    switch (action) {
      case 'retention':
        return '#f59e0b'
      case 'upsell':
        return '#10b981'
      case 'escalate':
        return '#ef4444'
      default:
        return '#6366f1'
    }
  }

  const getActionLabel = (action) => {
    switch (action) {
      case 'retention':
        return 'Retention Strategy'
      case 'upsell':
        return 'Upsell Opportunity'
      case 'escalate':
        return 'Escalation'
      default:
        return 'Neutral'
    }
  }

  return (
    <motion.div
      className={`chat-bubble ${isUser ? 'user' : 'agent'}`}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="bubble-content">
        <div className="bubble-header">
          <div className="sender-info">
            <div className={`sender-avatar ${isUser ? 'user-avatar' : 'agent-avatar'}`}>
              {isUser ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            <div className="sender-details">
              <span className="sender-name">
                {isUser ? 'You' : 'AI Agent'}
              </span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
          
          {isAgent && message.action && message.action !== 'neutral' && (
            <div 
              className="action-badge"
              style={{ backgroundColor: `${getActionColor(message.action)}20`, borderColor: `${getActionColor(message.action)}40` }}
            >
              <span style={{ color: getActionColor(message.action) }}>
                {getActionIcon(message.action)}
                {getActionLabel(message.action)}
              </span>
            </div>
          )}
        </div>
        
        <div className="message-text">
          {message.text}
        </div>
        
        {isAgent && message.suggestedOffer && (
          <motion.div 
            className="offer-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <div className="offer-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L15.09 8.26L22 9L17 14L18.18 21L12 17.77L5.82 21L7 14L2 9L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Special Offer</span>
            </div>
            <div className="offer-content">
              {message.suggestedOffer}
            </div>
          </motion.div>
        )}
        
        {isAgent && message.confidence && (
          <div className="confidence-indicator">
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ width: `${message.confidence * 100}%` }}
              />
            </div>
            <span className="confidence-text">
              Confidence: {Math.round(message.confidence * 100)}%
            </span>
          </div>
        )}

        {isAgent && message.options && message.options.length > 0 && (
          <motion.div 
            className="quick-reply-options"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.4 }}
          >
            <div className="options-label">Quick replies:</div>
            <div className="options-grid">
              {message.options.map((option, index) => (
                <motion.button
                  key={index}
                  className="quick-reply-btn"
                  onClick={() => onOptionClick && onOptionClick(option)}
                  whileHover={{ scale: 1.05, boxShadow: "0 8px 25px rgba(255, 140, 0, 0.3)" }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                >
                  {option}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default ChatBubble
