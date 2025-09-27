exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

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
};
