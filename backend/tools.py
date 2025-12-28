from sqlalchemy.orm import Session
from datetime import datetime
import random
import logging
from .models import MenuItem, Order, ServiceRequest
from .database import SessionLocal

logger = logging.getLogger(__name__)

def get_db_session():
    """Get database session"""
    try:
        return SessionLocal()
    except:
        return None

# --- Receptionist Tools ---
def check_room_availability(room_type: str = None) -> str:
    """Check room availability"""
    try:
        if room_type:
            room_type = room_type.lower()
            
            room_data = {
                "deluxe": {"price": 250, "available": random.choice([True, True, False])},
                "suite": {"price": 500, "available": random.choice([True, False, False])},
                "standard": {"price": 150, "available": random.choice([True, True, True])},
                "premium": {"price": 350, "available": random.choice([True, True, False])}
            }
            
            matched_type = "standard"
            for key in room_data:
                if key in room_type:
                    matched_type = key
                    break
            
            data = room_data.get(matched_type, room_data["standard"])
            
            if data["available"]:
                return f"✅ {matched_type.capitalize()} rooms available at ₹{data['price']}/night."
            else:
                return f"❌ {matched_type.capitalize()} rooms are currently full."
        
        else:
            return """🏨 **Room Availability:**
• Standard: ₹150/night (Available)
• Deluxe: ₹250/night (Available) 
• Premium: ₹350/night (Limited)
• Suite: ₹500/night (Full)

Check-in: 2:00 PM, Check-out: 11:00 AM"""
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Unable to check room availability."

def get_facility_info(facility_name: str) -> str:
    """Get facility information"""
    try:
        facility_name = facility_name.lower().strip()
        
        facilities = {
            "gym": "🏋️ Gym: 6 AM - 10 PM (Energy-efficient equipment)",
            "spa": "💆 Spa: 10 AM - 8 PM (Organic treatments)",
            "pool": "🏊 Pool: 7 AM - 9 PM (Saltwater system)",
            "restaurant": "🍽️ Restaurant: Breakfast 7-10, Lunch 12-3, Dinner 7-11",
            "checkin": "🕐 Check-in: 2:00 PM",
            "checkout": "🕚 Check-out: 11:00 AM",
            "wifi": "📶 WiFi: Free throughout resort",
            "parking": "🅿️ Parking: Free valet, EV charging"
        }
        
        # Try to find matching facility
        for key, value in facilities.items():
            if key in facility_name:
                return value
        
        # If not found, list available facilities
        return f"Facilities: {', '.join(facilities.keys())}. Which one?"
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Unable to get facility information."

# --- Restaurant Tools ---
def get_menu_items(compact: bool = False, category: str = None) -> str:
    """Get menu"""
    db = get_db_session()
    if not db:
        return "🍽️ Menu unavailable. Please contact restaurant."
    
    try:
        items = db.query(MenuItem).order_by(MenuItem.category, MenuItem.name).all()
        
        if not items:
            return "🍽️ Menu is being updated. Please check back."
        
        if compact:
            menu_text = "🍽️ **Popular Items:**\n\n"
            
            # Group by category
            categories = {}
            for item in items:
                cat = item.category or "Other"
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            for cat in ["Breakfast", "Main Course", "Drinks"]:
                if cat in categories:
                    menu_text += f"**{cat}:**\n"
                    for item in categories[cat][:3]:
                        menu_text += f"• {item.name} - ₹{item.price}\n"
                    menu_text += "\n"
            
            menu_text += "💚 *Say 'full menu' for complete menu*"
            return menu_text
        
        else:
            menu_text = "🍽️ **RESTAURANT MENU** 🍽️\n\n"
            
            # Group by category
            categories = {}
            for item in items:
                cat = item.category or "Other"
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            for cat, cat_items in categories.items():
                menu_text += f"════════════════════\n**{cat.upper()}**\n════════════════════\n\n"
                for item in cat_items:
                    menu_text += f"• **{item.name}** - ₹{item.price}\n"
                    if item.description:
                        menu_text += f"  _{item.description}_\n"
                    menu_text += "\n"
            
            menu_text += "💚 *Compostable packaging* | 📞 *Extension 2*"
            return menu_text
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return "🍽️ Unable to load menu. Please contact restaurant."
    finally:
        db.close()

def place_restaurant_order(room_number: str, items_dict: dict) -> str:
    """Place food order"""
    db = get_db_session()
    if not db:
        return "❌ Unable to place order. Please try again."
    
    try:
        # Validate room
        if not room_number or not room_number.strip():
            return "❌ Please provide room number."
        
        room_number = room_number.strip()
        
        # Validate items
        if not items_dict:
            return "❌ No items specified."
        
        # Find menu items
        valid_items = []
        total = 0
        
        for item_name, quantity in items_dict.items():
            menu_item = db.query(MenuItem).filter(MenuItem.name.ilike(f"%{item_name}%")).first()
            if menu_item:
                item_total = menu_item.price * quantity
                total += item_total
                valid_items.append({
                    "name": menu_item.name,
                    "quantity": quantity,
                    "price": menu_item.price,
                    "total": item_total
                })
        
        if not valid_items:
            return "❌ No valid items found. Please check menu."
        
        # Create order
        order = Order(
            room_number=room_number,
            items=valid_items,
            total_amount=total,
            status="Pending",
            created_at=datetime.now()
        )
        
        db.add(order)
        db.commit()
        
        # Build response
        items_text = "\n".join([f"• {item['quantity']}x {item['name']} - ₹{item['total']}" for item in valid_items])
        
        return f"""✅ **ORDER PLACED!**
        
📋 Order #{order.id}
🏨 Room {room_number}
💰 Total: ₹{total}

**Items:**
{items_text}

⏰ Delivery: 20-30 minutes
💚 Compostable packaging used
        
Thank you for ordering!"""
        
    except Exception as e:
        db.rollback()
        logger.error(f"Order error: {e}")
        return f"❌ Order failed: {str(e)[:50]}"
    finally:
        db.close()

# --- Room Service Tools ---
def create_room_service_request(room_number: str, request_type: str, details: str = "") -> str:
    """Create service request"""
    db = get_db_session()
    if not db:
        return "❌ Unable to create request. Please try again."
    
    try:
        # Validate room
        if not room_number or not room_number.strip():
            return "❌ Please provide room number."
        
        room_number = room_number.strip()
        
        # Validate request type
        if not request_type or not request_type.strip():
            return "❌ Please specify request type."
        
        # Create request
        request = ServiceRequest(
            room_number=room_number,
            request_type=request_type,
            details=details[:200] if details else None,
            status="Pending",
            created_at=datetime.now()
        )
        
        db.add(request)
        db.commit()
        
        # Eco message based on request type
        eco_msg = ""
        request_lower = request_type.lower()
        if "clean" in request_lower:
            eco_msg = "💚 Using plant-based cleaners"
        elif "towel" in request_lower:
            eco_msg = "💚 Towel reuse saves water"
        
        return f"""✅ **SERVICE REQUESTED**
        
📋 Request #{request.id}
🏨 Room {room_number}
🔧 {request_type}
📝 {details if details else 'Standard request'}

{eco_msg}
⏰ ETA: 30 minutes
        
Thank you!"""
        
    except Exception as e:
        db.rollback()
        logger.error(f"Request error: {e}")
        return f"❌ Request failed: {str(e)[:50]}"
    finally:
        db.close()