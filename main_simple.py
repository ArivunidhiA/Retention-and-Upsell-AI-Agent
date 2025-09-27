from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Retention & Upsell Agent", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    userId: str
    message: str

class ChatResponse(BaseModel):
    response: str
    action: str  # "retention", "upsell", "escalate", "neutral"
    confidence: float
    suggestedOffer: Optional[str] = None
    tools_used: Optional[List[str]] = None

# Load customer data
def load_customer_data():
    data_path = Path("data/customers.json")
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
def save_conversation_turn(user_id: str, user_message: str, agent_response: str, action: str, tools_used: List[str] = None, confidence: float = 0.0):
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
        "session_id": str(uuid.uuid4())
    })
    
    with open(log_file, "w") as f:
        json.dump(conversation, f, indent=2)

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

# Enhanced AI response for demo purposes
def generate_ai_response(user_message: str, customer_profile: Dict, conversation_history: List[Dict]) -> Dict:
    """Generate AI response based on customer profile and message analysis"""
    
    message_lower = user_message.lower()
    
    # Churn signals
    churn_keywords = ["cancel", "unsubscribe", "quit", "stop", "end", "leave", "not worth", "too expensive", "disappointed"]
    price_keywords = ["expensive", "cost", "price", "money", "afford", "budget"]
    feature_keywords = ["missing", "need", "want", "feature", "functionality", "capability", "more features"]
    api_keywords = ["api", "integration", "connect", "webhook"]
    automation_keywords = ["automation", "workflow", "trigger", "automate"]
    support_keywords = ["help", "support", "issue", "problem", "bug", "broken"]
    
    has_churn_signal = any(keyword in message_lower for keyword in churn_keywords)
    has_price_concern = any(keyword in message_lower for keyword in price_keywords)
    has_feature_request = any(keyword in message_lower for keyword in feature_keywords)
    has_api_request = any(keyword in message_lower for keyword in api_keywords)
    has_automation_request = any(keyword in message_lower for keyword in automation_keywords)
    has_support_request = any(keyword in message_lower for keyword in support_keywords)
    
    # Get customer context
    usage_level = customer_profile.get("usage_level", "low")
    churn_risk = customer_profile.get("churn_risk", "low")
    upsell_potential = customer_profile.get("upsell_potential", "low")
    
    # Determine action based on profile and message
    if has_churn_signal and churn_risk == "high":
        if has_price_concern:
            return {
                "response": f"I completely understand your concerns about pricing. Looking at your account, I can see you're a {usage_level}-value customer. I can offer you a special 20% discount for the next 3 months to help you get more value from CloudFlow Pro. This would bring your monthly cost down significantly while you explore all our features. Would this help address your concerns?",
                "action": "retention",
                "confidence": 0.9,
                "suggestedOffer": "20% discount for 3 months",
                "tools_used": ["CustomerLookup", "OfferGenerator"]
            }
        else:
            return {
                "response": "I'm sorry to hear you're considering canceling. I'd love to understand what's not working for you so I can help find a solution. Sometimes a quick feature walkthrough or account optimization can make a big difference. Could you tell me more about what's not meeting your expectations?",
                "action": "retention",
                "confidence": 0.8,
                "suggestedOffer": "Account optimization consultation",
                "tools_used": ["CustomerLookup"]
            }
    
    elif has_price_concern and usage_level == "high":
        return {
            "response": f"I see you're getting great value from CloudFlow Pro with your {usage_level} usage! Instead of canceling, have you considered our Premium plan? It offers even more features and better value per dollar. I can offer you a 15% discount on the upgrade for the first year. This would give you access to advanced analytics, API access, and priority support.",
            "action": "upsell",
            "confidence": 0.85,
            "suggestedOffer": "Premium plan upgrade with 15% first-year discount",
            "tools_used": ["CustomerLookup", "OfferGenerator"]
        }
    
    elif has_feature_request and upsell_potential == "high":
        return {
            "response": "That's a great feature request! Actually, that functionality is available in our Premium plan. Given how actively you're using CloudFlow Pro, upgrading would give you access to that feature plus many others like advanced analytics, API access, and custom integrations. I can offer you a free 30-day trial of Premium so you can test it out. Would you like to try it?",
            "action": "upsell",
            "confidence": 0.8,
            "suggestedOffer": "30-day Premium trial",
            "tools_used": ["CustomerLookup", "OfferGenerator"]
        }
    
    elif has_api_request:
        return {
            "response": "Great question about API access! Our API is available in the Professional and Premium plans. It allows you to integrate CloudFlow Pro with your existing systems, create custom workflows, and automate data synchronization. Would you like me to show you what's included in our Professional plan ($99/month) or Premium plan ($299/month)?",
            "action": "upsell",
            "confidence": 0.8,
            "suggestedOffer": "API access with Professional or Premium plan",
            "tools_used": ["CustomerLookup", "OfferGenerator"]
        }
    
    elif has_automation_request:
        return {
            "response": "CloudFlow Pro's automation features are perfect for streamlining your workflows! Our Professional plan includes advanced automation with triggers, conditions, and multi-step workflows. You can automate email sequences, data processing, and integrate with other tools. Would you like to see a demo of our automation capabilities?",
            "action": "upsell",
            "confidence": 0.8,
            "suggestedOffer": "Automation features with Professional plan",
            "tools_used": ["CustomerLookup", "OfferGenerator"]
        }
    
    elif has_support_request:
        return {
            "response": "I'm here to help! For technical issues, I can connect you with our support team. For account questions, I can assist you directly. What specific issue are you experiencing? If it's something I can't resolve, I'll make sure you get connected with the right specialist.",
            "action": "escalate",
            "confidence": 0.7,
            "suggestedOffer": "Direct support connection",
            "tools_used": ["EscalationHandler"]
        }
    
    elif has_churn_signal:
        return {
            "response": "I understand you're having some concerns. I'm here to help make sure you're getting the most value from CloudFlow Pro. Could you help me understand what specific issues you're facing? I want to make sure we address them properly.",
            "action": "retention",
            "confidence": 0.7,
            "suggestedOffer": "Personalized solution consultation",
            "tools_used": ["CustomerLookup"]
        }
    
    else:
        return {
            "response": "Thank you for reaching out! I'm here to help with any questions or concerns you might have about your CloudFlow Pro subscription. How can I assist you today?",
            "action": "neutral",
            "confidence": 0.6,
            "suggestedOffer": None,
            "tools_used": []
        }

