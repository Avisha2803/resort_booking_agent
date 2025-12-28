from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from .database import get_db
from .models import Order, ServiceRequest, MenuItem
from .agents import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Eco Resort Agent System")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    agent_type: Optional[str] = None

class OrderUpdate(BaseModel):
    status: str

class ServiceRequestUpdate(BaseModel):
    status: str

# --- Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - ALWAYS use agent system
    """
    try:
        logger.info(f"Chat request for session: {request.session_id}")
        
        # ALWAYS use agent manager - no direct handling
        response_text = manager.chat(request.history, request.session_id)
        
        # Simple agent type detection for response
        last_user_message = ""
        if request.history:
            for msg in reversed(request.history):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "").lower()
                    break
        
        agent_type = "Receptionist"
        if any(word in last_user_message for word in ["menu", "order", "food", "restaurant"]):
            agent_type = "Restaurant"
        elif any(word in last_user_message for word in ["service", "clean", "towel"]):
            agent_type = "RoomService"
        
        return ChatResponse(response=response_text, agent_type=agent_type)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    room_number: Optional[str] = None,
    limit: Optional[int] = 100
):
    """Get orders with filtering"""
    try:
        query = db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        if room_number:
            query = query.filter(Order.room_number == room_number)
        
        query = query.order_by(Order.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        orders = query.all()
        
        # Convert to dict
        result = []
        for order in orders:
            order_dict = {
                "id": order.id,
                "room_number": order.room_number,
                "items": order.items if order.items else [],
                "total_amount": float(order.total_amount) if order.total_amount else 0.0,
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None
            }
            result.append(order_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail="Error fetching orders")

@app.put("/orders/{order_id}")
def update_order(
    order_id: int, 
    update: OrderUpdate, 
    db: Session = Depends(get_db)
):
    """Update order status"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        valid_statuses = ["Pending", "Preparing", "Delivered", "Cancelled"]
        if update.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        order.status = update.status
        db.commit()
        
        logger.info(f"Order {order_id} updated to: {update.status}")
        
        return {"message": "Order updated successfully", "order_id": order_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating order")

@app.get("/requests")
def get_requests(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    room_number: Optional[str] = None,
    limit: Optional[int] = 100
):
    """Get service requests"""
    try:
        query = db.query(ServiceRequest)
        
        if status:
            query = query.filter(ServiceRequest.status == status)
        if room_number:
            query = query.filter(ServiceRequest.room_number == room_number)
        
        query = query.order_by(ServiceRequest.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        requests = query.all()
        
        # Convert to dict
        result = []
        for req in requests:
            req_dict = {
                "id": req.id,
                "room_number": req.room_number,
                "request_type": req.request_type,
                "details": req.details,
                "status": req.status,
                "created_at": req.created_at.isoformat() if req.created_at else None
            }
            result.append(req_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching requests: {e}")
        raise HTTPException(status_code=500, detail="Error fetching requests")

@app.put("/requests/{request_id}")
def update_request(
    request_id: int, 
    update: ServiceRequestUpdate, 
    db: Session = Depends(get_db)
):
    """Update request status"""
    try:
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        valid_statuses = ["Pending", "In Progress", "Completed", "Cancelled"]
        if update.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        request.status = update.status
        db.commit()
        
        logger.info(f"Request {request_id} updated to: {update.status}")
        
        return {"message": "Request updated successfully", "request_id": request_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating request {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating request")

# --- Direct Menu Endpoint (Optional) ---
@app.get("/menu")
def get_menu_direct():
    """Direct menu endpoint for dashboard/testing"""
    try:
        from .tools import get_menu_items
        menu_text = get_menu_items(compact=False)
        return {"menu": menu_text}
    except Exception as e:
        logger.error(f"Error getting menu: {e}")
        raise HTTPException(status_code=500, detail="Error fetching menu")

# --- Health Check ---
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check"""
    try:
        db.execute("SELECT 1")
        
        order_count = db.query(Order).count()
        request_count = db.query(ServiceRequest).count()
        menu_count = db.query(MenuItem).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "orders": order_count,
                "requests": request_count,
                "menu_items": menu_count
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# --- Root ---
@app.get("/")
async def root():
    return {
        "message": "Eco Resort Agent System",
        "version": "1.0",
        "endpoints": {
            "chat": "POST /chat",
            "orders": "GET /orders",
            "requests": "GET /requests",
            "menu": "GET /menu",
            "health": "GET /health"
        }
    }

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    logger.info("API starting up...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)