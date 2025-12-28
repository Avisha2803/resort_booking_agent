from backend.database import engine, SessionLocal, Base
from backend.models import MenuItem
import sys

def create_tables():
    """Create all database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def get_complete_menu_data():
    """Return complete menu data (merged from both files)"""
    return [
        # BREAKFAST
        {"name": "Masala Dosa", "description": "Crispy dosa with spiced potato filling", "price": 120, "category": "Breakfast"},
        {"name": "Plain Idli", "description": "Steamed rice cakes with chutney", "price": 80, "category": "Breakfast"},
        {"name": "Medu Vada", "description": "Fried lentil doughnuts", "price": 90, "category": "Breakfast"},
        {"name": "Upma", "description": "Semolina cooked with vegetables", "price": 100, "category": "Breakfast"},
        {"name": "Poha", "description": "Flattened rice with peanuts", "price": 100, "category": "Breakfast"},
        {"name": "Aloo Paratha", "description": "Stuffed paratha with curd", "price": 130, "category": "Breakfast"},
        {"name": "Paneer Paratha", "description": "Paneer stuffed paratha", "price": 150, "category": "Breakfast"},
        {"name": "Puri Bhaji", "description": "Fried bread with potato curry", "price": 140, "category": "Breakfast"},
        {"name": "Omelette", "description": "Indian-style omelette", "price": 90, "category": "Breakfast"},
        {"name": "Boiled Eggs", "description": "Two boiled eggs", "price": 70, "category": "Breakfast"},
        
        # VEG STARTERS
        {"name": "Paneer Tikka", "description": "Grilled cottage cheese with spices", "price": 240, "category": "Veg Starter"},
        {"name": "Veg Manchurian", "description": "Vegetable balls in spicy sauce", "price": 200, "category": "Veg Starter"},
        {"name": "Crispy Corn", "description": "Fried corn kernels with pepper", "price": 180, "category": "Veg Starter"},
        {"name": "Spring Roll", "description": "Crispy vegetable rolls", "price": 160, "category": "Veg Starter"},
        {"name": "Hara Bhara Kabab", "description": "Spinach and potato patties", "price": 220, "category": "Veg Starter"},
        
        # NON-VEG STARTERS
        {"name": "Chicken Tikka", "description": "Tandoori grilled chicken chunks", "price": 320, "category": "Non-Veg Starter"},
        {"name": "Chilli Chicken", "description": "Spicy fried chicken with bell peppers", "price": 300, "category": "Non-Veg Starter"},
        {"name": "Fish Fry", "description": "Crispy fried fish fillet", "price": 350, "category": "Non-Veg Starter"},
        {"name": "Mutton Seekh Kabab", "description": "Minced mutton skewers", "price": 380, "category": "Non-Veg Starter"},
        {"name": "Chicken Lollipop", "description": "Crispy chicken wings", "price": 340, "category": "Non-Veg Starter"},
        
        # VEG MAIN COURSE
        {"name": "Paneer Butter Masala", "description": "Cottage cheese in rich tomato gravy", "price": 300, "category": "Veg Main Course"},
        {"name": "Dal Makhani", "description": "Creamy black lentils slow cooked", "price": 250, "category": "Veg Main Course"},
        {"name": "Veg Biryani", "description": "Aromatic rice with mixed vegetables", "price": 280, "category": "Veg Main Course"},
        {"name": "Palak Paneer", "description": "Paneer in spinach gravy", "price": 290, "category": "Veg Main Course"},
        {"name": "Chana Masala", "description": "Chickpeas in spicy gravy", "price": 220, "category": "Veg Main Course"},
        {"name": "Malai Kofta", "description": "Cottage cheese balls in creamy sauce", "price": 320, "category": "Veg Main Course"},
        {"name": "Veg Korma", "description": "Mixed vegetables in cashew gravy", "price": 270, "category": "Veg Main Course"},
        
        # NON-VEG MAIN COURSE
        {"name": "Butter Chicken", "description": "Chicken in creamy tomato sauce", "price": 380, "category": "Non-Veg Main Course"},
        {"name": "Mutton Rogan Josh", "description": "Kashmiri style mutton curry", "price": 450, "category": "Non-Veg Main Course"},
        {"name": "Chicken Biryani", "description": "Fragrant rice layered with spiced chicken", "price": 350, "category": "Non-Veg Main Course"},
        {"name": "Fish Curry", "description": "Fish cooked in spicy coconut gravy", "price": 340, "category": "Non-Veg Main Course"},
        {"name": "Chicken Curry", "description": "Traditional chicken curry", "price": 320, "category": "Non-Veg Main Course"},
        {"name": "Mutton Biryani", "description": "Aromatic rice with tender mutton", "price": 420, "category": "Non-Veg Main Course"},
        {"name": "Prawn Masala", "description": "Prawns in spicy masala gravy", "price": 390, "category": "Non-Veg Main Course"},
        
        # BREADS
        {"name": "Tandoori Roti", "description": "Whole wheat flatbread cooked in clay oven", "price": 40, "category": "Breads"},
        {"name": "Butter Naan", "description": "Soft leavened bread topped with butter", "price": 60, "category": "Breads"},
        {"name": "Garlic Naan", "description": "Naan infused with fresh garlic", "price": 70, "category": "Breads"},
        {"name": "Cheese Kulcha", "description": "Stuffed bread with cheese filling", "price": 90, "category": "Breads"},
        {"name": "Lachha Paratha", "description": "Layered whole wheat bread", "price": 65, "category": "Breads"},
        {"name": "Roomali Roti", "description": "Thin handkerchief bread", "price": 50, "category": "Breads"},
        {"name": "Missi Roti", "description": "Gram flour bread with spices", "price": 55, "category": "Breads"},
        
        # DESSERTS
        {"name": "Gulab Jamun", "description": "Fried milk dumplings in sugar syrup", "price": 120, "category": "Desserts"},
        {"name": "Rasmalai", "description": "Soft paneer patties in sweetened milk", "price": 150, "category": "Desserts"},
        {"name": "Vanilla Ice Cream", "description": "Classic vanilla scoop", "price": 100, "category": "Desserts"},
        {"name": "Chocolate Brownie", "description": "Warm brownie with chocolate sauce", "price": 180, "category": "Desserts"},
        {"name": "Rasgulla", "description": "Spongy cottage cheese balls in syrup", "price": 110, "category": "Desserts"},
        {"name": "Kheer", "description": "Rice pudding with nuts", "price": 130, "category": "Desserts"},
        {"name": "Mango Ice Cream", "description": "Seasonal mango flavor", "price": 120, "category": "Desserts"},
        
        # DRINKS
        {"name": "Mineral Water", "description": "1L bottled water", "price": 30, "category": "Drinks"},
        {"name": "Fresh Lime Soda", "description": "Refreshing lime drink (Sweet/Salted)", "price": 80, "category": "Drinks"},
        {"name": "Sweet Lassi", "description": "Traditional yogurt drink", "price": 90, "category": "Drinks"},
        {"name": "Masala Chai", "description": "Indian spiced tea", "price": 40, "category": "Drinks"},
        {"name": "Cold Coffee", "description": "Chilled coffee with vanilla ice cream", "price": 120, "category": "Drinks"},
        {"name": "Soft Drink", "description": "Coke/Sprite/Fanta (300ml)", "price": 50, "category": "Drinks"},
        {"name": "Fresh Juice", "description": "Orange/Mosambi/Watermelon", "price": 100, "category": "Drinks"},
        {"name": "Buttermilk", "description": "Spiced buttermilk", "price": 60, "category": "Drinks"},
        
        # MISCELLANEOUS
        {"name": "Green Salad", "description": "Sliced cucumber, tomato, carrot, onion", "price": 80, "category": "Miscellaneous"},
        {"name": "Masala Papad", "description": "Roasted papad topped with spicy salad", "price": 50, "category": "Miscellaneous"},
        {"name": "Boondi Raita", "description": "Yogurt with fried gram flour pearls", "price": 90, "category": "Miscellaneous"},
        {"name": "Plain Curd", "description": "Fresh plain yogurt", "price": 60, "category": "Miscellaneous"},
        {"name": "Pickle", "description": "Assorted Indian pickle", "price": 20, "category": "Miscellaneous"},
        {"name": "Chutney", "description": "Coconut/Mint/Tomato chutney", "price": 30, "category": "Miscellaneous"},
        {"name": "Papad", "description": "Plain roasted papad", "price": 40, "category": "Miscellaneous"},
    ]

def seed_menu(clear_existing=False):
    """
    Seed complete menu data into database
    Args:
        clear_existing: If True, clear all existing menu items first
    """
    db = SessionLocal()
    
    if clear_existing:
        print("🗑️  Clearing existing menu items...")
        deleted_count = db.query(MenuItem).delete()
        print(f"   Removed {deleted_count} existing items")
    
    menu_data = get_complete_menu_data()
    
    print(f"📥 Adding {len(menu_data)} menu items...")
    print("=" * 50)
    
    added_count = 0
    skipped_count = 0
    
    for item in menu_data:
        # Check if item already exists (unless we cleared them)
        if not clear_existing:
            exists = db.query(MenuItem).filter(MenuItem.name == item["name"]).first()
            if exists:
                skipped_count += 1
                print(f"⏭️  Skipped: {item['name']} (already exists)")
                continue
        
        db_item = MenuItem(**item)
        db.add(db_item)
        added_count += 1
        print(f"✅ Added: {item['name']} (₹{item['price']})")
    
    db.commit()
    
    print("=" * 50)
    print(f"\n📊 SEEDING SUMMARY")
    print(f"   Total items in menu: {len(menu_data)}")
    print(f"   Newly added: {added_count}")
    print(f"   Skipped (already existed): {skipped_count}")
    
    # Show category-wise count
    categories = {}
    for item in menu_data:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📈 CATEGORY BREAKDOWN:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count} items")
    
    db.close()
    print(f"\n✅ Menu database updated successfully!")

def setup_full_database():
    """Complete database setup: create tables + seed data"""
    print("🔧 Setting up complete database...")
    print("=" * 50)
    
    # Step 1: Create tables
    create_tables()
    
    # Step 2: Seed menu data (clear existing)
    seed_menu(clear_existing=True)
    
    print("=" * 50)
    print("🎉 Database setup completed successfully!")

def add_items_only():
    """Add menu items only (no table creation, no clearing)"""
    print("📥 Adding menu items (incremental update)...")
    print("=" * 50)
    seed_menu(clear_existing=False)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏨 RESORT MENU DATABASE MANAGEMENT")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup" or command == "seed":
            # Full setup: create tables + seed data (clear existing)
            setup_full_database()
            
        elif command == "add" or command == "update":
            # Add items only (incremental, no clear)
            add_items_only()
            
        elif command == "tables":
            # Create tables only
            create_tables()
            
        elif command == "help":
            print("\n📖 USAGE:")
            print("  python add_menu_items.py setup    → Create tables + seed data (clears existing)")
            print("  python add_menu_items.py add      → Add items only (no clear, no table creation)")
            print("  python add_menu_items.py tables   → Create tables only")
            print("  python add_menu_items.py          → Interactive mode (default)")
            
        else:
            print(f"❌ Unknown command: {command}")
            print("   Use: setup, add, tables, or help")
            
    else:
        # Interactive mode
        print("\n🔍 What would you like to do?")
        print("   1. Complete setup (create tables + seed all data)")
        print("   2. Add menu items only (incremental update)")
        print("   3. Create tables only")
        print("   4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            setup_full_database()
        elif choice == "2":
            add_items_only()
        elif choice == "3":
            create_tables()
        elif choice == "4":
            print("👋 Exiting...")
        else:
            print("❌ Invalid choice. Please run the script again.")