# Mount static files (frontend build)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# API Routes
@app.get("/")
async def root():
    """Serve the main React app"""
    return FileResponse("dist/index.html")

@app.get("/api/")
async def api_root():
    return {"message": "AI Retention & Upsell Agent API v2.0", "status": "running", "langchain": "demo_mode"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Load customer data
        customers = load_customer_data()
        customer_data = customers.get(request.userId, {
            "monthly_usage": 50,
            "months_subscribed": 6,
            "payment_issues": 0,
            "support_tickets": 1,
            "plan": "basic"
        })
        
        # Analyze customer profile
        customer_profile = analyze_customer_profile(customer_data)
        
        # Load conversation history
        conversation_history = load_conversation(request.userId)
        
        # Generate AI response
        ai_response = generate_ai_response(request.message, customer_profile, conversation_history)
        
        # Save conversation turn
        save_conversation_turn(
            request.userId,
            request.message,
            ai_response["response"],
            ai_response["action"],
            ai_response["tools_used"],
            ai_response["confidence"]
        )
        
        return ChatResponse(**ai_response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/customer/{user_id}")
async def get_customer_profile(user_id: str):
    """Get customer profile for debugging"""
    try:
        customers = load_customer_data()
        customer_data = customers.get(user_id, {})
        customer_profile = analyze_customer_profile(customer_data)
        
        return {
            "customer_data": customer_data,
            "profile_analysis": customer_profile
        }
            
    except Exception as e:
        logger.error(f"Error getting customer profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving customer profile: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "langchain_initialized": False,
        "vectorstore_ready": False,
        "demo_mode": True,
        "timestamp": datetime.now().isoformat()
    }

# Catch-all route for React Router
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React app for all other routes"""
    return FileResponse("dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
