from backend.tools import get_menu_items

try:
    print("calling get_menu_items()...")
    menu = get_menu_items()
    print("--- RESULT ---")
    print(menu)
    print("--- END RESULT ---")
except Exception as e:
    print(f"ERROR: {e}")
