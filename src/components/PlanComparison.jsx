import React from 'react'
import { motion } from 'framer-motion'
import './PlanComparison.css'

const PlanComparison = ({ comparison, onAccept, onDecline }) => {
  if (!comparison) return null

  const { current_plan, suggested_plan, action } = comparison

  return (
    <motion.div
      className="plan-comparison"
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="comparison-header">
        <h3>
          {action === 'upsell' ? '🚀 Upgrade Recommendation' : '💡 Plan Optimization'}
        </h3>
        <p>
          {action === 'upsell' 
            ? 'Based on your usage, we recommend upgrading to get more value'
            : 'Let us help you find a plan that better fits your needs'
          }
        </p>
      </div>

      <div className="plans-container">
        <div className="plan-card current-plan">
          <div className="plan-header">
            <h4>{current_plan.name}</h4>
            <div className="plan-price">${current_plan.price}/month</div>
          </div>
          <div className="plan-features">
            <h5>Current Features:</h5>
            <ul>
              {current_plan.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="comparison-arrow">
          <motion.div
            className="arrow"
            animate={{ x: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            →
          </motion.div>
        </div>

        <div className="plan-card suggested-plan">
          <div className="plan-header">
            <h4>{suggested_plan.name}</h4>
            <div className="plan-price">${suggested_plan.price}/month</div>
          </div>
          <div className="plan-features">
            <h5>Suggested Features:</h5>
            <ul>
              {suggested_plan.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="comparison-actions">
        <motion.button
          className="accept-btn"
          onClick={() => onAccept && onAccept(suggested_plan)}
          whileHover={{ scale: 1.05, boxShadow: "0 8px 25px rgba(255, 140, 0, 0.4)" }}
          whileTap={{ scale: 0.95 }}
        >
          Accept {suggested_plan.name}
        </motion.button>
        <motion.button
          className="decline-btn"
          onClick={() => onDecline && onDecline()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Keep Current Plan
        </motion.button>
      </div>
    </motion.div>
  )
}

export default PlanComparison
