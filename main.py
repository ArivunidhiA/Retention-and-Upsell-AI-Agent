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

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain.tools import Tool
from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.callbacks.base import BaseCallbackHandler

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

# Global variables for LangChain components
vectorstore = None
agent = None
llm = None

# Custom callback handler for logging
class LoggingCallbackHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized: Dict[str, any], input_str: str, **kwargs) -> None:
        logger.info(f"Tool started: {serialized.get('name', 'Unknown')} with input: {input_str}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        logger.info(f"Tool ended with output: {output}")

    def on_agent_action(self, action, **kwargs) -> None:
        logger.info(f"Agent action: {action.tool} with input: {action.tool_input}")

# Initialize LangChain components
def initialize_langchain():
    global vectorstore, agent, llm
    
    try:
        # Load customer data with LangChain
        logger.info("Loading customer data...")
        loader = JSONLoader(file_path="data/customers.json", jq_schema=".[]")
        docs = loader.load()
        
        # Enhance documents with metadata
        enhanced_docs = []
        for doc in docs:
            customer_data = doc.metadata
            # Create a more detailed document for better retrieval
            content = f"""
            Customer: {customer_data.get('name', 'Unknown')} from {customer_data.get('company', 'Unknown Company')}
            Email: {customer_data.get('email', 'N/A')}
            Industry: {customer_data.get('industry', 'N/A')}
            Plan: {customer_data.get('plan', 'basic')} - ${customer_data.get('subscription_value', 0)}/month
            Monthly Usage: {customer_data.get('monthly_usage', 0)}%
            Months Subscribed: {customer_data.get('months_subscribed', 0)}
            Payment Issues: {customer_data.get('payment_issues', 0)}
            Support Tickets: {customer_data.get('support_tickets', 0)}
            Revenue Impact: {customer_data.get('revenue_impact', 'medium')}
            Features Used: {', '.join(customer_data.get('feature_usage', []))}
            Last Login: {customer_data.get('last_login', 'N/A')}
            
            Profile Analysis:
            - Usage Level: {'High' if customer_data.get('monthly_usage', 0) > 80 else 'Medium' if customer_data.get('monthly_usage', 0) > 40 else 'Low'}
            - Churn Risk: {'High' if customer_data.get('months_subscribed', 0) < 3 or customer_data.get('payment_issues', 0) > 0 or customer_data.get('support_tickets', 0) > 5 else 'Medium' if customer_data.get('months_subscribed', 0) < 12 or customer_data.get('support_tickets', 0) > 2 else 'Low'}
            - Upsell Potential: {'High' if customer_data.get('monthly_usage', 0) > 80 else 'Medium' if customer_data.get('monthly_usage', 0) > 40 else 'Low'}
            - Customer Value: {customer_data.get('revenue_impact', 'medium').title()}
            """
            
            enhanced_doc = Document(
                page_content=content,
                metadata={
                    **customer_data,
                    'customer_id': customer_data.get('name', 'Unknown'),
                    'usage_level': 'High' if customer_data.get('monthly_usage', 0) > 80 else 'Medium' if customer_data.get('monthly_usage', 0) > 40 else 'Low',
                    'churn_risk': 'High' if customer_data.get('months_subscribed', 0) < 3 or customer_data.get('payment_issues', 0) > 0 or customer_data.get('support_tickets', 0) > 5 else 'Medium' if customer_data.get('months_subscribed', 0) < 12 or customer_data.get('support_tickets', 0) > 2 else 'Low',
                    'upsell_potential': 'High' if customer_data.get('monthly_usage', 0) > 80 else 'Medium' if customer_data.get('monthly_usage', 0) > 40 else 'Low'
                }
            )
            enhanced_docs.append(enhanced_doc)
        
        # Create embeddings and vector store
        logger.info("Creating embeddings and vector store...")
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(enhanced_docs, embeddings)
        
        # Initialize LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")
        
        # Create retrieval QA chain
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa = RetrievalQA.from_chain_type(
            llm=llm, 
            retriever=retriever,
            return_source_documents=True
        )
        
        # Define custom tools
        def customer_lookup(query: str) -> str:
            """Look up customer details by name, ID, or characteristics"""
            try:
                result = qa.run(query)
                return result
            except Exception as e:
                logger.error(f"Error in customer lookup: {e}")
                return f"Error looking up customer: {str(e)}"
        
        def offer_generator(query: str) -> str:
            """Generate retention or upsell offers based on customer profile and query"""
            try:
                # Analyze the query for offer type
                query_lower = query.lower()
                
                if any(word in query_lower for word in ["cancel", "unsubscribe", "quit", "stop", "leave"]):
                    if any(word in query_lower for word in ["expensive", "cost", "price", "money"]):
                        return "Retention Offer: 20% discount for 3 months + free month extension"
                    else:
                        return "Retention Offer: Account optimization consultation + feature walkthrough"
                elif any(word in query_lower for word in ["upgrade", "premium", "features", "more"]):
                    return "Upsell Offer: Premium plan upgrade with 15% first-year discount + 30-day free trial"
                elif any(word in query_lower for word in ["expensive", "cost", "price"]):
                    return "Retention Offer: 20% discount for 3 months + value demonstration"
                else:
                    return "General Offer: Personalized solution consultation + account review"
            except Exception as e:
                logger.error(f"Error in offer generation: {e}")
                return "Standard retention offer: 15% discount for 2 months"
        
        def escalation_handler(query: str) -> str:
            """Handle complex issues that require human intervention"""
            try:
                complex_keywords = ["bug", "broken", "not working", "error", "technical", "complex", "refund", "billing"]
                if any(word in query.lower() for word in complex_keywords):
                    return "Escalation: Connecting you with a human specialist who can resolve this technical issue immediately"
                else:
                    return "No escalation needed - AI agent can handle this request"
            except Exception as e:
                logger.error(f"Error in escalation handler: {e}")
                return "Escalation: Connecting you with a human agent"
        
        # Create tools
        tools = [
            Tool(
                name="CustomerLookup",
                func=customer_lookup,
                description="Looks up customer details, usage patterns, subscription history, and risk profile. Use this to understand the customer's current situation."
            ),
            Tool(
                name="OfferGenerator",
                func=offer_generator,
                description="Generates appropriate retention or upsell offers based on customer profile and their specific concerns or requests."
            ),
            Tool(
                name="EscalationHandler",
                func=escalation_handler,
                description="Determines if a customer issue requires human intervention or can be handled by the AI agent."
            )
        ]
        
        # Initialize agent with tools
        logger.info("Initializing LangChain agent...")
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            callbacks=[LoggingCallbackHandler()]
        )
        
        logger.info("LangChain initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing LangChain: {e}")
        raise e

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

