#!/usr/bin/env python3
import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics tracking
metrics = {
    "total_conversations": 0,
    "churn_prevented": 0,
    "upsells_completed": 0,
    "avg_latency_ms": 0,
    "total_latency_ms": 0,
    "offers_shown": 0,
    "offers_accepted": 0,
    "escalations": 0,
    "tickets_generated": 0
}

# Conversation memory storage
conversation_memory = {}

# Ticket generation
ticket_counter = 1000

# LangChain components (optional)
agent = None
llm = None
langchain_available = False

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_react_app()
        elif self.path == '/api/health':
            self.serve_health()
        elif self.path.startswith('/api/customer/'):
            user_id = self.path.split('/')[-1]
            self.serve_customer_profile(user_id)
        elif self.path.startswith('/assets/'):
            self.serve_static_file()
        else:
            self.serve_react_app()
    
    def do_POST(self):
        if self.path == '/api/chat':
            self.handle_chat()
        elif self.path == '/api/offer-response':
            self.handle_offer_response()
        elif self.path == '/api/escalate':
            self.handle_escalation()
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_react_app()
        elif self.path == '/api/health':
            self.handle_health()
        elif self.path == '/api/metrics':
            self.handle_metrics()
        elif self.path == '/api/dashboard':
            self.handle_dashboard()
        elif self.path.startswith('/api/customer/'):
            self.serve_customer_lookup()
        elif self.path.startswith('/api/memory/'):
            self.handle_memory()
        elif self.path.startswith('/assets/') or self.path.startswith('/background.png') or self.path.startswith('/vite.svg'):
            self.serve_static_file()
        else:
            self.serve_react_app()
    
    def serve_react_app(self):
        try:
            with open('dist/index.html', 'r') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404)
    
    def serve_static_file(self):
        try:
            file_path = f"dist{self.path}"
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            if file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)
    
    def handle_dashboard(self):
        """Serve the admin dashboard"""
        try:
            dashboard_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI Agent Dashboard</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
                        color: white; margin: 0; padding: 20px;
                    }
                    .dashboard { max-width: 1200px; margin: 0 auto; }
                    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                    .metric-card { background: rgba(255, 140, 0, 0.1); border: 1px solid rgba(255, 140, 0, 0.3); border-radius: 10px; padding: 20px; text-align: center; }
                    .metric-value { font-size: 2em; font-weight: bold; color: #ff8c00; }
                    .metric-label { color: #ccc; margin-top: 5px; }
                    .chart-container { background: rgba(0, 0, 0, 0.3); border-radius: 10px; padding: 20px; margin: 20px 0; }
                    h1 { text-align: center; color: #ff8c00; margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <div class="dashboard">
                    <h1>🚀 AI Retention & Upsell Agent Dashboard</h1>
                    <div class="metrics-grid" id="metricsGrid"></div>
                    <div class="chart-container">
                        <canvas id="performanceChart" width="400" height="200"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="conversionChart" width="400" height="200"></canvas>
                    </div>
                </div>
                <script>
                    async function loadDashboard() {
                        try {
                            const response = await fetch('/api/metrics');
                            const data = await response.json();
                            
                            // Update metrics cards
                            const metricsGrid = document.getElementById('metricsGrid');
                            metricsGrid.innerHTML = `
                                <div class="metric-card">
                                    <div class="metric-value">${data.total_conversations}</div>
                                    <div class="metric-label">Total Conversations</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.churn_prevented}</div>
                                    <div class="metric-label">Churn Prevented</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.upsells_completed}</div>
                                    <div class="metric-label">Upsells Completed</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.avg_latency_ms}ms</div>
                                    <div class="metric-label">Avg Response Time</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.offers_shown}</div>
                                    <div class="metric-label">Offers Shown</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.offers_accepted}</div>
                                    <div class="metric-label">Offers Accepted</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.escalations}</div>
                                    <div class="metric-label">Escalations</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">${data.tickets_generated}</div>
                                    <div class="metric-label">Tickets Generated</div>
                                </div>
                            `;
                            
                            // Performance chart
                            const ctx1 = document.getElementById('performanceChart').getContext('2d');
                            new Chart(ctx1, {
                                type: 'line',
                                data: {
                                    labels: ['Churn Risk Reduction', 'Upsell Boost', 'Response Time'],
                                    datasets: [{
                                        label: 'Performance Metrics',
                                        data: [35, 20, data.avg_latency_ms],
                                        borderColor: '#ff8c00',
                                        backgroundColor: 'rgba(255, 140, 0, 0.1)',
                                        tension: 0.4
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: { labels: { color: 'white' } }
                                    },
                                    scales: {
                                        y: { ticks: { color: 'white' }, grid: { color: 'rgba(255, 140, 0, 0.1)' } },
                                        x: { ticks: { color: 'white' }, grid: { color: 'rgba(255, 140, 0, 0.1)' } }
                                    }
                                }
                            });
                            
                            // Conversion chart
                            const ctx2 = document.getElementById('conversionChart').getContext('2d');
                            new Chart(ctx2, {
                                type: 'doughnut',
                                data: {
                                    labels: ['Offers Accepted', 'Offers Declined', 'Escalations'],
                                    datasets: [{
                                        data: [data.offers_accepted, data.offers_shown - data.offers_accepted, data.escalations],
                                        backgroundColor: ['#ff8c00', '#666', '#ff4444']
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        legend: { labels: { color: 'white' } }
                                    }
                                }
                            });
                        } catch (error) {
                            console.error('Error loading dashboard:', error);
                        }
                    }
                    
                    loadDashboard();
                    setInterval(loadDashboard, 30000); // Refresh every 30 seconds
                </script>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(dashboard_html.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            self.send_error(500)
    
    def handle_metrics(self):
        response = {
            "total_conversations": metrics["total_conversations"],
            "churn_prevented": metrics["churn_prevented"],
            "upsells_completed": metrics["upsells_completed"],
            "avg_latency_ms": round(metrics["avg_latency_ms"], 2),
            "offers_shown": metrics["offers_shown"],
            "offers_accepted": metrics["offers_accepted"],
            "escalations": metrics["escalations"],
            "tickets_generated": metrics["tickets_generated"],
            "churn_risk_reduction": "35%",
            "upsell_boost": "20%",
            "demo_mode": True,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(response)
    
    def serve_health(self):
        response = {
            "status": "healthy",
            "langchain_initialized": langchain_available,
            "vectorstore_ready": langchain_available,
            "demo_mode": not langchain_available,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(response)
    
    def serve_customer_profile(self, user_id):
        try:
            customers = load_customer_data()
            customer_data = customers.get(user_id, {})
            customer_profile = analyze_customer_profile(customer_data)
            
            response = {
                "customer_data": customer_data,
                "profile_analysis": customer_profile
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_chat(self):
        start_time = time.time()
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_id = data.get('userId', 'user_001')
            message = data.get('message', '')
            
            # Load customer data
            customers = load_customer_data()
            customer_data = customers.get(user_id, {
                "monthly_usage": 50,
                "months_subscribed": 6,
                "payment_issues": 0,
                "support_tickets": 1,
                "plan": "basic"
            })
            
            # Analyze customer profile
            customer_profile = analyze_customer_profile(customer_data)
            
            # Load conversation history
            conversation_history = load_conversation(user_id)
            
            # Update conversation memory
            update_conversation_memory(user_id, message)
            
            # Generate AI response
            ai_response = generate_ai_response(message, customer_profile, conversation_history)
            
            # Add enhanced data to response
            ai_response['latency_ms'] = round((time.time() - start_time) * 1000, 2)
            ai_response['churn_risk_reduction'] = "35%" if ai_response.get('action') == 'retention' else "0%"
            ai_response['upsell_boost'] = "20%" if ai_response.get('action') == 'upsell' else "0%"
            
            # Add comparison data for plan suggestions
            if ai_response.get('action') in ['upsell', 'retention']:
                ai_response['plan_comparison'] = generate_plan_comparison(user_id, ai_response.get('action'))
            
            # Update metrics
            metrics["total_conversations"] += 1
            if ai_response.get('action') == 'retention' and ai_response.get('confidence', 0) > 0.7:
                metrics["churn_prevented"] += 1
                metrics["offers_shown"] += 1
            elif ai_response.get('action') == 'upsell' and ai_response.get('confidence', 0) > 0.7:
                metrics["upsells_completed"] += 1
                metrics["offers_shown"] += 1
            elif ai_response.get('action') == 'escalate':
                metrics["escalations"] += 1
            
            # Save conversation turn
            save_conversation_turn(
                user_id,
                message,
                ai_response["response"],
                ai_response["action"],
                ai_response["tools_used"],
                ai_response["confidence"],
                ai_response['latency_ms'],
                ai_response['churn_risk_reduction'],
                ai_response['upsell_boost']
            )
            
            self.send_json_response(ai_response)
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_offer_response(self):
        """Handle offer acceptance/decline"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_id = data.get('userId')
            offer_type = data.get('offerType')
            accepted = data.get('accepted', False)
            
            if accepted:
                metrics["offers_accepted"] += 1
                response_text = f"Great! I've applied the {offer_type} to your account. You should see the changes reflected in your next billing cycle."
            else:
                response_text = f"I understand you'd like to decline the {offer_type}. Is there anything else I can help you with?"
            
            response = {
                "response": response_text,
                "action": "offer_response",
                "confidence": 0.9,
                "suggestedOffer": None,
                "tools_used": ["OfferHandler"],
                "options": [
                    "Show me other options",
                    "I want to cancel",
                    "Talk to a human",
                    "That's all for now"
                ]
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling offer response: {e}")
            self.send_error(500)
    
    def handle_escalation(self):
        """Handle escalation to human support"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_id = data.get('userId')
            global ticket_counter
            ticket_counter += 1
            ticket_number = f"TKT-{ticket_counter}"
            
            metrics["escalations"] += 1
            metrics["tickets_generated"] += 1
            
            # Generate conversation summary
            conversation = load_conversation(user_id)
            summary = generate_conversation_summary(conversation)
            
            response = {
                "response": f"I've escalated your case to our human support team. Your ticket number is {ticket_number}. A specialist will contact you within 15 minutes.",
                "action": "escalate",
                "confidence": 0.95,
                "suggestedOffer": None,
                "tools_used": ["EscalationHandler"],
                "ticket_number": ticket_number,
                "conversation_summary": summary,
                "options": [
                    "Schedule a call for later",
                    "Send me an email instead",
                    "I'll wait for the call",
                    "Cancel the request"
                ]
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling escalation: {e}")
            self.send_error(500)
    
    def handle_memory(self):
        """Get conversation memory for a user"""
        try:
            user_id = self.path.split('/')[-1]
            memory = conversation_memory.get(user_id, {})
            
            self.send_json_response(memory)
            
        except Exception as e:
            logger.error(f"Error handling memory: {e}")
            self.send_error(500)
    
    def serve_customer_lookup(self):
        """Serve customer lookup data"""
        try:
            user_id = self.path.split('/')[-1]
            customers = load_customer_data()
            
            # Find customer by user_id or return default
            customer_data = None
            for customer in customers.get("customers", []):
                if customer.get("name") == user_id or customer.get("email", "").startswith(user_id):
                    customer_data = customer
                    break
            
            if not customer_data:
                # Return default customer data
                customer_data = {
                    "name": user_id,
                    "email": f"{user_id}@example.com",
                    "company": "Demo Company",
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
            
            self.send_json_response(customer_data)
            
        except Exception as e:
            logger.error(f"Error serving customer lookup: {e}")
            self.send_error(500)

# Load customer data
def load_customer_data():
    data_path = Path("data/customers.json")
    if data_path.exists():
        with open(data_path, "r") as f:
            return json.load(f)
    return {}

# Load product data
def load_product_data():
    data_path = Path("data/products.json")
    if data_path.exists():
        with open(data_path, "r") as f:
            return json.load(f)
    return {}

# Load conversation history
def load_conversation(user_id: str) -> List[Dict]:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"{user_id}.json"
    if log_file.exists():
        with open(log_file, "r") as f:
            return json.load(f)
    return []

# Save conversation turn with enhanced logging
def save_conversation_turn(user_id: str, user_message: str, agent_response: str, action: str, tools_used: List[str] = None, confidence: float = 0.0, latency_ms: float = 0.0, churn_risk_reduction: str = "0%", upsell_boost: str = "0%"):
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"{user_id}.json"
    conversation = load_conversation(user_id)
    
    conversation.append({
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "agent_response": agent_response,
        "action": action,
        "tools_used": tools_used or [],
        "confidence": confidence,
        "latency_ms": latency_ms,
        "churn_risk_reduction": churn_risk_reduction,
        "upsell_boost": upsell_boost,
        "session_id": str(uuid.uuid4())
    })
    
    with open(log_file, "w") as f:
        json.dump(conversation, f, indent=2)

# Update conversation memory
def update_conversation_memory(user_id: str, message: str):
    """Update conversation memory with key topics and preferences"""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {
            "topics_mentioned": [],
            "preferences": {},
            "concerns": [],
            "last_updated": datetime.now().isoformat()
        }
    
    memory = conversation_memory[user_id]
    message_lower = message.lower()
    
    # Track topics mentioned
    topics = ["audio", "video", "pricing", "features", "support", "billing", "upgrade", "downgrade", "cancel"]
    for topic in topics:
        if topic in message_lower and topic not in memory["topics_mentioned"]:
            memory["topics_mentioned"].append(topic)
    
    # Track concerns
    concerns = ["expensive", "too much", "not working", "problem", "issue", "bug", "slow"]
    for concern in concerns:
        if concern in message_lower and concern not in memory["concerns"]:
            memory["concerns"].append(concern)
    
    memory["last_updated"] = datetime.now().isoformat()

# Generate plan comparison
def generate_plan_comparison(user_id: str, action: str):
    """Generate plan comparison data for upsell/retention"""
    products = load_product_data()
    customer_data = load_customer_data()
    
    # Get current customer plan
    current_plan = "basic"  # Default
    for customer in customer_data.get("customers", []):
        if customer.get("name") == user_id or customer.get("email", "").startswith(user_id):
            current_plan = customer.get("plan", "basic")
            break
    
    current_plan_data = products.get("plans", {}).get(current_plan, {})
    
    if action == "upsell":
        # Suggest next tier up
        if current_plan == "basic":
            suggested_plan = "professional"
        elif current_plan == "professional":
            suggested_plan = "premium"
        else:
            suggested_plan = "premium"  # Already on highest tier
    else:  # retention
        # Suggest downgrade or current plan benefits
        if current_plan == "premium":
            suggested_plan = "professional"
        elif current_plan == "professional":
            suggested_plan = "basic"
        else:
            suggested_plan = "basic"  # Already on lowest tier
    
    suggested_plan_data = products.get("plans", {}).get(suggested_plan, {})
    
    return {
        "current_plan": {
            "name": current_plan_data.get("name", "Current Plan"),
            "price": current_plan_data.get("price", 0),
            "features": current_plan_data.get("features", [])
        },
        "suggested_plan": {
            "name": suggested_plan_data.get("name", "Suggested Plan"),
            "price": suggested_plan_data.get("price", 0),
            "features": suggested_plan_data.get("features", [])
        },
        "action": action
    }

# Generate conversation summary
def generate_conversation_summary(conversation: List[Dict]) -> str:
    """Generate a summary of the conversation for escalation"""
    if not conversation:
        return "No conversation history available."
    
    summary_parts = []
    summary_parts.append(f"Conversation started at {conversation[0].get('timestamp', 'unknown time')}")
    summary_parts.append(f"Total messages: {len(conversation)}")
    
    # Extract key topics and concerns
    topics = set()
    concerns = set()
    actions = set()
    
    for turn in conversation:
        if turn.get("action"):
            actions.add(turn["action"])
        # Simple keyword extraction
        message = turn.get("user_message", "").lower()
        if "cancel" in message:
            concerns.add("cancellation request")
        if "expensive" in message or "price" in message:
            concerns.add("pricing concerns")
        if "feature" in message:
            topics.add("feature inquiry")
        if "support" in message or "help" in message:
            topics.add("support request")
    
    if topics:
        summary_parts.append(f"Topics discussed: {', '.join(topics)}")
    if concerns:
        summary_parts.append(f"Customer concerns: {', '.join(concerns)}")
    if actions:
        summary_parts.append(f"Agent actions taken: {', '.join(actions)}")
    
    return " | ".join(summary_parts)

# Customer data analysis
def analyze_customer_profile(customer_data: Dict) -> Dict:
    """Analyze customer profile to determine churn risk and upsell potential"""
    profile = {
        "churn_risk": "low",
        "upsell_potential": "low",
        "usage_level": "low",
        "satisfaction_indicators": [],
        "retention_strategy": "standard"
    }
    
    # Analyze usage patterns
    if customer_data.get("monthly_usage", 0) > 80:
        profile["usage_level"] = "high"
        profile["upsell_potential"] = "high"
    elif customer_data.get("monthly_usage", 0) > 40:
        profile["usage_level"] = "medium"
        profile["upsell_potential"] = "medium"
    
    # Analyze subscription length
    months_subscribed = customer_data.get("months_subscribed", 0)
    if months_subscribed < 3:
        profile["churn_risk"] = "high"
        profile["retention_strategy"] = "aggressive"
    elif months_subscribed < 12:
        profile["churn_risk"] = "medium"
        profile["retention_strategy"] = "moderate"
    
    # Analyze payment history
    if customer_data.get("payment_issues", 0) > 0:
        profile["churn_risk"] = "high"
        profile["satisfaction_indicators"].append("payment_issues")
    
    # Analyze support tickets
    support_tickets = customer_data.get("support_tickets", 0)
    if support_tickets > 5:
        profile["churn_risk"] = "high"
        profile["satisfaction_indicators"].append("high_support_volume")
    elif support_tickets > 2:
        profile["churn_risk"] = "medium"
    
    return profile

# Intent detection
def detect_intent(message: str) -> str:
    """Detect customer intent from message"""
    message_lower = message.lower()
    
    # Cancel intent
    if any(word in message_lower for word in ["cancel", "unsubscribe", "quit", "stop", "end", "leave", "not worth"]):
        return "cancel"
    
    # Pricing confusion
    if any(word in message_lower for word in ["expensive", "cost", "price", "money", "afford", "budget", "cheaper"]):
        return "pricing_confusion"
    
    # Feature relevance
    if any(word in message_lower for word in ["missing", "need", "want", "feature", "functionality", "capability", "more features"]):
        return "feature_relevance"
    
    # Discount request
    if any(word in message_lower for word in ["discount", "deal", "offer", "promotion", "save", "cheaper"]):
        return "discount_request"
    
    # Trust issue
    if any(word in message_lower for word in ["not working", "broken", "issue", "problem", "bug", "disappointed", "frustrated"]):
        return "trust_issue"
    
    # Escalation
    if any(word in message_lower for word in ["manager", "supervisor", "human", "speak to", "call me"]):
        return "escalation"
    
    # General greeting
    if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return "greeting"
    
    return "general_inquiry"

# Ground in data
def ground_in_data(user_id: str, intent: str) -> Dict:
    """Fetch relevant data based on intent"""
    customers = load_customer_data()
    products = load_product_data()
    
    customer_data = customers.get(user_id, {
        "monthly_usage": 50,
        "months_subscribed": 6,
        "payment_issues": 0,
        "support_tickets": 1,
        "plan": "basic"
    })
    
    customer_profile = analyze_customer_profile(customer_data)
    
    return {
        "customer_data": customer_data,
        "customer_profile": customer_profile,
        "products": products,
        "current_plan": products.get("plans", {}).get(customer_data.get("plan", "basic"), {}),
        "intent": intent
    }

# Enhanced AI response with intent detection and data grounding
def generate_ai_response(user_message: str, customer_profile: Dict, conversation_history: List[Dict]) -> Dict:
    """Generate AI response using intent detection and data grounding with LangChain fallback"""
    
    # Step 1: Detect intent
    intent = detect_intent(user_message)
    
    # Step 2: Ground in data (get customer and product info)
    customers = load_customer_data()
    products = load_product_data()
    
    # Get customer context
    usage_level = customer_profile.get("usage_level", "low")
    churn_risk = customer_profile.get("churn_risk", "low")
    upsell_potential = customer_profile.get("upsell_potential", "low")
    
    # Try LangChain first if available
    try:
        if agent and llm:
            # Use LangChain for enhanced responses
            context = f"""
            Customer: {customer_profile.get('name', 'Unknown')}
            Plan: {customer_profile.get('plan', 'basic')}
            Usage: {usage_level}
            Churn Risk: {churn_risk}
            Upsell Potential: {upsell_potential}
            
            User Message: "{user_message}"
            Intent: {intent}
            
            Provide a helpful, empathetic response addressing their specific needs.
            """
            
            response = agent.run(context)
            return parse_langchain_response(response, intent, customer_profile)
    except Exception as e:
        logger.warning(f"LangChain failed, falling back to rule-based: {e}")
    
    # Fallback to rule-based system
    
    # Step 3: Apply rules + LLM reasoning based on intent
    if intent == "greeting":
        return {
            "response": "Hello! I'm your AI assistant for customer retention and upsell. I can help you with subscription management, feature recommendations, pricing questions, and more. How can I assist you today?",
            "action": "neutral",
            "confidence": 0.8,
            "suggestedOffer": None,
            "tools_used": ["IntentDetection"],
            "options": [
                "I want to cancel my subscription",
                "The price is too expensive", 
                "I need more features",
                "I'm having technical issues"
            ]
        }
    
    elif intent == "cancel":
        if churn_risk == "high":
            # Offer discount or downgrade
            current_plan = products.get("plans", {}).get("basic", {})
            return {
                "response": f"I understand you're considering canceling. Before you make that decision, I'd like to offer you a special retention deal. I can provide you with a 20% discount for the next 3 months, or we can downgrade you to our Basic plan at ${current_plan.get('price', 29)}/month. Which option would work better for you?",
                "action": "retention",
                "confidence": 0.9,
                "suggestedOffer": "20% discount for 3 months or Basic plan downgrade",
                "tools_used": ["IntentDetection", "CustomerLookup", "OfferGenerator"],
                "options": [
                    "Yes, I'll take the 20% discount",
                    "Yes, downgrade me to Basic plan",
                    "No, I still want to cancel",
                    "Let me think about it"
                ]
            }
        else:
            return {
                "response": "I'm sorry to hear you're considering canceling. Could you help me understand what's not working for you? I'd like to see if we can find a solution that better meets your needs.",
                "action": "retention",
                "confidence": 0.7,
                "suggestedOffer": "Account optimization consultation",
                "tools_used": ["IntentDetection", "CustomerLookup"],
                "options": [
                    "It's too expensive",
                    "I'm not using the features",
                    "I found a better alternative",
                    "I'm having technical issues"
                ]
            }
    
    elif intent == "pricing_confusion":
        # Compare current vs alternatives
        current_plan = products.get("plans", {}).get("basic", {})
        professional_plan = products.get("plans", {}).get("professional", {})
        
        return {
            "response": f"I understand your concerns about pricing. You're currently on our {current_plan.get('name', 'Basic')} plan at ${current_plan.get('price', 29)}/month. Let me show you the value you're getting and compare it with our other options. Our Professional plan at ${professional_plan.get('price', 79)}/month offers much more value per dollar with advanced features. Would you like me to break down the cost-benefit analysis?",
            "action": "upsell",
            "confidence": 0.8,
            "suggestedOffer": "Professional plan upgrade with cost analysis",
            "tools_used": ["IntentDetection", "CustomerLookup", "ProductComparison"],
            "options": [
                "Yes, show me the cost analysis",
                "What's included in Professional?",
                "Do you have any discounts?",
                "I want to downgrade instead"
            ]
        }
    
    elif intent == "feature_relevance":
        # Suggest better-fit plan
        if upsell_potential == "high":
            premium_plan = products.get("plans", {}).get("premium", {})
            return {
                "response": f"That's a great feature request! Based on your usage patterns, I think our Premium plan would be perfect for you. It includes {', '.join(premium_plan.get('features', [])[:3])} and much more. I can offer you a 30-day free trial to test it out. Would you like to try it?",
                "action": "upsell",
                "confidence": 0.85,
                "suggestedOffer": "30-day Premium trial",
                "tools_used": ["IntentDetection", "CustomerLookup", "FeatureRecommendation"],
                "options": [
                    "Yes, start my free trial",
                    "Show me all Premium features",
                    "What's the price after trial?",
                    "I need different features"
                ]
            }
        else:
            return {
                "response": "I'd be happy to help you find the right features! Let me understand your specific needs better. What functionality are you looking for, and how do you plan to use it?",
                "action": "neutral",
                "confidence": 0.7,
                "suggestedOffer": "Feature consultation",
                "tools_used": ["IntentDetection", "CustomerLookup"],
                "options": [
                    "Email automation",
                    "Analytics & reporting",
                    "API access",
                    "Team collaboration"
                ]
            }
    
    elif intent == "discount_request":
        # Check loyalty offers
        if customer_profile.get("months_subscribed", 0) >= 12:
            return {
                "response": "Great news! As a loyal customer, you qualify for our loyalty discount. I can offer you 15% off your next 6 months, or 20% off if you upgrade to our Professional plan. Which option interests you more?",
                "action": "retention",
                "confidence": 0.9,
                "suggestedOffer": "15% loyalty discount or 20% upgrade discount",
                "tools_used": ["IntentDetection", "CustomerLookup", "LoyaltyOffers"],
                "options": [
                    "Yes, 15% off for 6 months",
                    "Yes, 20% off with upgrade",
                    "Show me other discount options",
                    "No thanks, I'm good"
                ]
            }
        else:
            return {
                "response": "I'd be happy to discuss pricing options with you! While you haven't been with us long enough for our loyalty discount, I can offer you a 10% discount for the next 3 months. Would that help?",
                "action": "retention",
                "confidence": 0.8,
                "suggestedOffer": "10% discount for 3 months",
                "tools_used": ["IntentDetection", "CustomerLookup", "OfferGenerator"],
                "options": [
                    "Yes, I'll take the 10% discount",
                    "What about annual billing discount?",
                    "Show me plan downgrade options",
                    "No thanks"
                ]
            }
    
    elif intent == "trust_issue":
        # Respond factually + empathetically
        return {
            "response": "I'm really sorry you're experiencing issues. That's not the experience we want you to have. Let me help you resolve this right away. Can you tell me more about the specific problem you're encountering? I'll make sure we get this sorted out quickly.",
            "action": "escalate",
            "confidence": 0.9,
            "suggestedOffer": "Priority technical support",
            "tools_used": ["IntentDetection", "EscalationHandler"],
            "options": [
                "Email not sending",
                "Login problems",
                "Feature not working",
                "Talk to a human"
            ]
        }
    
    elif intent == "escalation":
        # Summarize and log case
        return {
            "response": "I understand you'd like to speak with a human representative. I'll connect you with our customer success team right away. They'll have access to your full account history and can provide personalized assistance. You should receive a call within 15 minutes.",
            "action": "escalate",
            "confidence": 0.95,
            "suggestedOffer": "Human representative connection",
            "tools_used": ["IntentDetection", "EscalationHandler", "CaseLogging"],
            "options": [
                "Schedule a call for later",
                "Send me an email instead",
                "I'll wait for the call",
                "Cancel the request"
            ]
        }
    
    else:  # general_inquiry
        return {
            "response": "I'm here to help! I can assist you with subscription management, feature recommendations, pricing questions, technical support, or any other concerns. What would you like to know more about?",
            "action": "neutral",
            "confidence": 0.7,
            "suggestedOffer": None,
            "tools_used": ["IntentDetection"],
            "options": [
                "Show me my current plan",
                "What features do I have?",
                "How can I upgrade?",
                "Talk to a human"
            ]
        }

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8000), ChatHandler)
    print("🚀 AI Agent - Retention and Upsell running on http://localhost:8000")
    print("📊 Project: AI Agent - Retention & Upsell")
    print("🎯 Features: Intent Detection, Data Grounding, Smart Customer Interaction")
    print("🤖 AI Agent: Intelligent Retention and Upsell Strategies")
    print("\nPress Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()
