const { Handler } = require('@netlify/functions');

// Mock customer data
const customers = {
  "user_001": {
    "name": "John Smith",
    "email": "john@example.com",
    "company": "Tech Corp",
    "plan": "basic",
    "subscription_value": 29,
    "monthly_usage": 50,
    "months_subscribed": 6,
    "payment_issues": 0,
    "support_tickets": 1,
    "feature_usage": ["email_templates", "basic_analytics"],
    "churn_risk": "low",
    "upsell_potential": "medium"
  }
};

// Mock product data
const products = {
  "plans": {
    "basic": {
      "name": "Basic Plan",
      "price": 29,
      "features": [
        "Email campaigns (up to 1,000 contacts)",
        "Basic analytics dashboard",
        "Email templates (10 templates)",
        "Customer support (email only)",
        "Basic automation (3 workflows)",
        "Mobile app access"
      ]
    },
    "professional": {
      "name": "Professional Plan",
      "price": 79,
      "features": [
        "Everything in Basic",
        "Advanced analytics & reporting",
        "Email campaigns (up to 10,000 contacts)",
        "Premium email templates (50 templates)",
        "Priority customer support",
        "Advanced automation (unlimited workflows)",
        "A/B testing",
        "API access",
        "Custom integrations",
        "Team collaboration (up to 5 members)"
      ]
    },
    "premium": {
      "name": "Premium Plan",
      "price": 199,
      "features": [
        "Everything in Professional",
        "Unlimited contacts",
        "AI-powered automation",
        "Advanced segmentation",
        "24/7 dedicated support",
        "Custom integrations"
      ]
    }
  }
};

// Intent detection
function detectIntent(message) {
  const msg = message.toLowerCase();
  
  if (msg.includes('cancel') || msg.includes('unsubscribe') || msg.includes('quit')) {
    return 'cancel';
  } else if (msg.includes('expensive') || msg.includes('price') || msg.includes('cost')) {
    return 'pricing_confusion';
  } else if (msg.includes('feature') || msg.includes('upgrade') || msg.includes('more')) {
    return 'feature_relevance';
  } else if (msg.includes('discount') || msg.includes('cheaper') || msg.includes('deal')) {
    return 'discount_request';
  } else if (msg.includes('human') || msg.includes('support') || msg.includes('help')) {
    return 'escalation';
  } else if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
    return 'greeting';
  } else {
    return 'general_inquiry';
  }
}

// Generate AI response
function generateAIResponse(message, customerProfile) {
  const intent = detectIntent(message);
  const usageLevel = customerProfile.usage_level || 'low';
  const churnRisk = customerProfile.churn_risk || 'low';
  const upsellPotential = customerProfile.upsell_potential || 'low';
  
  let response, action, confidence, suggestedOffer, options;
  
  switch (intent) {
    case 'greeting':
      response = "Hello! I'm your AI assistant for customer retention and upsell. I can help you with subscription management, feature recommendations, pricing questions, and more. How can I assist you today?";
      action = 'neutral';
      confidence = 0.8;
      suggestedOffer = null;
      options = [
        "I want to cancel my subscription",
        "The price is too expensive",
        "I need more features",
        "I'm having technical issues"
      ];
      break;
      
    case 'cancel':
      response = "I'm sorry to hear you're considering canceling. Could you help me understand what's not working for you? I'd like to see if we can find a solution that better meets your needs.";
      action = 'retention';
      confidence = 0.7;
      suggestedOffer = "Account optimization consultation";
      options = [
        "It's too expensive",
        "I'm not using the features",
        "I found a better alternative",
        "I'm having technical issues"
      ];
      break;
      
    case 'pricing_confusion':
      response = "I understand your concerns about pricing. You're currently on our Basic Plan at $29/month. Let me show you the value you're getting and compare it with our other options. Our Professional plan at $79/month offers much more value per dollar with advanced features. Would you like me to break down the cost-benefit analysis?";
      action = 'upsell';
      confidence = 0.8;
      suggestedOffer = "Professional plan upgrade with cost analysis";
      options = [
        "Yes, show me the cost analysis",
        "What's included in Professional?",
        "Do you have any discounts?",
        "I want to downgrade instead"
      ];
      break;
      
    case 'feature_relevance':
      response = "I'd be happy to help you find the right features! Let me understand your specific needs better. What functionality are you looking for, and how do you plan to use it?";
      action = 'neutral';
      confidence = 0.7;
      suggestedOffer = "Feature consultation";
      options = [
        "Email automation",
        "Analytics & reporting",
        "API access",
        "Team collaboration"
      ];
      break;
      
    case 'discount_request':
      response = "I understand you're looking for a better deal. Based on your usage patterns and loyalty, I can offer you a 15% discount for the next 3 months. This would bring your Basic Plan down to $24.65/month. Would you like to take advantage of this offer?";
      action = 'retention';
      confidence = 0.8;
      suggestedOffer = "15% discount for 3 months";
      options = [
        "Yes, I'll take the discount",
        "Can you do better?",
        "I want to upgrade instead",
        "No thanks"
      ];
      break;
      
    case 'escalation':
      response = "I understand you'd like to speak with a human representative. I'll connect you with our customer success team right away. They'll have access to your full account history and can provide personalized assistance. You should receive a call within 15 minutes.";
      action = 'escalate';
      confidence = 0.95;
      suggestedOffer = "Human representative connection";
      options = [
        "Schedule a call for later",
        "Send me an email instead",
        "I'll wait for the call",
        "Cancel the request"
      ];
      break;
      
    default:
      response = "I'm here to help! Could you tell me more about what you're looking for? I can assist with subscription management, feature recommendations, pricing questions, or connect you with our support team.";
      action = 'neutral';
      confidence = 0.6;
      suggestedOffer = null;
      options = [
        "Show me my plan",
        "What features do I have?",
        "How can I upgrade?",
        "Talk to a human"
      ];
  }
  
  return {
    response,
    action,
    confidence,
    suggestedOffer,
    tools_used: ["IntentDetection", "CustomerLookup"],
    options,
    latency_ms: Math.random() * 100 + 50, // Mock latency
    churn_risk_reduction: action === 'retention' ? "35%" : "0%",
    upsell_boost: action === 'upsell' ? "20%" : "0%",
    plan_comparison: generatePlanComparison(customerProfile.plan, action)
  };
}