# Mount static files (frontend build)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# API Routes
@app.get("/")
async def root():
    """Serve the main React app"""
    return FileResponse("dist/index.html")

@app.get("/api/")
async def api_root():
    return {"message": "AI Retention & Upsell Agent API v2.0", "status": "running", "langchain": "enabled"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="LangChain agent not initialized")
        
        # Prepare context for the agent
        conversation_history = load_conversation(request.userId)
        context = f"""
        You are an AI Retention & Upsell Agent for CloudFlow Pro, a comprehensive business automation platform that helps companies streamline their operations with email marketing, analytics, automation, and integrations.
        
        CloudFlow Pro offers:
        - Basic Plan ($49/month): Email campaigns, basic analytics, 1,000 contacts
        - Professional Plan ($99/month): Advanced analytics, automation, 10,000 contacts, API access
        - Premium Plan ($299/month): Custom integrations, priority support, unlimited contacts, advanced features
        
        Customer ID: {request.userId}
        
        Recent conversation history:
        {json.dumps(conversation_history[-3:], indent=2) if conversation_history else 'No previous conversation'}
        
        User message: "{request.message}"
        
        Your task:
        1. Use the CustomerLookup tool to understand the customer's profile and situation
        2. Use the OfferGenerator tool to suggest appropriate offers based on their concerns
        3. Use the EscalationHandler tool if the issue requires human intervention
        4. Provide a helpful, empathetic response that addresses their specific needs
        5. Be specific about offers and next steps
        
        Guidelines:
        - Always be empathetic and understanding
        - Address their concerns directly
        - Offer specific solutions with clear benefits
        - Use a professional but friendly tone
        - If suggesting offers, be specific about what they get and how it helps
        - If escalating, explain why and what to expect
        - Reference CloudFlow Pro features and benefits when relevant
        """
        
        # Run the agent
        response = agent.run(context)
        
        # Parse response to determine action and confidence
        response_lower = response.lower()
        
        # Determine action type
        if "escalation" in response_lower or "human" in response_lower:
            action = "escalate"
            confidence = 0.9
        elif any(word in response_lower for word in ["discount", "offer", "retention", "keep"]):
            action = "retention"
            confidence = 0.8
        elif any(word in response_lower for word in ["upgrade", "premium", "upsell", "enhance"]):
            action = "upsell"
            confidence = 0.8
        else:
            action = "neutral"
            confidence = 0.6
        
        # Extract suggested offer if present
        suggested_offer = None
        if "offer:" in response_lower:
            offer_start = response_lower.find("offer:")
            offer_text = response[offer_start:offer_start + 200]
            suggested_offer = offer_text.split(":")[1].strip() if ":" in offer_text else None
        
        # Extract tools used (simplified - in production you'd track this from callbacks)
        tools_used = []
        if "customerlookup" in response_lower:
            tools_used.append("CustomerLookup")
        if "offergenerator" in response_lower:
            tools_used.append("OfferGenerator")
        if "escalationhandler" in response_lower:
            tools_used.append("EscalationHandler")
        
        # Save conversation turn
        save_conversation_turn(
            request.userId,
            request.message,
            response,
            action,
            tools_used,
            confidence
        )
        
        return ChatResponse(
            response=response,
            action=action,
            confidence=confidence,
            suggestedOffer=suggested_offer,
            tools_used=tools_used
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/customer/{user_id}")
async def get_customer_profile(user_id: str):
    """Get customer profile for debugging"""
    try:
        if not vectorstore:
            raise HTTPException(status_code=500, detail="Vector store not initialized")
        
        # Search for customer in vector store
        docs = vectorstore.similarity_search(f"customer {user_id}", k=1)
        
        if docs:
            return {
                "customer_data": docs[0].metadata,
                "profile_analysis": {
                    "usage_level": docs[0].metadata.get("usage_level", "Unknown"),
                    "churn_risk": docs[0].metadata.get("churn_risk", "Unknown"),
                    "upsell_potential": docs[0].metadata.get("upsell_potential", "Unknown")
                }
            }
        else:
            return {"message": "Customer not found", "customer_data": {}, "profile_analysis": {}}
            
    except Exception as e:
        logger.error(f"Error getting customer profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving customer profile: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "langchain_initialized": agent is not None,
        "vectorstore_ready": vectorstore is not None,
        "timestamp": datetime.now().isoformat()
    }

# Catch-all route for React Router
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React app for all other routes"""
    return FileResponse("dist/index.html")

# Initialize LangChain on startup
@app.on_event("startup")
async def startup_event():
    """Initialize LangChain components on startup"""
    try:
        initialize_langchain()
        logger.info("Application startup complete!")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        # Don't raise the exception to allow the app to start
        # The health check will indicate if LangChain is properly initialized

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)