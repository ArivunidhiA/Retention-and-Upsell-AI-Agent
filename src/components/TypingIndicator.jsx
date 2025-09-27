import React from 'react'
import { motion } from 'framer-motion'
import './TypingIndicator.css'

const TypingIndicator = () => {
  return (
    <motion.div 
      className="typing-indicator"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="typing-content">
        <div className="typing-header">
          <div className="typing-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="typing-details">
            <span className="typing-name">AI Agent</span>
            <span className="typing-status">is typing...</span>
          </div>
        </div>
        
        <div className="typing-dots">
          <motion.div 
            className="typing-dot"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              delay: 0
            }}
          />
          <motion.div 
            className="typing-dot"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              delay: 0.2
            }}
          />
          <motion.div 
            className="typing-dot"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              delay: 0.4
            }}
          />
        </div>
      </div>
    </motion.div>
  )
}

export default TypingIndicator
