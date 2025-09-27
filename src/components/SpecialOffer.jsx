import React from 'react'
import { motion } from 'framer-motion'
import './SpecialOffer.css'

const SpecialOffer = ({ offer, onAccept, onDecline }) => {
  if (!offer) return null

  return (
    <motion.div
      className="special-offer"
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="offer-glow"></div>
      
      <div className="offer-header">
        <div className="offer-icon">🎁</div>
        <h3>Special Offer</h3>
        <div className="offer-badge">Limited Time</div>
      </div>

      <div className="offer-content">
        <p className="offer-description">{offer}</p>
        
        <div className="offer-benefits">
          <div className="benefit-item">
            <span className="benefit-icon">✓</span>
            <span>Instant activation</span>
          </div>
          <div className="benefit-item">
            <span className="benefit-icon">✓</span>
            <span>No commitment required</span>
          </div>
          <div className="benefit-item">
            <span className="benefit-icon">✓</span>
            <span>Cancel anytime</span>
          </div>
        </div>
      </div>

      <div className="offer-actions">
        <motion.button
          className="accept-offer-btn"
          onClick={() => onAccept && onAccept()}
          whileHover={{ 
            scale: 1.05, 
            boxShadow: "0 8px 25px rgba(255, 140, 0, 0.4)",
            y: -2
          }}
          whileTap={{ scale: 0.95 }}
        >
          Accept Offer
        </motion.button>
        
        <motion.button
          className="decline-offer-btn"
          onClick={() => onDecline && onDecline()}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
        >
          No Thanks
        </motion.button>
      </div>

      <div className="offer-timer">
        <span>⏰ This offer expires in 24 hours</span>
      </div>
    </motion.div>
  )
}

export default SpecialOffer
