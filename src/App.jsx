import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import ChatBubble from './components/ChatBubble'
import TypingIndicator from './components/TypingIndicator'
import Header from './components/Header'
import PlanComparison from './components/PlanComparison'
import SpecialOffer from './components/SpecialOffer'
import CustomerProfile from './components/CustomerProfile'
import TicketConfirmation from './components/TicketConfirmation'
import './App.css'

const API_BASE_URL = '/api'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [userId] = useState(() => `user_${Math.random().toString(36).substr(2, 9)}`)
  const [showProfile, setShowProfile] = useState(false)
  const [currentOffer, setCurrentOffer] = useState(null)
  const [currentPlanComparison, setCurrentPlanComparison] = useState(null)
  const [ticketInfo, setTicketInfo] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (message) => {
    if (!message.trim()) return

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        userId: userId,
        message: message
      })

      const agentMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'agent',
        timestamp: new Date(),
        action: response.data.action,
        confidence: response.data.confidence,
        suggestedOffer: response.data.suggestedOffer,
        options: response.data.options,
        planComparison: response.data.plan_comparison,
        ticketNumber: response.data.ticket_number,
        conversationSummary: response.data.conversation_summary
      }

      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment.",
        sender: 'agent',
        timestamp: new Date(),
        action: 'error',
        confidence: 0
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(inputMessage)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(inputMessage)
    }
  }

  const handleOptionClick = (option) => {
    sendMessage(option)
  }

  const handleOfferAccept = async (offerType) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/offer-response`, {
        userId: userId,
        offerType: offerType,
        accepted: true
      })
      
      const agentMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'agent',
        timestamp: new Date(),
        action: response.data.action,
        confidence: response.data.confidence,
        options: response.data.options
      }
      
      setMessages(prev => [...prev, agentMessage])
      setCurrentOffer(null)
    } catch (error) {
      console.error('Error accepting offer:', error)
    }
  }

  const handleOfferDecline = async (offerType) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/offer-response`, {
        userId: userId,
        offerType: offerType,
        accepted: false
      })
      
      const agentMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'agent',
        timestamp: new Date(),
        action: response.data.action,
        confidence: response.data.confidence,
        options: response.data.options
      }
      
      setMessages(prev => [...prev, agentMessage])
      setCurrentOffer(null)
    } catch (error) {
      console.error('Error declining offer:', error)
    }
  }

  const handleEscalation = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/escalate`, {
        userId: userId
      })
      
      const agentMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'agent',
        timestamp: new Date(),
        action: response.data.action,
        confidence: response.data.confidence,
        options: response.data.options
      }
      
      setMessages(prev => [...prev, agentMessage])
      setTicketInfo({
        ticketNumber: response.data.ticket_number,
        summary: response.data.conversation_summary
      })
    } catch (error) {
      console.error('Error escalating:', error)
    }
  }

  const handlePlanAccept = (plan) => {
    sendMessage(`I accept the ${plan.name} plan`)
    setCurrentPlanComparison(null)
  }

  const handlePlanDecline = () => {
    sendMessage("I want to keep my current plan")
    setCurrentPlanComparison(null)
  }

  const clearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat and start fresh?')) {
      setMessages([])
      setCurrentOffer(null)
      setCurrentPlanComparison(null)
      setTicketInfo(null)
    }
  }

  const quickActions = [
    "I want to cancel my subscription",
    "The price is too expensive",
    "I need more features",
    "I'm having technical issues",
    "What upgrade options do you have?",
    "I'm not getting value from this",
    "How can I use the API?",
    "I need help with automation",
    "Can I get a discount?",
    "What's included in the premium plan?"
  ]

  const handleQuickAction = (action) => {
    if (action === "Clear Chat") {
      clearChat()
    } else {
      sendMessage(action)
    }
  }

  return (
    <div className="app">
      {/* Particle Effects */}
      <div className="particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>
      
      <Header />
      
      <motion.div 
        className="chat-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="messages-container">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                <ChatBubble message={message} onOptionClick={handleOptionClick} />
                
                {message.planComparison && (
                  <PlanComparison
                    comparison={message.planComparison}
                    onAccept={handlePlanAccept}
                    onDecline={handlePlanDecline}
                  />
                )}
                
                {message.suggestedOffer && message.action === 'retention' && (
                  <SpecialOffer
                    offer={message.suggestedOffer}
                    onAccept={() => handleOfferAccept(message.suggestedOffer)}
                    onDecline={() => handleOfferDecline(message.suggestedOffer)}
                  />
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <TypingIndicator />
            </motion.div>
          )}
          
          {messages.length === 0 && (
            <motion.div 
              className="welcome-message"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              <div className="welcome-content">
                <h2>Welcome to AI Agent - Retention and Upsell</h2>
                <p>I'm your AI assistant for customer retention and upsell strategies. I can help you with subscription management, feature recommendations, pricing questions, and demonstrate intelligent customer support capabilities.</p>
                <div className="quick-actions">
                  <p>Try asking:</p>
                  <div className="quick-buttons">
                    {quickActions.map((action, index) => (
                      <motion.button
                        key={index}
                        className="quick-action-btn"
                        onClick={() => handleQuickAction(action)}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        transition={{ type: "spring", stiffness: 300, damping: 20 }}
                      >
                        {action}
                      </motion.button>
                    ))}
                    <motion.button
                      className="quick-action-btn clear-action-btn"
                      onClick={() => handleQuickAction("Clear Chat")}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    >
                      🗑️ Clear Chat
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <motion.form 
          className="input-container"
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <div className="input-wrapper">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="message-input"
              disabled={isLoading}
            />
            <motion.button
              type="submit"
              className="send-button"
              disabled={!inputMessage.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </motion.button>
          </div>
        </motion.form>
      </motion.div>

      {/* Customer Profile Sidebar */}
      <CustomerProfile
        userId={userId}
        isVisible={showProfile}
        onToggle={() => setShowProfile(!showProfile)}
      />

      {/* Ticket Confirmation Modal */}
      {ticketInfo && (
        <TicketConfirmation
          ticketNumber={ticketInfo.ticketNumber}
          summary={ticketInfo.summary}
          onClose={() => setTicketInfo(null)}
        />
      )}

      {/* Profile Toggle Button */}
      <motion.button
        className="profile-toggle-btn"
        onClick={() => setShowProfile(!showProfile)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1 }}
      >
        👤
      </motion.button>

      {/* Clear Chat Button */}
      <motion.button
        className="clear-chat-btn"
        onClick={clearChat}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.2 }}
        title="Clear chat and start fresh"
      >
        🗑️
      </motion.button>
    </div>
  )
}

export default App
