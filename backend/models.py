from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, index=True)
    items = Column(JSON)
    total_amount = Column(Float)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, index=True)
    request_type = Column(String)
    details = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)