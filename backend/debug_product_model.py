import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Attempting to import Product model...")
    from app.models.product import Product
    print("Successfully imported Product model!")
    
    print("Checking relationship...")
    print(Product.components)
    print("Successfully checked relationship!")
    
except Exception as e:
    print(f"Error importing Product: {e}")
    import traceback
    traceback.print_exc()