// Generate plan comparison
function generatePlanComparison(currentPlan, action) {
  const currentPlanData = products.plans[currentPlan] || products.plans.basic;
  let suggestedPlan;
  
  if (action === 'upsell') {
    if (currentPlan === 'basic') {
      suggestedPlan = products.plans.professional;
    } else if (currentPlan === 'professional') {
      suggestedPlan = products.plans.premium;
    } else {
      suggestedPlan = products.plans.premium;
    }
  } else {
    suggestedPlan = currentPlanData;
  }
  
  return {
    current_plan: {
      name: currentPlanData.name,
      price: currentPlanData.price,
      features: currentPlanData.features
    },
    suggested_plan: {
      name: suggestedPlan.name,
      price: suggestedPlan.price,
      features: suggestedPlan.features
    },
    action: action
  };
}

// Main handler
exports.handler = async (event, context) => {
  // Handle CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    if (event.httpMethod === 'POST') {
      const body = JSON.parse(event.body);
      const { userId, message } = body;
      
      // Get customer profile
      const customerProfile = customers[userId] || {
        name: userId,
        email: `${userId}@example.com`,
        company: "Demo Company",
        plan: "basic",
        subscription_value: 29,
        monthly_usage: 50,
        months_subscribed: 6,
        payment_issues: 0,
        support_tickets: 1,
        feature_usage: ["email_templates", "basic_analytics"],
        churn_risk: "low",
        upsell_potential: "medium"
      };
      
      // Generate AI response
      const aiResponse = generateAIResponse(message, customerProfile);
      
      return {
        statusCode: 200,
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(aiResponse)
      };
    }
    
    if (event.httpMethod === 'GET') {
      // Health check
      if (event.path === '/api/health') {
        return {
          statusCode: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: "healthy",
            langchain_initialized: false,
            vectorstore_ready: false,
            gpt4_enabled: false,
            demo_mode: true,
            timestamp: new Date().toISOString()
          })
        };
      }
      
      // Metrics
      if (event.path === '/api/metrics') {
        return {
          statusCode: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            total_conversations: 10,
            churn_prevented: 2,
            upsells_completed: 1,
            avg_latency_ms: 150,
            offers_shown: 5,
            offers_accepted: 3,
            escalations: 1,
            tickets_generated: 1,
            churn_risk_reduction: "35%",
            upsell_boost: "20%",
            demo_mode: true,
            timestamp: new Date().toISOString()
          })
        };
      }
      
      // Customer profile
      if (event.path.startsWith('/api/customer/')) {
        const userId = event.path.split('/').pop();
        const customerProfile = customers[userId] || {
          name: userId,
          email: `${userId}@example.com`,
          company: "Demo Company",
          plan: "basic",
          subscription_value: 29,
          monthly_usage: 50,
          months_subscribed: 6,
          payment_issues: 0,
          support_tickets: 1,
          feature_usage: ["email_templates", "basic_analytics"],
          churn_risk: "low",
          upsell_potential: "medium"
        };
        
        return {
          statusCode: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(customerProfile)
        };
      }
    }
    
    return {
      statusCode: 404,
      headers,
      body: JSON.stringify({ error: 'Not found' })
    };
    
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
