import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import './CustomerProfile.css'

const CustomerProfile = ({ userId, isVisible, onToggle }) => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (userId && isVisible) {
      fetchCustomerProfile()
    }
  }, [userId, isVisible])

  const fetchCustomerProfile = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/customer/${userId}`)
      const data = await response.json()
      setProfile(data)
    } catch (error) {
      console.error('Error fetching customer profile:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isVisible) return null

  return (
    <motion.div
      className="customer-profile"
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="profile-header">
        <h3>Customer Profile</h3>
        <button className="close-btn" onClick={onToggle}>
          ×
        </button>
      </div>

      <div className="profile-content">
        {loading ? (
          <div className="loading">Loading profile...</div>
        ) : profile ? (
          <>
            <div className="profile-section">
              <div className="profile-avatar">
                <div className="avatar-circle">
                  {profile.name ? profile.name.charAt(0).toUpperCase() : 'U'}
                </div>
              </div>
              <div className="profile-info">
                <h4>{profile.name || 'Unknown Customer'}</h4>
                <p>{profile.email || 'No email provided'}</p>
                <p>{profile.company || 'No company'}</p>
              </div>
            </div>

            <div className="profile-section">
              <h5>Current Plan</h5>
              <div className="plan-info">
                <div className="plan-name">{profile.plan || 'Basic'}</div>
                <div className="plan-price">${profile.subscription_value || 29}/month</div>
              </div>
            </div>

            <div className="profile-section">
              <h5>Usage & Metrics</h5>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Monthly Usage</span>
                  <span className="metric-value">{profile.monthly_usage || 0}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Tenure</span>
                  <span className="metric-value">{profile.months_subscribed || 0} months</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Support Tickets</span>
                  <span className="metric-value">{profile.support_tickets || 0}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Payment Issues</span>
                  <span className="metric-value">{profile.payment_issues || 0}</span>
                </div>
              </div>
            </div>

            <div className="profile-section">
              <h5>Risk Assessment</h5>
              <div className="risk-indicators">
                <div className={`risk-item ${profile.churn_risk === 'high' ? 'high-risk' : profile.churn_risk === 'medium' ? 'medium-risk' : 'low-risk'}`}>
                  <span className="risk-label">Churn Risk</span>
                  <span className="risk-value">{profile.churn_risk || 'Low'}</span>
                </div>
                <div className={`risk-item ${profile.upsell_potential === 'high' ? 'high-potential' : profile.upsell_potential === 'medium' ? 'medium-potential' : 'low-potential'}`}>
                  <span className="risk-label">Upsell Potential</span>
                  <span className="risk-value">{profile.upsell_potential || 'Low'}</span>
                </div>
              </div>
            </div>

            <div className="profile-section">
              <h5>Features Used</h5>
              <div className="features-list">
                {profile.feature_usage && profile.feature_usage.length > 0 ? (
                  profile.feature_usage.map((feature, index) => (
                    <span key={index} className="feature-tag">
                      {feature}
                    </span>
                  ))
                ) : (
                  <span className="no-features">No features tracked</span>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="no-profile">No profile data available</div>
        )}
      </div>
    </motion.div>
  )
}

export default CustomerProfile
