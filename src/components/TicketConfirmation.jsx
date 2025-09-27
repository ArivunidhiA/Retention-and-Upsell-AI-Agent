import React from 'react'
import { motion } from 'framer-motion'
import './TicketConfirmation.css'

const TicketConfirmation = ({ ticketNumber, summary, onClose }) => {
  return (
    <motion.div
      className="ticket-confirmation-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="ticket-confirmation"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.3 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="ticket-header">
          <div className="ticket-icon">🎫</div>
          <h3>Ticket Created Successfully</h3>
        </div>

        <div className="ticket-content">
          <div className="ticket-number">
            <span className="ticket-label">Ticket Number:</span>
            <motion.div
              className="ticket-badge"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              {ticketNumber}
            </motion.div>
          </div>

          <div className="ticket-details">
            <h4>What happens next?</h4>
            <ul>
              <li>A human specialist will review your case</li>
              <li>You'll receive a call within 15 minutes</li>
              <li>Your conversation history has been shared</li>
              <li>You can reference this ticket number for follow-ups</li>
            </ul>
          </div>

          {summary && (
            <div className="conversation-summary">
              <h4>Conversation Summary</h4>
              <p>{summary}</p>
            </div>
          )}

          <div className="ticket-actions">
            <motion.button
              className="close-ticket-btn"
              onClick={onClose}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Got it, thanks!
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default TicketConfirmation
