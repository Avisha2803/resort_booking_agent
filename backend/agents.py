import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import FunctionDeclaration, Tool
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = bool(api_key and api_key.startswith("AIza"))

if GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=api_key)
        logger.info("✅ Gemini configured")
    except:
        GEMINI_AVAILABLE = False
        logger.warning("⚠️ Gemini not available, using mock mode")

# --- Conversation Memory ---
class ConversationMemory:
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        return self.conversations.get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        if metadata:
            message["metadata"] = metadata
        
        self.conversations[session_id].append(message)
        if len(self.conversations[session_id]) > 10:
            self.conversations[session_id] = self.conversations[session_id][-10:]
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        return self.user_contexts.get(session_id, {})
    
    def update_context(self, session_id: str, updates: Dict[str, Any]):
        if session_id not in self.user_contexts:
            self.user_contexts[session_id] = {}
        self.user_contexts[session_id].update(updates)

memory = ConversationMemory()

# --- Tool Definitions ---
receptionist_tools = [
    FunctionDeclaration(
        name="check_room_availability",
        description="Check room availability and prices",
        parameters={
            "type": "object",
            "properties": {
                "room_type": {"type": "string", "description": "deluxe, suite, standard, premium"}
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="get_facility_info",
        description="Get facility information",
        parameters={
            "type": "object",
            "properties": {
                "facility_name": {"type": "string", "description": "gym, spa, pool, restaurant, checkin, checkout, wifi, parking"}
            },
            "required": ["facility_name"]
        }
    )
]

restaurant_tools = [
    FunctionDeclaration(
        name="get_menu_items",
        description="Get restaurant menu",
        parameters={
            "type": "object",
            "properties": {
                "compact": {"type": "boolean", "description": "Brief menu if true"}
            },
            "required": []
        }
    ),
    FunctionDeclaration(
        name="place_restaurant_order",
        description="Place food order",
        parameters={
            "type": "object",
            "properties": {
                "room_number": {"type": "string", "description": "Room number"},
                "items_dict": {"type": "object", "description": "Item names and quantities"}
            },
            "required": ["room_number", "items_dict"]
        }
    )
]

room_service_tools = [
    FunctionDeclaration(
        name="create_room_service_request",
        description="Create room service request",
        parameters={
            "type": "object",
            "properties": {
                "room_number": {"type": "string", "description": "Room number"},
                "request_type": {"type": "string", "description": "cleaning, towel, amenity, repair"},
                "details": {"type": "string", "description": "Additional details"}
            },
            "required": ["room_number", "request_type"]
        }
    )
]

# --- ResortAgent Class ---
class ResortAgent:
    def __init__(self, system_prompt: str, tools: List[FunctionDeclaration], agent_type: str, session_id: str = "default"):
        self.system_prompt = system_prompt
        self.agent_type = agent_type
        self.session_id = session_id
        self.tools = tools
        
        if GEMINI_AVAILABLE:
            try:
                self.model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash',
                    tools=tools,
                    system_instruction=system_prompt
                )
                self.chat_session = self.model.start_chat(enable_automatic_function_calling=False)  # Changed to False
                logger.info(f"✅ {agent_type} agent created")
            except:
                self.model = None
                self.chat_session = None
        else:
            self.model = None
            self.chat_session = None
    
    def _load_tools(self):
        """Load tool functions"""
        try:
            from .tools import (
                check_room_availability,
                get_facility_info,
                get_menu_items,
                place_restaurant_order,
                create_room_service_request
            )
            
            return {
                "check_room_availability": check_room_availability,
                "get_facility_info": get_facility_info,
                "get_menu_items": get_menu_items,
                "place_restaurant_order": place_restaurant_order,
                "create_room_service_request": create_room_service_request
            }
        except ImportError:
            return {}
    
    def _execute_tool(self, func_name: str, args: Dict) -> str:
        """Execute a tool function"""
        try:
            tools = self._load_tools()
            if func_name not in tools:
                return f"Tool '{func_name}' not available"
            
            func = tools[func_name]
            
            if func_name == "get_menu_items":
                compact = args.get("compact", False)
                return func(compact=compact)
            elif func_name == "check_room_availability":
                room_type = args.get("room_type")
                return func(room_type=room_type) if room_type else func()
            elif func_name == "get_facility_info":
                return func(args.get("facility_name", ""))
            elif func_name == "place_restaurant_order":
                return func(room_number=args.get("room_number", ""), items_dict=args.get("items_dict", {}))
            elif func_name == "create_room_service_request":
                return func(
                    room_number=args.get("room_number", ""),
                    request_type=args.get("request_type", ""),
                    details=args.get("details", "")
                )
        except Exception as e:
            return f"Error: {str(e)[:100]}"
    
    def process_message(self, history: List[Dict[str, str]]) -> str:
        """Process message with manual function calling"""
        try:
            # Get user message
            user_message = ""
            for msg in reversed(history):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if not user_message:
                return "How can I help you?"
            
            # Extract room number
            room_match = re.search(r'room\s*(\d+)', user_message.lower())
            if room_match:
                memory.update_context(self.session_id, {"room_number": room_match.group(1)})
            
            # Store user message
            memory.add_message(self.session_id, "user", user_message)
            
            if not GEMINI_AVAILABLE or not self.chat_session:
                return self._get_mock_response(user_message)
            
            # Send to Gemini
            response = self.chat_session.send_message(user_message)
            response_text = ""
            
            # Check for function calls and execute them manually
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
                    elif hasattr(part, 'function_call'):
                        # EXECUTE THE FUNCTION (FIXED)
                        func_name = part.function_call.name
                        args = dict(part.function_call.args)
                        
                        logger.info(f"🔧 Executing: {func_name} with {args}")
                        tool_result = self._execute_tool(func_name, args)
                        
                        # Send result back to Gemini
                        self.chat_session.send_message(str(tool_result))
                        response_text += f"\n{tool_result}"
            
            if not response_text.strip():
                response_text = self._get_mock_response(user_message)
            
            # Store response
            memory.add_message(self.session_id, "assistant", response_text)
            return response_text
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._get_mock_response(user_message) if 'user_message' in locals() else "I encountered an error"
    
    def _get_mock_response(self, user_message: str) -> str:
        """Mock response when Gemini unavailable"""
        user_lower = user_message.lower()
        
        if self.agent_type == "Restaurant":
            if "menu" in user_lower:
                try:
                    tools = self._load_tools()
                    return tools["get_menu_items"](compact=False)
                except:
                    return "🍽️ Restaurant menu: Puri Bhaji (₹140), Masala Dosa (₹120), Soft Drink (₹50)"
            elif any(word in user_lower for word in ["order", "want", "get"]):
                return "I can take your order. Please specify items and room number."
        
        elif self.agent_type == "RoomService":
            if any(word in user_lower for word in ["clean", "towel", "service"]):
                return "I can help with room service. Please provide your room number and request details."
        
        else:  # Receptionist
            if "check" in user_lower and "in" in user_lower:
                return "Check-in: 2:00 PM, Check-out: 11:00 AM"
            elif "room" in user_lower and "available" in user_lower:
                return "Rooms available: Deluxe (₹250), Standard (₹150)"
        
        return "How can I help you?"

# System Prompts
RECEPTIONIST_PROMPT = """You are a resort receptionist. Answer questions about rooms, facilities, check-in/out.
Use tools for accurate information."""

RESTAURANT_PROMPT = """You are a restaurant assistant. Handle menu requests and food orders.
For ordering: Ask for room number, confirm items, then place order.
Use tools when needed."""

ROOM_SERVICE_PROMPT = """You handle room service requests. Ask for room number and request type.
Use tool to create service requests."""

# --- Agent Manager ---
class AgentManager:
    def __init__(self):
        self.conversation_states = {}
        self.agent_cache = {}
    
    def get_agent(self, agent_type: str, session_id: str = "default"):
        cache_key = f"{session_id}_{agent_type}"
        if cache_key in self.agent_cache:
            return self.agent_cache[cache_key]
        
        if agent_type == "Restaurant":
            tools = restaurant_tools
            prompt = RESTAURANT_PROMPT
        elif agent_type == "RoomService":
            tools = room_service_tools
            prompt = ROOM_SERVICE_PROMPT
        else:
            tools = receptionist_tools
            prompt = RECEPTIONIST_PROMPT
        
        agent = ResortAgent(prompt, tools, agent_type, session_id)
        self.agent_cache[cache_key] = agent
        return agent
    
    def route_request(self, text: str, session_id: str = "default") -> str:
        if not text:
            return "Receptionist"
        
        text_lower = text.lower()
        
        # Check current state
        current_state = self.conversation_states.get(session_id)
        if current_state == "Restaurant" and any(word in text_lower for word in ["menu", "order", "food", "eat", "want", "get"]):
            return "Restaurant"
        if current_state == "RoomService" and any(word in text_lower for word in ["clean", "towel", "service"]):
            return "RoomService"
        
        # Restaurant keywords (expanded)
        restaurant_words = ["menu", "food", "order", "restaurant", "eat", "hungry", 
                          "pizza", "burger", "dosa", "rice", "curry", "meal",
                          "puri", "bhaji", "drink", "soft", "plate", "serving",
                          "want", "need", "would like", "thirsty"]
        
        # Room service keywords
        service_words = ["clean", "towel", "service", "request", "amenity", 
                        "laundry", "housekeeping", "maintenance", "repair"]
        
        if any(word in text_lower for word in restaurant_words):
            self.conversation_states[session_id] = "Restaurant"
            return "Restaurant"
        
        if any(word in text_lower for word in service_words):
            self.conversation_states[session_id] = "RoomService"
            return "RoomService"
        
        self.conversation_states[session_id] = "Receptionist"
        return "Receptionist"
    
    def chat(self, history: List[Dict[str, str]], session_id: str = "default") -> str:
        if not history:
            welcome = "Welcome to Eco Resort! How can I help?"
            memory.add_message(session_id, "assistant", welcome)
            return welcome
        
        # Get user message
        user_text = ""
        for msg in reversed(history):
            if msg.get("role") == "user":
                user_text = msg.get("content", "")
                break
        
        # Store user message
        memory.add_message(session_id, "user", user_text)
        
        # Route to agent
        agent_type = self.route_request(user_text, session_id)
        logger.info(f"Routing to: {agent_type}")
        
        # Get agent and process
        agent = self.get_agent(agent_type, session_id)
        response = agent.process_message(history)
        
        return response

# Global instance
manager = AgentManager()